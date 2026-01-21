"""Advanced Analytics and AI-Powered Predictions"""
from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Tuple
import os
import json
import uuid
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
from datetime import date

ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")
# Optional local overrides (do not commit secrets)
load_dotenv(ROOT_DIR / ".env.local", override=True)

from utils.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])

# Database will be injected
db = None

def init_db(database):
    global db
    db = database

SYSTEM_PROMPT = """You are an expert education data analyst for the Maharashtra Education Department.
        Analyze school metrics data and provide actionable insights, predictions, and recommendations.
        Be specific with numbers, percentages, and block names when available.
        Format responses with clear sections using markdown headers.
        Focus on practical, implementable recommendations."""

@router.get("/ai/status")
async def ai_status(current_user: dict = Depends(get_current_user)):
    """Return whether insights generation is enabled (without exposing secrets)."""
    return {
        "provider": os.environ.get("INSIGHTS_PROVIDER", "local"),
        # local mode is always enabled; openai mode depends on key
        "enabled": os.environ.get("INSIGHTS_PROVIDER", "local") != "openai"
        or bool(os.environ.get("OPENAI_API_KEY")),
        "model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
    }

def _format_ai_exception(e: Exception) -> str:
    msg = str(e)
    return f"AI analysis unavailable: {msg}"


def _safe_div(num: float, den: float) -> float:
    return float(num) / float(den) if den else 0.0


def _percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    return float(np.percentile(np.array(values, dtype=float), p))


def _z_scores(values: List[float]) -> List[float]:
    if not values:
        return []
    arr = np.array(values, dtype=float)
    std = float(arr.std()) if len(arr) > 1 else 0.0
    if std == 0.0:
        return [0.0 for _ in values]
    mean = float(arr.mean())
    return [float((x - mean) / std) for x in arr.tolist()]


def _top(items: List[Dict[str, Any]], key: str, n: int = 5) -> List[Dict[str, Any]]:
    return sorted(items, key=lambda x: float(x.get(key, 0) or 0), reverse=True)[:n]


def _bottom(items: List[Dict[str, Any]], key: str, n: int = 5) -> List[Dict[str, Any]]:
    return sorted(items, key=lambda x: float(x.get(key, 0) or 0))[:n]


def _local_dropout_insights(risk_data: List[Dict[str, Any]]) -> str:
    if not risk_data:
        return "No data available to generate insights."

    avg_dropout = round(sum(r["dropout_rate"] for r in risk_data) / max(len(risk_data), 1), 2)
    high = [r for r in risk_data if r.get("risk_level") == "High"]
    top5 = _top(risk_data, "risk_score", 5)

    # ML-style: z-score outliers on risk_score
    z = _z_scores([float(r.get("risk_score", 0) or 0) for r in risk_data])
    outliers = [
        {**risk_data[i], "z": round(z[i], 2)}
        for i in range(len(risk_data))
        if z[i] >= 1.5
    ][:5]

    lines = []
    lines.append("## Key Findings")
    lines.append(f"- Total blocks analyzed: **{len(risk_data)}**")
    lines.append(f"- Average dropout rate: **{avg_dropout}%**")
    lines.append(f"- High-risk blocks: **{len(high)}**")
    if top5:
        lines.append(f"- Highest risk block: **{top5[0]['block']}** (risk score **{top5[0]['risk_score']}**, dropout rate **{top5[0]['dropout_rate']}%**)")

    lines.append("\n## High Risk Blocks (Top 5)")
    for r in top5:
        lines.append(
            f"- **{r['block']}**: dropout **{r['dropout_count']}**, migration **{r['migration_count']}**, "
            f"dropout rate **{r['dropout_rate']}%**, risk score **{r['risk_score']}**"
        )

    lines.append("\n## Root Cause Signals (data-driven)")
    lines.append("- **High migration share** often indicates seasonal movement or documentation issues; prioritize verification + tracking.")
    lines.append("- **High dropout with low migration** suggests retention/attendance challenges; prioritize counselling + attendance monitoring.")
    if outliers:
        lines.append("- **Statistical outliers** (z-score ≥ 1.5) indicate blocks disproportionately driving district risk:")
        for o in outliers:
            lines.append(f"  - **{o['block']}** (risk score {o['risk_score']}, z={o['z']})")

    lines.append("\n## Recommendations (no LLM)")
    lines.append("- **Targeted outreach** in top-risk blocks: identify at-risk students weekly and follow up with parents.")
    lines.append("- **Migration workflow**: create a standard checklist for transfer/migration cases to reduce misclassification.")
    lines.append("- **Attendance early-warning**: flag students with repeated absences and intervene within 7 days.")
    lines.append("- **Block-level review**: monthly review of dropout/migration counts with headmasters and cluster officers.")

    lines.append("\n## Priority Action Items (next 30 days)")
    lines.append("- **Week 1**: publish top-10 at-risk schools per high-risk block; assign case owners.")
    lines.append("- **Week 2**: run parent counselling drives in top 2 blocks; track attendance improvements weekly.")
    lines.append("- **Week 3–4**: audit migration entries for top 2 blocks; correct data + update SOP.")

    return "\n".join(lines)


def _local_infra_insights(forecast_data: List[Dict[str, Any]]) -> str:
    if not forecast_data:
        return "No data available to generate insights."

    total_classrooms = sum(int(f.get("total_classrooms", 0) or 0) for f in forecast_data)
    repair_needed = sum(int(f.get("current_repair_needed", 0) or 0) for f in forecast_data)
    dilapidated = sum(int(f.get("dilapidated", 0) or 0) for f in forecast_data)
    repair_rate = round(_safe_div(repair_needed, total_classrooms) * 100, 2) if total_classrooms else 0.0

    # Priority ranking: use estimated budget + dilapidated + repair
    scored = []
    for f in forecast_data:
        tc = int(f.get("total_classrooms", 0) or 0)
        rn = int(f.get("current_repair_needed", 0) or 0)
        dil = int(f.get("dilapidated", 0) or 0)
        budget = float(f.get("estimated_budget_lakhs", 0) or 0)
        score = (10 * _safe_div(rn, max(tc, 1))) + (20 * _safe_div(dil, max(tc, 1))) + (0.02 * budget)
        scored.append({**f, "_score": round(score, 3)})
    top5 = _top(scored, "_score", 5)

    lines = []
    lines.append("## Infrastructure Health Summary")
    lines.append(f"- Total classrooms: **{total_classrooms:,}**")
    lines.append(f"- Current repair needed: **{repair_needed:,}** (**{repair_rate}%** of classrooms)")
    lines.append(f"- Dilapidated classrooms: **{dilapidated:,}**")

    lines.append("\n## Critical Blocks (Top 5)")
    for f in top5:
        lines.append(
            f"- **{f['block']}**: repair needed **{f['current_repair_needed']}** / **{f['total_classrooms']}**, "
            f"dilapidated **{f['dilapidated']}**, est. budget **₹{round(float(f.get('estimated_budget_lakhs',0) or 0),1)}L**"
        )

    lines.append("\n## Budget Allocation (data-driven)")
    lines.append("- Prioritize blocks with **high dilapidated share** first (safety risk), then high repair share (preventive maintenance).")
    lines.append("- Split budget into **60% safety-critical repairs**, **30% preventive repairs**, **10% contingency**.")

    lines.append("\n## Maintenance Schedule")
    lines.append("- **0–3 months**: address dilapidated classrooms + major repairs in top 2 blocks.")
    lines.append("- **3–6 months**: complete minor repairs across remaining high-score blocks.")
    lines.append("- **Quarterly**: re-run condition survey and update forecast.")

    lines.append("\n## Long-term Planning (3-year)")
    lines.append("- Create an annual **block-wise capex plan** and track condition improvements as a KPI.")
    lines.append("- Standardize procurement + contractor empanelment to reduce repair cycle time.")
    return "\n".join(lines)


def _local_teacher_insights(shortage_data: List[Dict[str, Any]], age_distribution: Dict[str, int]) -> str:
    if not shortage_data:
        return "No data available to generate insights."

    total_teachers = sum(int(s.get("total_teachers", 0) or 0) for s in shortage_data)
    retiring_5 = sum(int(s.get("retiring_in_5_years", 0) or 0) for s in shortage_data)
    avg_ctet = round(sum(float(s.get("ctet_rate", 0) or 0) for s in shortage_data) / max(len(shortage_data), 1), 1)
    high_risk = [s for s in shortage_data if s.get("risk_level") == "High"]
    top5 = _top(shortage_data, "retirement_risk_pct", 5)

    lines = []
    lines.append("## Workforce Health Analysis")
    lines.append(f"- Total teachers analyzed: **{total_teachers:,}**")
    lines.append(f"- Retiring in 5 years: **{retiring_5:,}** (**{round(_safe_div(retiring_5, total_teachers)*100,1)}%**)")
    lines.append(f"- Average CTET qualification rate: **{avg_ctet}%**")
    lines.append(f"- High retirement-risk blocks: **{len(high_risk)}**")

    lines.append("\n## Retirement Wave Impact (Top 5 blocks)")
    for s in top5:
        lines.append(
            f"- **{s['block']}**: retiring(5y) **{s['retiring_in_5_years']}** / **{s['total_teachers']}** "
            f"({s['retirement_risk_pct']}%), CTET **{s['ctet_rate']}%**, net shortage(5y) **{s['forecast_shortage_5yr']}**"
        )

    lines.append("\n## Hiring & Deployment Requirements (data-driven)")
    lines.append("- Prioritize recruitment/transfer into blocks with **high retirement risk** and **negative 5-year net**.")
    lines.append("- Maintain a buffer pool for **mid-year vacancies** in blocks with high 3-year retirement counts.")

    lines.append("\n## Training Priorities (CTET / capacity)")
    lines.append("- Focus CTET training in blocks with **CTET rate below district median**.")
    lines.append("- Pair senior teachers (55+) with new entrants for **handover of key roles** before retirement.")

    lines.append("\n## Succession Planning (5-year)")
    lines.append("- Create a **block-wise replacement plan** (retirements minus new entrants) updated quarterly.")
    lines.append("- Track KPIs: CTET rate, vacancy fill time, teacher-to-student ratio (PTR) where available.")

    lines.append("\n## Age Distribution Snapshot")
    lines.append(f"- {json.dumps(age_distribution, indent=2)}")
    return "\n".join(lines)


def _parse_ddmmyyyy(s: Any) -> Optional[date]:
    if not s or not isinstance(s, str):
        return None
    try:
        parts = s.strip().split("/")
        if len(parts) != 3:
            return None
        dd, mm, yyyy = int(parts[0]), int(parts[1]), int(parts[2])
        return date(yyyy, mm, dd)
    except Exception:
        return None


def _age_from_dob(dob: Any) -> Optional[int]:
    d = _parse_ddmmyyyy(dob)
    if not d:
        return None
    today = date.today()
    years = today.year - d.year - ((today.month, today.day) < (d.month, d.day))
    if years < 0 or years > 120:
        return None
    return years


def _local_completion_insights(block_data: List[Dict[str, Any]], overall_rate: float) -> str:
    if not block_data:
        return "No data available to generate insights."

    bottom5 = _bottom(block_data, "rate", 5)
    top5 = _top(block_data, "rate", 5)
    max_weeks = max(int(b.get("estimated_weeks", 0) or 0) for b in block_data)

    lines = []
    lines.append("## Completion Status Summary")
    lines.append(f"- Overall generation rate: **{overall_rate}%**")
    lines.append(f"- Estimated worst-case timeline (based on 2% weekly assumption): **{max_weeks} weeks**")

    lines.append("\n## Bottleneck Blocks (lowest completion)")
    for b in bottom5:
        lines.append(
            f"- **{b['block']}**: rate **{b['rate']}%**, pending **{b['pending']:,}**, est. **{b['estimated_weeks']} weeks**"
        )

    lines.append("\n## Top Performing Blocks (highest completion)")
    for b in top5:
        lines.append(f"- **{b['block']}**: rate **{b['rate']}%** (pending **{b['pending']:,}**)")

    lines.append("\n## Acceleration Strategy (process + data)")
    lines.append("- Run weekly **exception lists** (schools with low rate) and assign accountability at cluster level.")
    lines.append("- Improve throughput by batching: schedule **fixed weekly camps** per low-performing block.")
    lines.append("- Resolve blockers: Aadhaar/identity mismatches, missing consent, or data entry gaps.")

    lines.append("\n## Risk Factors")
    lines.append("- Low internet/device availability at schools; plan mobile/offline capture where needed.")
    lines.append("- Data quality issues causing rejections; add validation checks before submission.")
    return "\n".join(lines)


def _local_executive_summary(metrics: Dict[str, Any]) -> str:
    if not metrics:
        return "No data available to generate executive summary."

    strengths = []
    concerns = []
    # simple thresholds; adjust as needed per district baselines
    if float(metrics.get("classroom_health", 0) or 0) >= 85:
        strengths.append(f"Classroom health is strong (**{metrics.get('classroom_health')}%**).")
    else:
        concerns.append(f"Classroom health needs improvement (**{metrics.get('classroom_health')}%**).")

    if float(metrics.get("toilet_functional", 0) or 0) >= 90:
        strengths.append(f"Toilet functionality is high (**{metrics.get('toilet_functional')}%**).")
    else:
        concerns.append(f"Toilet functionality is below target (**{metrics.get('toilet_functional')}%**).")

    if float(metrics.get("apaar_rate", 0) or 0) >= 80:
        strengths.append(f"APAAR generation is progressing (**{metrics.get('apaar_rate')}%**).")
    else:
        concerns.append(f"APAAR generation is lagging (**{metrics.get('apaar_rate')}%**).")

    if float(metrics.get("dropout_rate", 0) or 0) <= 2.0:
        strengths.append(f"Dropout rate is low (**{metrics.get('dropout_rate')}%**).")
    else:
        concerns.append(f"Dropout rate is elevated (**{metrics.get('dropout_rate')}%**).")

    lines = []
    lines.append("## Executive Summary")
    lines.append(
        f"Pune District dashboard overview across **{metrics.get('schools', 0)}** schools and "
        f"**{metrics.get('students', 0):,}** students. Key infrastructure and identity metrics are summarized below."
    )

    lines.append("\n## Strengths")
    if strengths:
        for s in strengths[:3]:
            lines.append(f"- {s}")
    else:
        lines.append("- No clear strengths identified from available thresholds.")

    lines.append("\n## Areas of Concern")
    if concerns:
        for c in concerns[:3]:
            lines.append(f"- {c}")
    else:
        lines.append("- No major concerns flagged from available thresholds.")

    lines.append("\n## Key Recommendations (next quarter)")
    lines.append("- Focus on the bottom-performing blocks/schools for each KPI with weekly review cadence.")
    lines.append("- Allocate maintenance funds based on safety-critical needs first (dilapidated), then preventive repairs.")
    lines.append("- Strengthen identity/document workflows to improve APAAR throughput and reduce rework.")
    lines.append("- Implement early-warning retention tracking (attendance + migration) for dropout prevention.")
    lines.append("- Track KPIs weekly: APAAR rate, dropout/migration counts, classroom/toilet functionality.")

    lines.append("\n## Success Metrics (KPIs)")
    lines.append("- +5–10pp improvement in APAAR rate in bottom 5 blocks within 8 weeks")
    lines.append("- Reduction in dropout/migration counts in top 2 risk blocks month-over-month")
    lines.append("- >95% toilet functionality and improving classroom condition trend")
    return "\n".join(lines)


def _insights_provider() -> str:
    """
    Insights generation mode:
    - local (default): deterministic insights using real data + stats/ML-style scoring
    - openai: optional LLM; not used unless explicitly enabled
    """
    return os.environ.get("INSIGHTS_PROVIDER", "local").lower().strip() or "local"


async def _generate_insights(kind: str, payload: Dict[str, Any]) -> str:
    provider = _insights_provider()
    if provider != "openai":
        if kind == "dropout-risk":
            return _local_dropout_insights(payload.get("risk_data", []))
        if kind == "infrastructure-forecast":
            return _local_infra_insights(payload.get("forecast_data", []))
        if kind == "teacher-shortage":
            return _local_teacher_insights(payload.get("shortage_data", []), payload.get("age_distribution", {}))
        if kind == "data-completion":
            return _local_completion_insights(payload.get("block_data", []), float(payload.get("overall_rate", 0) or 0))
        if kind == "executive-summary":
            return _local_executive_summary(payload.get("metrics", {}))
        return "Insights unavailable for this analysis type."

    # Optional: keep openai as a future provider without forcing it for this project.
    raise HTTPException(status_code=501, detail="INSIGHTS_PROVIDER=openai is not enabled in this build.")


@router.get("/predictions/dropout-risk")
async def get_dropout_risk_predictions(current_user: dict = Depends(get_current_user)):
    """AI-powered dropout risk analysis"""
    
    # Gather data for analysis
    dropbox_data = await db.dropbox_analytics.find({}, {"_id": 0}).to_list(100)
    enrolment_data = await db.enrolment_analytics.find({}, {"_id": 0}).to_list(100)
    
    # Calculate dropout metrics by block
    block_metrics = {}
    for d in dropbox_data:
        block = d.get("block_name", "Unknown")
        if block not in block_metrics:
            block_metrics[block] = {"dropout": 0, "total_remarks": 0, "migration": 0}
        block_metrics[block]["dropout"] += d.get("dropout", 0)
        block_metrics[block]["total_remarks"] += d.get("total_remarks", 0)
        block_metrics[block]["migration"] += d.get("migration", 0)
    
    # Calculate risk scores
    risk_data = []
    for block, metrics in block_metrics.items():
        dropout_rate = metrics["dropout"] / max(metrics["total_remarks"], 1) * 100
        risk_score = min(100, dropout_rate * 2 + (metrics["migration"] / max(metrics["total_remarks"], 1) * 50))
        risk_data.append({
            "block": block,
            "dropout_count": metrics["dropout"],
            "dropout_rate": round(dropout_rate, 2),
            "migration_count": metrics["migration"],
            "risk_score": round(risk_score, 1),
            "risk_level": "High" if risk_score > 60 else "Medium" if risk_score > 30 else "Low"
        })
    
    risk_data.sort(key=lambda x: x["risk_score"], reverse=True)
    
    # Get AI insights
    try:
        ai_insights = await _generate_insights("dropout-risk", {"risk_data": risk_data})
    except Exception as e:
        ai_insights = _format_ai_exception(e)
    
    return {
        "summary": {
            "total_blocks": len(risk_data),
            "high_risk_count": len([r for r in risk_data if r["risk_level"] == "High"]),
            "medium_risk_count": len([r for r in risk_data if r["risk_level"] == "Medium"]),
            "low_risk_count": len([r for r in risk_data if r["risk_level"] == "Low"]),
            "avg_dropout_rate": round(sum(r["dropout_rate"] for r in risk_data) / max(len(risk_data), 1), 2)
        },
        "block_risk_data": risk_data,
        "ai_insights": ai_insights,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


@router.get("/predictions/infrastructure-forecast")
async def get_infrastructure_forecast(current_user: dict = Depends(get_current_user)):
    """Infrastructure gap analysis and forecast"""
    
    # Gather infrastructure data
    ct_data = await db.classrooms_toilets.find({}, {"_id": 0}).to_list(1000)
    
    # Aggregate by block
    block_infra = {}
    for school in ct_data:
        block = school.get("block_name", "Unknown")
        if block not in block_infra:
            block_infra[block] = {
                "schools": 0, "classrooms": 0, "good": 0, "minor_repair": 0, "major_repair": 0,
                "toilets": 0, "functional_toilets": 0, "dilapidated": 0
            }
        block_infra[block]["schools"] += 1
        block_infra[block]["classrooms"] += school.get("classrooms_instructional", 0)
        block_infra[block]["good"] += school.get("pucca_good", 0) + school.get("part_pucca_good", 0)
        block_infra[block]["minor_repair"] += school.get("pucca_minor", 0) + school.get("part_pucca_minor", 0)
        block_infra[block]["major_repair"] += school.get("pucca_major", 0) + school.get("part_pucca_major", 0)
        block_infra[block]["toilets"] += school.get("boys_toilets_total", 0) + school.get("girls_toilets_total", 0)
        block_infra[block]["functional_toilets"] += school.get("boys_toilets_functional", 0) + school.get("girls_toilets_functional", 0)
        block_infra[block]["dilapidated"] += school.get("classrooms_dilapidated", 0)
    
    # Calculate forecasts
    forecast_data = []
    for block, data in block_infra.items():
        total_cr = data["classrooms"]
        repair_rate = (data["minor_repair"] + data["major_repair"]) / max(total_cr, 1) * 100
        
        # Forecast: Assume 5% annual degradation
        minor_next_year = int(data["minor_repair"] * 1.2 + data["good"] * 0.05)
        major_next_year = int(data["major_repair"] * 1.1 + data["minor_repair"] * 0.1)
        
        forecast_data.append({
            "block": block,
            "schools": data["schools"],
            "total_classrooms": total_cr,
            "current_repair_needed": data["minor_repair"] + data["major_repair"],
            "repair_rate": round(repair_rate, 1),
            "dilapidated": data["dilapidated"],
            "forecast_minor_repair": minor_next_year,
            "forecast_major_repair": major_next_year,
            "estimated_budget_lakhs": round((minor_next_year * 0.5 + major_next_year * 2) / 100, 1),
            "priority": "High" if repair_rate > 10 or data["dilapidated"] > 5 else "Medium" if repair_rate > 5 else "Low"
        })
    
    forecast_data.sort(key=lambda x: x["repair_rate"], reverse=True)
    
    total_budget = sum(f["estimated_budget_lakhs"] for f in forecast_data)
    
    # Get AI insights
    try:
        ai_insights = await _generate_insights("infrastructure-forecast", {"forecast_data": forecast_data})
    except Exception as e:
        ai_insights = _format_ai_exception(e)
    
    return {
        "summary": {
            "total_blocks": len(forecast_data),
            "total_classrooms": sum(f["total_classrooms"] for f in forecast_data),
            "current_repair_needed": sum(f["current_repair_needed"] for f in forecast_data),
            "forecast_repair_needed": sum(f["forecast_minor_repair"] + f["forecast_major_repair"] for f in forecast_data),
            "total_dilapidated": sum(f["dilapidated"] for f in forecast_data),
            "estimated_budget_lakhs": round(total_budget, 1),
            "high_priority_blocks": len([f for f in forecast_data if f["priority"] == "High"])
        },
        "block_forecast": forecast_data,
        "ai_insights": ai_insights,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


@router.get("/predictions/teacher-shortage")
async def get_teacher_shortage_predictions(current_user: dict = Depends(get_current_user)):
    """Teacher shortage and retirement forecast"""
    
    # Gather teacher data
    ct_data = await db.ctteacher_analytics.find({}, {"_id": 0}).to_list(5000)
    
    # Aggregate by block
    block_teachers = {}
    age_distribution = {"<30": 0, "30-40": 0, "40-50": 0, "50-55": 0, "55+": 0}
    
    for teacher in ct_data:
        block = teacher.get("block_name", "Unknown")
        age = _age_from_dob(teacher.get("dob"))
        if age is None:
            age = 40
        
        if block not in block_teachers:
            block_teachers[block] = {"total": 0, "retiring_5yr": 0, "retiring_3yr": 0, "new_entrants": 0, "ctet": 0}
        
        block_teachers[block]["total"] += 1
        if age >= 55:
            block_teachers[block]["retiring_5yr"] += 1
            age_distribution["55+"] += 1
        elif age >= 52:
            block_teachers[block]["retiring_3yr"] += 1
            age_distribution["50-55"] += 1
        elif age >= 40:
            age_distribution["40-50"] += 1
        elif age >= 30:
            age_distribution["30-40"] += 1
        else:
            block_teachers[block]["new_entrants"] += 1
            age_distribution["<30"] += 1
        
        if teacher.get("ctet_qualified"):
            block_teachers[block]["ctet"] += 1
    
    # Calculate shortage forecasts
    shortage_data = []
    for block, data in block_teachers.items():
        retiring_pct = data["retiring_5yr"] / max(data["total"], 1) * 100
        shortage_data.append({
            "block": block,
            "total_teachers": data["total"],
            "retiring_in_5_years": data["retiring_5yr"],
            "retiring_in_3_years": data["retiring_3yr"],
            "new_entrants": data["new_entrants"],
            "ctet_qualified": data["ctet"],
            "ctet_rate": round(data["ctet"] / max(data["total"], 1) * 100, 1),
            "retirement_risk_pct": round(retiring_pct, 1),
            "forecast_shortage_5yr": data["retiring_5yr"] - data["new_entrants"],
            "risk_level": "High" if retiring_pct > 20 else "Medium" if retiring_pct > 10 else "Low"
        })
    
    shortage_data.sort(key=lambda x: x["retirement_risk_pct"], reverse=True)
    
    total_retiring = sum(s["retiring_in_5_years"] for s in shortage_data)
    
    # Get AI insights
    try:
        ai_insights = await _generate_insights(
            "teacher-shortage",
            {"shortage_data": shortage_data, "age_distribution": age_distribution},
        )
    except Exception as e:
        ai_insights = _format_ai_exception(e)
    
    return {
        "summary": {
            "total_teachers": sum(s["total_teachers"] for s in shortage_data),
            "retiring_in_5_years": total_retiring,
            "retiring_in_3_years": sum(s["retiring_in_3_years"] for s in shortage_data),
            "new_entrants": sum(s["new_entrants"] for s in shortage_data),
            "net_shortage_5yr": sum(s["forecast_shortage_5yr"] for s in shortage_data),
            "avg_ctet_rate": round(sum(s["ctet_rate"] for s in shortage_data) / max(len(shortage_data), 1), 1),
            "high_risk_blocks": len([s for s in shortage_data if s["risk_level"] == "High"])
        },
        "age_distribution": age_distribution,
        "block_forecast": shortage_data,
        "ai_insights": ai_insights,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


@router.get("/predictions/data-completion")
async def get_data_completion_forecast(current_user: dict = Depends(get_current_user)):
    """APAAR/Aadhaar completion timeline prediction"""
    
    # Gather data
    apaar_data = await db.apaar_analytics.find({}, {"_id": 0}).to_list(1000)
    aadhaar_data = await db.aadhaar_analytics.find({}, {"_id": 0}).to_list(1000)
    
    # Calculate APAAR metrics
    apaar_metrics = []
    for school in apaar_data:
        block = school.get("block_name", "Unknown")
        total = school.get("total_student", 0)
        generated = school.get("total_generated", 0)
        rate = generated / max(total, 1) * 100
        
        # Estimate completion based on current rate
        pending = total - generated
        # Assume 2% weekly progress
        weeks_to_complete = int(pending / max(total * 0.02, 1)) if rate < 100 else 0
        
        apaar_metrics.append({
            "school": school.get("school_name", "Unknown")[:40],
            "block": block,
            "total_students": total,
            "generated": generated,
            "generation_rate": round(rate, 1),
            "pending": pending,
            "weeks_to_complete": min(weeks_to_complete, 52)
        })
    
    # Aggregate by block
    block_completion = {}
    for m in apaar_metrics:
        block = m["block"]
        if block not in block_completion:
            block_completion[block] = {"total": 0, "generated": 0, "schools": 0}
        block_completion[block]["total"] += m["total_students"]
        block_completion[block]["generated"] += m["generated"]
        block_completion[block]["schools"] += 1
    
    block_data = []
    for block, data in block_completion.items():
        rate = data["generated"] / max(data["total"], 1) * 100
        pending = data["total"] - data["generated"]
        weeks = int(pending / max(data["total"] * 0.02, 1)) if rate < 100 else 0
        block_data.append({
            "block": block,
            "total_students": data["total"],
            "generated": data["generated"],
            "rate": round(rate, 1),
            "pending": pending,
            "estimated_weeks": min(weeks, 52),
            "completion_date": "Complete" if rate >= 99.9 else f"{weeks} weeks"
        })
    
    block_data.sort(key=lambda x: x["rate"])
    
    total_students = sum(b["total_students"] for b in block_data)
    total_generated = sum(b["generated"] for b in block_data)
    overall_rate = round(total_generated / max(total_students, 1) * 100, 1)
    
    # Get AI insights
    try:
        ai_insights = await _generate_insights("data-completion", {"block_data": block_data, "overall_rate": overall_rate})
    except Exception as e:
        ai_insights = _format_ai_exception(e)
    
    return {
        "summary": {
            "total_students": total_students,
            "apaar_generated": total_generated,
            "overall_rate": overall_rate,
            "pending": total_students - total_generated,
            "estimated_weeks_to_100": int((total_students - total_generated) / max(total_students * 0.02, 1)),
            "blocks_above_90": len([b for b in block_data if b["rate"] >= 90]),
            "blocks_below_80": len([b for b in block_data if b["rate"] < 80])
        },
        "block_data": block_data,
        "ai_insights": ai_insights,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


@router.get("/insights/executive-summary")
async def get_executive_insights(current_user: dict = Depends(get_current_user)):
    """AI-generated executive summary with insights and recommendations"""
    
    # Gather all key metrics
    ct_count = await db.classrooms_toilets.count_documents({})
    teacher_count = await db.ctteacher_analytics.count_documents({})
    
    # Infrastructure summary
    ct_pipeline = [{"$group": {"_id": None, 
        "classrooms": {"$sum": "$classrooms_instructional"},
        "good": {"$sum": {"$add": ["$pucca_good", "$part_pucca_good"]}},
        "toilets": {"$sum": {"$add": ["$boys_toilets_total", "$girls_toilets_total"]}},
        "functional": {"$sum": {"$add": ["$boys_toilets_functional", "$girls_toilets_functional"]}}
    }}]
    ct_result = await db.classrooms_toilets.aggregate(ct_pipeline).to_list(1)
    ct = ct_result[0] if ct_result else {}
    
    # APAAR summary
    apaar_pipeline = [{"$group": {"_id": None, "students": {"$sum": "$total_student"}, "generated": {"$sum": "$total_generated"}}}]
    apaar_result = await db.apaar_analytics.aggregate(apaar_pipeline).to_list(1)
    apaar = apaar_result[0] if apaar_result else {}
    
    # Dropbox summary
    dropbox_pipeline = [{"$group": {"_id": None, "total": {"$sum": "$total_remarks"}, "dropout": {"$sum": "$dropout"}}}]
    dropbox_result = await db.dropbox_analytics.aggregate(dropbox_pipeline).to_list(1)
    dropbox = dropbox_result[0] if dropbox_result else {}
    
    metrics = {
        "schools": ct_count,
        "teachers": teacher_count,
        "students": apaar.get("students", 0),
        "classrooms": ct.get("classrooms", 0),
        "classroom_health": round(ct.get("good", 0) / max(ct.get("classrooms", 1), 1) * 100, 1),
        "toilets": ct.get("toilets", 0),
        "toilet_functional": round(ct.get("functional", 0) / max(ct.get("toilets", 1), 1) * 100, 1),
        "apaar_rate": round(apaar.get("generated", 0) / max(apaar.get("students", 1), 1) * 100, 1),
        "dropout_rate": round(dropbox.get("dropout", 0) / max(dropbox.get("total", 1), 1) * 100, 2)
    }
    
    # Get AI executive summary
    try:
        ai_summary = await _generate_insights("executive-summary", {"metrics": metrics})
    except Exception as e:
        ai_summary = _format_ai_exception(e)
    
    return {
        "metrics": metrics,
        "ai_summary": ai_summary,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


@router.get("/map/block-metrics")
async def get_block_map_metrics():
    """Get block-wise metrics for choropleth map"""
    
    # Aggregate metrics by block
    ct_pipeline = [
        {"$group": {
            "_id": "$block_name",
            "schools": {"$sum": 1},
            "classrooms": {"$sum": "$classrooms_instructional"},
            "good_classrooms": {"$sum": {"$add": ["$pucca_good", "$part_pucca_good"]}},
            "toilets": {"$sum": {"$add": ["$boys_toilets_total", "$girls_toilets_total"]}},
            "functional_toilets": {"$sum": {"$add": ["$boys_toilets_functional", "$girls_toilets_functional"]}},
            "handwash": {"$sum": {"$cond": [{"$eq": ["$handwash_facility", True]}, 1, 0]}}
        }}
    ]
    ct_data = await db.classrooms_toilets.aggregate(ct_pipeline).to_list(50)
    
    # APAAR data
    apaar_pipeline = [
        {"$group": {
            "_id": "$block_name",
            "students": {"$sum": "$total_student"},
            "generated": {"$sum": "$total_generated"}
        }}
    ]
    apaar_data = await db.apaar_analytics.aggregate(apaar_pipeline).to_list(50)
    apaar_map = {a["_id"]: a for a in apaar_data}
    
    # Teacher data
    teacher_pipeline = [
        {"$group": {
            "_id": "$block_name",
            "teachers": {"$sum": 1},
            "ctet": {
                "$sum": {
                    "$cond": [
                        {
                            "$or": [
                                {"$eq": ["$ctet_qualified", True]},
                                {"$gt": ["$ctet_qualified", 0]},
                            ]
                        },
                        1,
                        0,
                    ]
                }
            }
        }}
    ]
    teacher_data = await db.ctteacher_analytics.aggregate(teacher_pipeline).to_list(50)
    teacher_map = {t["_id"]: t for t in teacher_data}
    
    # Combine metrics
    block_metrics = []
    for ct in ct_data:
        block_name = ct["_id"]
        apaar = apaar_map.get(block_name, {})
        teacher = teacher_map.get(block_name, {})
        
        classroom_health = round(ct["good_classrooms"] / max(ct["classrooms"], 1) * 100, 1)
        toilet_pct = round(ct["functional_toilets"] / max(ct["toilets"], 1) * 100, 1)
        apaar_rate = round(apaar.get("generated", 0) / max(apaar.get("students", 1), 1) * 100, 1)
        ctet_rate = round(teacher.get("ctet", 0) / max(teacher.get("teachers", 1), 1) * 100, 1)
        
        # Calculate SHI
        shi = round((classroom_health * 0.25 + toilet_pct * 0.25 + apaar_rate * 0.25 + min(ctet_rate * 3, 25)) , 1)
        
        block_metrics.append({
            "block_name": block_name,
            "schools": ct["schools"],
            "students": apaar.get("students", 0),
            "teachers": teacher.get("teachers", 0),
            "classroom_health": classroom_health,
            "toilet_functional": toilet_pct,
            "apaar_rate": apaar_rate,
            "teacher_quality": ctet_rate,
            "shi_score": shi,
            "rag_status": "green" if shi >= 75 else "amber" if shi >= 60 else "red"
        })
    
    block_metrics.sort(key=lambda x: x["shi_score"], reverse=True)
    
    return {
        "blocks": block_metrics,
        "total_blocks": len(block_metrics),
        "metric_ranges": {
            "shi": {"min": min(b["shi_score"] for b in block_metrics), "max": max(b["shi_score"] for b in block_metrics)},
            "classroom_health": {"min": min(b["classroom_health"] for b in block_metrics), "max": max(b["classroom_health"] for b in block_metrics)},
            "apaar_rate": {"min": min(b["apaar_rate"] for b in block_metrics), "max": max(b["apaar_rate"] for b in block_metrics)}
        }
    }
