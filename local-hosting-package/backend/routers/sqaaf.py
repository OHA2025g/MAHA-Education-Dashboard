"""
SQAAF (School Quality Assessment and Accreditation Framework) Analytics Router.
ETL: Excel -> MongoDB. Dashboard reads from MongoDB (sqaaf_meta, sqaaf_schools, sqaaf_blocks).
"""
import io
import math
import re
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import pandas as pd
import numpy as np
from fastapi import APIRouter, Query, HTTPException, UploadFile, File


def _sanitize_for_json(obj: Any) -> Any:
    """Replace NaN/Inf floats with None so response is JSON-serializable."""
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_for_json(v) for v in obj]
    if isinstance(obj, float) and (math.isnan(obj) or math.isinf(obj)):
        return None
    if hasattr(obj, "item"):  # numpy scalar (e.g. np.float64 from MongoDB)
        try:
            v = obj.item()
            if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                return None
            return v
        except (ValueError, AttributeError):
            return None
    return obj

router = APIRouter(prefix="/sqaaf", tags=["SQAAF"])

# Database and uploads (set by init_db)
db = None
UPLOADS_DIR: Optional[Path] = None
_sqaaf_cache: Optional[tuple] = None

# Regex for question columns: e.g. "1.1. 1", "2.3. 15"
QUESTION_COL_PATTERN = re.compile(r"^\d+\.\d+\.\s*\d+", re.IGNORECASE)

# Score band bins
BANDS = [
    (float("-inf"), 40, "Critical"),
    (40, 55, "Needs Focus"),
    (55, 70, "Developing"),
    (70, 85, "Strong"),
    (85, float("inf"), "Exemplary"),
]


def init_db(database, uploads_dir):
    global db, UPLOADS_DIR
    db = database
    UPLOADS_DIR = Path(uploads_dir) if uploads_dir else None


def _get_excel_path() -> Path:
    """Resolve path to Pune_District_SQAAF.xlsx (env, uploads, backend/data/excel, Docker mount, cwd, workspace root)."""
    filename = "Pune_District_SQAAF.xlsx"
    env_path = os.environ.get("SQAAF_EXCEL_PATH")
    if env_path:
        p = Path(env_path)
        if p.is_file():
            return p
    if UPLOADS_DIR:
        p = UPLOADS_DIR / filename
        if p.is_file():
            return p
    base = Path(__file__).resolve().parent.parent  # backend dir
    cwd = Path.cwd()
    candidates = [
        base / "data" / "excel" / filename,           # backend/data/excel
        base.parent / "data" / "excel" / filename,   # local-hosting-package/data/excel (Docker mount)
        Path("/app/data/excel") / filename,           # explicit Docker app mount
        cwd / filename,                               # workspace/project root (e.g. Dashboard for Pune)
        cwd / "data" / "excel" / filename,
        cwd / "local-hosting-package" / "data" / "excel" / filename,
        cwd / "local-hosting-package" / "backend" / "data" / "excel" / filename,
    ]
    for p in candidates:
        if p.is_file():
            return p
    for candidate in [base.parent.parent, base.parent.parent.parent, cwd]:
        p = candidate / filename
        if p.is_file():
            return p
    raise FileNotFoundError(
        "Pune_District_SQAAF.xlsx not found. Set SQAAF_EXCEL_PATH or place file in backend/data/excel/ or project root."
    )


def _identify_columns(df: pd.DataFrame) -> tuple:
    """Return (metadata_cols, question_cols). Question cols match pattern like 1.1. 1."""
    meta_candidates = [
        "district", "block", "cluster", "school name", "school code", "school management",
        "school category", "answered", "percentage"
    ]
    meta_cols = []
    question_cols = []
    for c in df.columns:
        c_str = str(c).strip()
        if not c_str:
            continue
        if QUESTION_COL_PATTERN.match(c_str):
            question_cols.append(c)
        else:
            c_lower = c_str.lower()
            if any(m in c_lower for m in meta_candidates) or c_str.replace(" ", "").lower() in ["answered", "percentage"]:
                meta_cols.append(c)
    return meta_cols, question_cols


def _normalize_meta_name(col: str) -> str:
    """Map Excel column to standard name. Be specific for 'answered' to avoid merging multiple columns."""
    c = str(col).strip().lower().replace(" ", "_")
    c_exact = str(col).strip().lower()
    if "district" in c and "code" not in c:
        return "district"
    if "block" in c and "code" not in c:
        return "block"
    if "cluster" in c:
        return "cluster"
    if "school_name" in c or "schoolname" in c:
        return "school_name"
    if "school_code" in c or "schoolcode" in c or "udise" in c:
        return "school_code"
    if "management" in c:
        return "school_management"
    if "category" in c:
        return "school_category"
    if c_exact == "answered" or c == "answered":
        return "answered"
    if c_exact == "percentage" or c == "percentage":
        return "percentage"
    return col


def _band(score: float) -> str:
    for lo, hi, label in BANDS:
        if lo < score <= hi:
            return label
    return "Critical"


def _load_and_compute() -> Dict[str, Any]:
    """Load Excel, compute derived fields and KPIs. Cached by file mtime."""
    global _sqaaf_cache
    path = _get_excel_path()
    mtime = path.stat().st_mtime
    if _sqaaf_cache is not None and _sqaaf_cache[0] == mtime:
        return _sqaaf_cache[1]

    df = pd.read_excel(path, sheet_name="Sheet1", header=1)
    df.columns = [str(c).strip() for c in df.columns]
    meta_cols, question_cols = _identify_columns(df)
    if not question_cols:
        raise ValueError("No question columns found (expected pattern like 1.1. 1)")

    # Normalize metadata column names for consistent access
    meta_map = {}
    for c in df.columns:
        if c in question_cols:
            continue
        meta_map[c] = _normalize_meta_name(c)
    df = df.rename(columns=meta_map)

    # Numeric question scores
    for q in question_cols:
        df[q] = pd.to_numeric(df[q], errors="coerce")

    # Derived: answered (if not present, count non-null questions)
    if "answered" not in df.columns:
        df["answered"] = df[question_cols].notna().sum(axis=1)
    else:
        df["answered"] = pd.to_numeric(df["answered"], errors="coerce").fillna(0).astype(int)

    n_questions = len(question_cols)
    df["Answered_%"] = np.round((df["answered"] / n_questions) * 100, 2)
    df["SQAAF_Score_%"] = np.round((df[question_cols].mean(axis=1) / 4.0) * 100, 2)
    df["Band"] = df["SQAAF_Score_%"].apply(_band)

    # Section mapping: group by prefix X.Y from column name
    section_prefix = re.compile(r"^(\d+\.\d+)")
    section_to_cols: Dict[str, List[str]] = {}
    for q in question_cols:
        m = section_prefix.match(str(q))
        key = m.group(1) if m else "Other"
        section_to_cols.setdefault(key, []).append(q)
    sections_ordered = sorted(section_to_cols.keys(), key=lambda x: (int(x.split(".")[0]), int(x.split(".")[1])))
    for sec in sections_ordered:
        cols = section_to_cols[sec]
        df[f"Section_{sec}_Score_%"] = np.round((df[cols].mean(axis=1) / 4.0) * 100, 2)

    # Build school list for API (with question_scores for school-detail / ETL)
    schools = []
    for _, row in df.iterrows():
        rec = {
            "school_code": str(row.get("school_code", "")).strip() if pd.notna(row.get("school_code")) else "",
            "school_name": str(row.get("school_name", "")).strip() if pd.notna(row.get("school_name")) else "",
            "block": str(row.get("block", "")).strip() if pd.notna(row.get("block")) else "",
            "cluster": str(row.get("cluster", "")).strip() if pd.notna(row.get("cluster")) else "",
            "school_management": str(row.get("school_management", "")).strip() if pd.notna(row.get("school_management")) else "",
            "school_category": str(row.get("school_category", "")).strip() if pd.notna(row.get("school_category")) else "",
            "answered": int(row.get("answered", 0)) if pd.notna(row.get("answered")) else 0,
            "Answered_%": float(row.get("Answered_%", 0)),
            "SQAAF_Score_%": float(row.get("SQAAF_Score_%", 0)),
            "Band": str(row.get("Band", "Critical")),
        }
        for sec in sections_ordered:
            rec[f"Section_{sec}_Score_%"] = float(row.get(f"Section_{sec}_Score_%", 0))
        rec["question_scores"] = {q: float(row[q]) for q in question_cols if pd.notna(row.get(q))}
        schools.append(rec)

    scores = df["SQAAF_Score_%"].dropna()
    n_schools = len(df)
    district_mean = float(scores.mean()) if len(scores) else 0
    district_median = float(scores.median()) if len(scores) else 0
    district_std = float(scores.std()) if len(scores) > 1 else 0
    top25 = scores.quantile(0.75)
    bottom25 = scores.quantile(0.25)
    equity_gap = float(top25 - bottom25) if len(scores) >= 4 else 0
    band_counts = df["Band"].value_counts()
    critical_pct = round((band_counts.get("Critical", 0) / n_schools) * 100, 2) if n_schools else 0
    needs_focus_pct = round((band_counts.get("Needs Focus", 0) / n_schools) * 100, 2) if n_schools else 0
    developing_pct = round((band_counts.get("Developing", 0) / n_schools) * 100, 2) if n_schools else 0
    strong_pct = round((band_counts.get("Strong", 0) / n_schools) * 100, 2) if n_schools else 0
    exemplary_pct = round((band_counts.get("Exemplary", 0) / n_schools) * 100, 2) if n_schools else 0
    completion_rate = float(df["Answered_%"].mean()) if n_schools else 0
    full_compliance = int((df["answered"] >= n_questions).sum())
    full_compliance_rate = round((full_compliance / n_schools) * 100, 2) if n_schools else 0
    intervention_load = round((df["SQAAF_Score_%"] < 60).sum() / n_schools * 100, 2) if n_schools else 0
    question_coverage = {q: round((df[q].notna().sum() / n_schools) * 100, 2) for q in question_cols}

    # Block stats
    block_agg = df.groupby("block", dropna=False).agg(
        schools=("SQAAF_Score_%", "count"),
        mean=("SQAAF_Score_%", "mean"),
        median=("SQAAF_Score_%", "median"),
        std=("SQAAF_Score_%", "std"),
    ).reset_index()
    block_agg["mean"] = block_agg["mean"].round(2)
    block_agg["median"] = block_agg["median"].round(2)
    block_agg["std"] = block_agg["std"].fillna(0).round(2)
    critical_by_block = df[df["Band"] == "Critical"].groupby("block", dropna=False).size().reindex(block_agg["block"], fill_value=0)
    block_agg["critical_count"] = critical_by_block.values
    block_agg["critical_pct"] = (block_agg["critical_count"] / block_agg["schools"] * 100).round(2)
    block_best_mean = block_agg["mean"].max() if len(block_agg) else 0
    block_worst_mean = block_agg["mean"].min() if len(block_agg) else 0
    block_gap = round(float(block_best_mean - block_worst_mean), 2)

    # Section (domain) stats
    section_means = {}
    for sec in sections_ordered:
        col = f"Section_{sec}_Score_%"
        section_means[sec] = round(float(df[col].mean()), 2)
    section_ordered_by_mean = sorted(section_means.keys(), key=lambda s: section_means[s])
    section_summary = []
    for sec in sections_ordered:
        col = f"Section_{sec}_Score_%"
        section_summary.append({
            "section": sec,
            "question_count": len(section_to_cols[sec]),
            "coverage_%": round((df[col].notna().sum() / n_schools) * 100, 2) if n_schools else 0,
            "mean": section_means[sec],
            "median": round(float(df[col].median()), 2),
        })

    # Management / Category
    mgmt_agg = df.groupby("school_management", dropna=False).agg(
        schools=("SQAAF_Score_%", "count"),
        mean=("SQAAF_Score_%", "mean"),
        std=("SQAAF_Score_%", "std"),
    ).reset_index()
    mgmt_agg["mean"] = mgmt_agg["mean"].round(2)
    mgmt_agg["std"] = mgmt_agg["std"].fillna(0).round(2)
    cat_agg = df.groupby("school_category", dropna=False).agg(
        schools=("SQAAF_Score_%", "count"),
        mean=("SQAAF_Score_%", "mean"),
        std=("SQAAF_Score_%", "std"),
    ).reset_index()
    cat_agg["mean"] = cat_agg["mean"].round(2)
    cat_agg["std"] = cat_agg["std"].fillna(0).round(2)

    # Bottom 10 questions (by mean score %)
    q_means = df[question_cols].mean() / 4.0 * 100
    bottom_questions = q_means.sort_values().head(10).reset_index()
    bottom_questions.columns = ["question", "mean_score_%"]
    bottom_questions["mean_score_%"] = bottom_questions["mean_score_%"].round(2)

    # Priority domains (bottom 5 sections)
    priority_domains = sorted(section_means.items(), key=lambda x: x[1])[:5]

    # Block intervention priority index: 0.6 * (% schools <60 in block) + 0.4 * (% critical in block)
    pct_below_60_series = df.groupby("block", dropna=False).apply(
        lambda g: (g["SQAAF_Score_%"] < 60).sum() / len(g) * 100 if len(g) else 0
    )
    block_agg["pct_below_60"] = block_agg["block"].map(lambda b: pct_below_60_series.get(b, 0)).fillna(0).values
    block_agg["intervention_index"] = (0.6 * block_agg["pct_below_60"] + 0.4 * block_agg["critical_pct"]).round(2)
    block_agg = block_agg.sort_values("mean", ascending=False).reset_index(drop=True)

    result = {
        "n_schools": n_schools,
        "n_questions": n_questions,
        "question_columns": question_cols,
        "sections_ordered": sections_ordered,
        "section_to_cols": section_to_cols,
        "district_mean": round(district_mean, 2),
        "district_median": round(district_median, 2),
        "district_std": round(district_std, 2),
        "equity_gap": equity_gap,
        "critical_pct": critical_pct,
        "needs_focus_pct": needs_focus_pct,
        "developing_pct": developing_pct,
        "strong_pct": strong_pct,
        "exemplary_pct": exemplary_pct,
        "completion_rate": round(completion_rate, 2),
        "full_compliance_rate": full_compliance_rate,
        "full_compliance_count": full_compliance,
        "intervention_load": intervention_load,
        "question_coverage": question_coverage,
        "block_gap": block_gap,
        "schools": schools,
        "block_summary": block_agg.to_dict("records"),
        "section_summary": section_summary,
        "section_means": section_means,
        "management_summary": mgmt_agg.to_dict("records"),
        "category_summary": cat_agg.to_dict("records"),
        "bottom_questions": bottom_questions.to_dict("records"),
        "priority_domains": [{"section": s, "mean": m} for s, m in priority_domains],
        "score_histogram": _histogram_bins(df["SQAAF_Score_%"].dropna(), bin_size=5),
        "band_distribution": [
            {"band": b, "count": int(band_counts.get(b, 0)), "pct": round((band_counts.get(b, 0) / n_schools) * 100, 2) if n_schools else 0}
            for _, _, b in BANDS
        ],
    }
    _sqaaf_cache = (mtime, result)
    return result


def _load_and_compute_from_path(path: Path) -> Dict[str, Any]:
    """Load Excel from path and compute same structure as _load_and_compute (no cache). Used by ETL."""
    df = pd.read_excel(path, sheet_name="Sheet1", header=1)
    df.columns = [str(c).strip() for c in df.columns]
    meta_cols, question_cols = _identify_columns(df)
    if not question_cols:
        raise ValueError("No question columns found (expected pattern like 1.1. 1)")
    meta_map = {}
    for c in df.columns:
        if c in question_cols:
            continue
        meta_map[c] = _normalize_meta_name(c)
    df = df.rename(columns=meta_map)
    for q in question_cols:
        df[q] = pd.to_numeric(df[q], errors="coerce")
    if "answered" not in df.columns:
        df["answered"] = df[question_cols].notna().sum(axis=1)
    else:
        df["answered"] = pd.to_numeric(df["answered"], errors="coerce").fillna(0).astype(int)
    n_questions = len(question_cols)
    df["Answered_%"] = np.round((df["answered"] / n_questions) * 100, 2)
    df["SQAAF_Score_%"] = np.round((df[question_cols].mean(axis=1) / 4.0) * 100, 2)
    df["Band"] = df["SQAAF_Score_%"].apply(_band)
    section_prefix = re.compile(r"^(\d+\.\d+)")
    section_to_cols = {}
    for q in question_cols:
        m = section_prefix.match(str(q))
        key = m.group(1) if m else "Other"
        section_to_cols.setdefault(key, []).append(q)
    sections_ordered = sorted(section_to_cols.keys(), key=lambda x: (int(x.split(".")[0]), int(x.split(".")[1])))
    for sec in sections_ordered:
        cols = section_to_cols[sec]
        df[f"Section_{sec}_Score_%"] = np.round((df[cols].mean(axis=1) / 4.0) * 100, 2)
    schools = []
    for _, row in df.iterrows():
        rec = {
            "school_code": str(row.get("school_code", "")).strip() if pd.notna(row.get("school_code")) else "",
            "school_name": str(row.get("school_name", "")).strip() if pd.notna(row.get("school_name")) else "",
            "block": str(row.get("block", "")).strip() if pd.notna(row.get("block")) else "",
            "cluster": str(row.get("cluster", "")).strip() if pd.notna(row.get("cluster")) else "",
            "school_management": str(row.get("school_management", "")).strip() if pd.notna(row.get("school_management")) else "",
            "school_category": str(row.get("school_category", "")).strip() if pd.notna(row.get("school_category")) else "",
            "answered": int(row.get("answered", 0)) if pd.notna(row.get("answered")) else 0,
            "Answered_%": float(row.get("Answered_%", 0)),
            "SQAAF_Score_%": float(row.get("SQAAF_Score_%", 0)),
            "Band": str(row.get("Band", "Critical")),
        }
        for sec in sections_ordered:
            rec[f"Section_{sec}_Score_%"] = float(row.get(f"Section_{sec}_Score_%", 0))
        rec["question_scores"] = {q: float(row[q]) for q in question_cols if pd.notna(row.get(q))}
        schools.append(rec)
    scores = df["SQAAF_Score_%"].dropna()
    n_schools = len(df)
    district_mean = float(scores.mean()) if len(scores) else 0
    district_median = float(scores.median()) if len(scores) else 0
    district_std = float(scores.std()) if len(scores) > 1 else 0
    top25 = scores.quantile(0.75)
    bottom25 = scores.quantile(0.25)
    equity_gap = float(top25 - bottom25) if len(scores) >= 4 else 0
    band_counts = df["Band"].value_counts()
    critical_pct = round((band_counts.get("Critical", 0) / n_schools) * 100, 2) if n_schools else 0
    needs_focus_pct = round((band_counts.get("Needs Focus", 0) / n_schools) * 100, 2) if n_schools else 0
    developing_pct = round((band_counts.get("Developing", 0) / n_schools) * 100, 2) if n_schools else 0
    strong_pct = round((band_counts.get("Strong", 0) / n_schools) * 100, 2) if n_schools else 0
    exemplary_pct = round((band_counts.get("Exemplary", 0) / n_schools) * 100, 2) if n_schools else 0
    completion_rate = float(df["Answered_%"].mean()) if n_schools else 0
    full_compliance = int((df["answered"] >= n_questions).sum())
    full_compliance_rate = round((full_compliance / n_schools) * 100, 2) if n_schools else 0
    intervention_load = round((df["SQAAF_Score_%"] < 60).sum() / n_schools * 100, 2) if n_schools else 0
    question_coverage = {q: round((df[q].notna().sum() / n_schools) * 100, 2) for q in question_cols}
    block_agg = df.groupby("block", dropna=False).agg(
        schools=("SQAAF_Score_%", "count"),
        mean=("SQAAF_Score_%", "mean"),
        median=("SQAAF_Score_%", "median"),
        std=("SQAAF_Score_%", "std"),
    ).reset_index()
    block_agg["mean"] = block_agg["mean"].round(2)
    block_agg["median"] = block_agg["median"].round(2)
    block_agg["std"] = block_agg["std"].fillna(0).round(2)
    critical_by_block = df[df["Band"] == "Critical"].groupby("block", dropna=False).size().reindex(block_agg["block"], fill_value=0)
    block_agg["critical_count"] = critical_by_block.values
    block_agg["critical_pct"] = (block_agg["critical_count"] / block_agg["schools"] * 100).round(2)
    pct_below_60_series = df.groupby("block", dropna=False).apply(
        lambda g: (g["SQAAF_Score_%"] < 60).sum() / len(g) * 100 if len(g) else 0
    )
    block_agg["pct_below_60"] = block_agg["block"].map(lambda b: pct_below_60_series.get(b, 0)).fillna(0).values
    block_agg["intervention_index"] = (0.6 * block_agg["pct_below_60"] + 0.4 * block_agg["critical_pct"]).round(2)
    block_agg = block_agg.sort_values("mean", ascending=False).reset_index(drop=True)
    block_gap = round(float(block_agg["mean"].max() - block_agg["mean"].min()), 2) if len(block_agg) else 0
    section_means = {}
    for sec in sections_ordered:
        col = f"Section_{sec}_Score_%"
        section_means[sec] = round(float(df[col].mean()), 2)
    section_summary = []
    for sec in sections_ordered:
        col = f"Section_{sec}_Score_%"
        section_summary.append({
            "section": sec,
            "question_count": len(section_to_cols[sec]),
            "coverage_%": round((df[col].notna().sum() / n_schools) * 100, 2) if n_schools else 0,
            "mean": section_means[sec],
            "median": round(float(df[col].median()), 2),
        })
    mgmt_agg = df.groupby("school_management", dropna=False).agg(
        schools=("SQAAF_Score_%", "count"),
        mean=("SQAAF_Score_%", "mean"),
        std=("SQAAF_Score_%", "std"),
    ).reset_index()
    mgmt_agg["mean"] = mgmt_agg["mean"].round(2)
    mgmt_agg["std"] = mgmt_agg["std"].fillna(0).round(2)
    cat_agg = df.groupby("school_category", dropna=False).agg(
        schools=("SQAAF_Score_%", "count"),
        mean=("SQAAF_Score_%", "mean"),
        std=("SQAAF_Score_%", "std"),
    ).reset_index()
    cat_agg["mean"] = cat_agg["mean"].round(2)
    cat_agg["std"] = cat_agg["std"].fillna(0).round(2)
    q_means = df[question_cols].mean() / 4.0 * 100
    bottom_questions = q_means.sort_values().head(10).reset_index()
    bottom_questions.columns = ["question", "mean_score_%"]
    bottom_questions["mean_score_%"] = bottom_questions["mean_score_%"].round(2)
    priority_domains = sorted(section_means.items(), key=lambda x: x[1])[:5]
    score_histogram = _histogram_bins(df["SQAAF_Score_%"].dropna(), 5)
    band_distribution = [
        {"band": b, "count": int(band_counts.get(b, 0)), "pct": round((band_counts.get(b, 0) / n_schools) * 100, 2) if n_schools else 0}
        for _, _, b in BANDS
    ]
    return {
        "n_schools": n_schools,
        "n_questions": n_questions,
        "question_columns": question_cols,
        "sections_ordered": sections_ordered,
        "section_to_cols": section_to_cols,
        "district_mean": round(district_mean, 2),
        "district_median": round(district_median, 2),
        "district_std": round(district_std, 2),
        "equity_gap": equity_gap,
        "critical_pct": critical_pct,
        "needs_focus_pct": needs_focus_pct,
        "developing_pct": developing_pct,
        "strong_pct": strong_pct,
        "exemplary_pct": exemplary_pct,
        "completion_rate": round(completion_rate, 2),
        "full_compliance_rate": full_compliance_rate,
        "full_compliance_count": full_compliance,
        "intervention_load": intervention_load,
        "question_coverage": question_coverage,
        "block_gap": block_gap,
        "schools": schools,
        "block_summary": block_agg.to_dict("records"),
        "section_summary": section_summary,
        "section_means": section_means,
        "management_summary": mgmt_agg.to_dict("records"),
        "category_summary": cat_agg.to_dict("records"),
        "bottom_questions": bottom_questions.to_dict("records"),
        "priority_domains": [{"section": s, "mean": m} for s, m in priority_domains],
        "score_histogram": score_histogram,
        "band_distribution": band_distribution,
    }


async def _etl_to_mongo(data: Dict[str, Any], source_file: str = "") -> str:
    """Write ETL result to MongoDB. Replaces existing SQAAF data. Returns import_id."""
    if db is None:
        raise RuntimeError("Database not initialized")
    import_id = datetime.now(timezone.utc).isoformat()
    meta_doc = {
        "import_id": import_id,
        "imported_at": datetime.now(timezone.utc),
        "source_file": source_file,
        "n_schools": data["n_schools"],
        "n_questions": data["n_questions"],
        "question_columns": data["question_columns"],
        "sections_ordered": data["sections_ordered"],
        "section_to_cols": data["section_to_cols"],
        "district_mean": data["district_mean"],
        "district_median": data["district_median"],
        "district_std": data["district_std"],
        "equity_gap": data["equity_gap"],
        "critical_pct": data["critical_pct"],
        "needs_focus_pct": data["needs_focus_pct"],
        "developing_pct": data["developing_pct"],
        "strong_pct": data["strong_pct"],
        "exemplary_pct": data["exemplary_pct"],
        "completion_rate": data["completion_rate"],
        "full_compliance_rate": data["full_compliance_rate"],
        "full_compliance_count": data["full_compliance_count"],
        "intervention_load": data["intervention_load"],
        "question_coverage": data["question_coverage"],
        "block_gap": data["block_gap"],
        "section_summary": data["section_summary"],
        "section_means": data["section_means"],
        "management_summary": data["management_summary"],
        "category_summary": data["category_summary"],
        "bottom_questions": data["bottom_questions"],
        "priority_domains": data["priority_domains"],
        "score_histogram": data["score_histogram"],
        "band_distribution": data["band_distribution"],
    }
    school_docs = []
    for s in data["schools"]:
        doc = {k: v for k, v in s.items() if k != "_id"}
        school_docs.append(doc)
    block_docs = [{"import_id": import_id, **b} for b in data["block_summary"]]
    await db.sqaaf_meta.delete_many({})
    await db.sqaaf_schools.delete_many({})
    await db.sqaaf_blocks.delete_many({})
    await db.sqaaf_meta.insert_one(meta_doc)
    if school_docs:
        await db.sqaaf_schools.insert_many(school_docs)
    if block_docs:
        await db.sqaaf_blocks.insert_many(block_docs)
    return import_id


async def _get_meta_from_mongo() -> Optional[Dict]:
    """Return latest SQAAF meta document or None."""
    if db is None:
        return None
    doc = await db.sqaaf_meta.find_one({}, {"_id": 0})
    return doc


async def _get_schools_from_mongo(
    block: Optional[str] = None,
    cluster: Optional[str] = None,
    school_management: Optional[str] = None,
    school_category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 500,
    offset: int = 0,
    for_count: bool = False,
) -> Any:
    """Query sqaaf_schools with filters. Returns list of schools or total count."""
    if db is None:
        return [] if not for_count else 0
    match = {}
    if block:
        match["block"] = {"$regex": f"^{re.escape(block.strip())}$", "$options": "i"}
    if cluster:
        match["cluster"] = {"$regex": f"^{re.escape(cluster.strip())}$", "$options": "i"}
    if school_management:
        match["school_management"] = {"$regex": f"^{re.escape(school_management.strip())}$", "$options": "i"}
    if school_category:
        match["school_category"] = {"$regex": f"^{re.escape(school_category.strip())}$", "$options": "i"}
    if search:
        search_clean = search.strip()
        match["$or"] = [
            {"school_name": {"$regex": search_clean, "$options": "i"}},
            {"school_code": {"$regex": search_clean, "$options": "i"}},
        ]
    cursor = db.sqaaf_schools.find(match, {"_id": 0})
    if for_count:
        return await db.sqaaf_schools.count_documents(match)
    schools = await cursor.skip(offset).limit(limit).to_list(length=limit + 1)
    return schools


async def _get_blocks_from_mongo(block_filter: Optional[str] = None) -> List[Dict]:
    if db is None:
        return []
    match = {}
    if block_filter:
        match["block"] = {"$regex": f"^{re.escape(block_filter.strip())}$", "$options": "i"}
    cursor = db.sqaaf_blocks.find(match, {"_id": 0, "import_id": 0})
    return await cursor.to_list(length=500)


def _histogram_bins(series: pd.Series, bin_size: float = 5) -> List[Dict]:
    """Return list of {bin_start, bin_end, count} for histogram."""
    if series.empty:
        return []
    min_s, max_s = series.min(), series.max()
    bins = []
    x = min_s // bin_size * bin_size
    while x <= max_s + bin_size:
        count = ((series >= x) & (series < x + bin_size)).sum()
        bins.append({"bin_start": round(x, 1), "bin_end": round(x + bin_size, 1), "count": int(count)})
        x += bin_size
    return bins


def _filter_schools(data: Dict, block: Optional[str], cluster: Optional[str], management: Optional[str], category: Optional[str]) -> List[Dict]:
    schools = data["schools"]
    if block:
        schools = [s for s in schools if (s.get("block") or "").strip().lower() == block.strip().lower()]
    if cluster:
        schools = [s for s in schools if (s.get("cluster") or "").strip().lower() == cluster.strip().lower()]
    if management:
        schools = [s for s in schools if (s.get("school_management") or "").strip().lower() == management.strip().lower()]
    if category:
        schools = [s for s in schools if (s.get("school_category") or "").strip().lower() == category.strip().lower()]
    return schools


@router.post("/import")
async def post_sqaaf_import(file: Optional[UploadFile] = File(None)):
    """
    ETL: Load Pune_District_SQAAF.xlsx (upload or from default path), transform, and push to MongoDB.
    Dashboard will then read from MongoDB. Call this once after placing the Excel file.
    """
    try:
        if file and file.filename and (file.filename.endswith(".xlsx") or file.filename.endswith(".xls")):
            contents = await file.read()
            df = pd.read_excel(io.BytesIO(contents), sheet_name="Sheet1", header=1)
        else:
            path = _get_excel_path()
            df = pd.read_excel(path, sheet_name="Sheet1", header=1)
            path = str(path)
        df.columns = [str(c).strip() for c in df.columns]
        meta_cols, question_cols = _identify_columns(df)
        if not question_cols:
            raise ValueError("No question columns found (expected pattern like 1.1. 1)")
        meta_map = {}
        for c in df.columns:
            if c in question_cols:
                continue
            meta_map[c] = _normalize_meta_name(c)
        df = df.rename(columns=meta_map)
        for q in question_cols:
            df[q] = pd.to_numeric(df[q], errors="coerce")
        if "answered" not in df.columns:
            df["answered"] = df[question_cols].notna().sum(axis=1)
        else:
            ans_col = df["answered"]
            if isinstance(ans_col, pd.DataFrame):
                df["answered"] = df[question_cols].notna().sum(axis=1)
            else:
                df["answered"] = pd.to_numeric(ans_col, errors="coerce").fillna(0).astype(int)
        n_questions = len(question_cols)
        df["Answered_%"] = np.round((df["answered"] / n_questions) * 100, 2)
        df["SQAAF_Score_%"] = np.round((df[question_cols].mean(axis=1) / 4.0) * 100, 2)
        df["Band"] = df["SQAAF_Score_%"].apply(_band)
        section_prefix = re.compile(r"^(\d+\.\d+)")
        section_to_cols = {}
        for q in question_cols:
            m = section_prefix.match(str(q))
            key = m.group(1) if m else "Other"
            section_to_cols.setdefault(key, []).append(q)
        sections_ordered = sorted(section_to_cols.keys(), key=lambda x: (int(x.split(".")[0]), int(x.split(".")[1])))
        for sec in sections_ordered:
            cols = section_to_cols[sec]
            df[f"Section_{sec}_Score_%"] = np.round((df[cols].mean(axis=1) / 4.0) * 100, 2)
        schools = []
        for _, row in df.iterrows():
            rec = {
                "school_code": str(row.get("school_code", "")).strip() if pd.notna(row.get("school_code")) else "",
                "school_name": str(row.get("school_name", "")).strip() if pd.notna(row.get("school_name")) else "",
                "block": str(row.get("block", "")).strip() if pd.notna(row.get("block")) else "",
                "cluster": str(row.get("cluster", "")).strip() if pd.notna(row.get("cluster")) else "",
                "school_management": str(row.get("school_management", "")).strip() if pd.notna(row.get("school_management")) else "",
                "school_category": str(row.get("school_category", "")).strip() if pd.notna(row.get("school_category")) else "",
                "answered": int(row.get("answered", 0)) if pd.notna(row.get("answered")) else 0,
                "Answered_%": float(row.get("Answered_%", 0)),
                "SQAAF_Score_%": float(row.get("SQAAF_Score_%", 0)),
                "Band": str(row.get("Band", "Critical")),
            }
            for sec in sections_ordered:
                rec[f"Section_{sec}_Score_%"] = float(row.get(f"Section_{sec}_Score_%", 0))
            rec["question_scores"] = {q: float(row[q]) for q in question_cols if pd.notna(row.get(q))}
            schools.append(rec)
        n_schools = len(df)
        scores = df["SQAAF_Score_%"].dropna()
        district_mean = float(scores.mean()) if len(scores) else 0
        district_median = float(scores.median()) if len(scores) else 0
        district_std = float(scores.std()) if len(scores) > 1 else 0
        top25 = scores.quantile(0.75)
        bottom25 = scores.quantile(0.25)
        equity_gap = float(top25 - bottom25) if len(scores) >= 4 else 0
        band_counts = df["Band"].value_counts()
        critical_pct = round((band_counts.get("Critical", 0) / n_schools) * 100, 2) if n_schools else 0
        needs_focus_pct = round((band_counts.get("Needs Focus", 0) / n_schools) * 100, 2) if n_schools else 0
        developing_pct = round((band_counts.get("Developing", 0) / n_schools) * 100, 2) if n_schools else 0
        strong_pct = round((band_counts.get("Strong", 0) / n_schools) * 100, 2) if n_schools else 0
        exemplary_pct = round((band_counts.get("Exemplary", 0) / n_schools) * 100, 2) if n_schools else 0
        completion_rate = float(df["Answered_%"].mean()) if n_schools else 0
        full_compliance = int((df["answered"] >= n_questions).sum())
        full_compliance_rate = round((full_compliance / n_schools) * 100, 2) if n_schools else 0
        intervention_load = round((df["SQAAF_Score_%"] < 60).sum() / n_schools * 100, 2) if n_schools else 0
        question_coverage = {q: round((df[q].notna().sum() / n_schools) * 100, 2) for q in question_cols}
        block_agg = df.groupby("block", dropna=False).agg(
            schools=("SQAAF_Score_%", "count"),
            mean=("SQAAF_Score_%", "mean"),
            median=("SQAAF_Score_%", "median"),
            std=("SQAAF_Score_%", "std"),
        ).reset_index()
        block_agg["mean"] = block_agg["mean"].round(2)
        block_agg["median"] = block_agg["median"].round(2)
        block_agg["std"] = block_agg["std"].fillna(0).round(2)
        critical_by_block = df[df["Band"] == "Critical"].groupby("block", dropna=False).size().reindex(block_agg["block"], fill_value=0)
        block_agg["critical_count"] = critical_by_block.values
        block_agg["critical_pct"] = (block_agg["critical_count"] / block_agg["schools"] * 100).round(2)
        pct_below_60_series = df.groupby("block", dropna=False).apply(
            lambda g: (g["SQAAF_Score_%"] < 60).sum() / len(g) * 100 if len(g) else 0
        )
        block_agg["pct_below_60"] = block_agg["block"].map(lambda b: pct_below_60_series.get(b, 0)).fillna(0).values
        block_agg["intervention_index"] = (0.6 * block_agg["pct_below_60"] + 0.4 * block_agg["critical_pct"]).round(2)
        block_agg = block_agg.sort_values("mean", ascending=False).reset_index(drop=True)
        block_gap = round(float(block_agg["mean"].max() - block_agg["mean"].min()), 2) if len(block_agg) else 0
        section_means = {}
        for sec in sections_ordered:
            col = f"Section_{sec}_Score_%"
            section_means[sec] = round(float(df[col].mean()), 2)
        section_summary = []
        for sec in sections_ordered:
            col = f"Section_{sec}_Score_%"
            section_summary.append({
                "section": sec,
                "question_count": len(section_to_cols[sec]),
                "coverage_%": round((df[col].notna().sum() / n_schools) * 100, 2) if n_schools else 0,
                "mean": section_means[sec],
                "median": round(float(df[col].median()), 2),
            })
        mgmt_agg = df.groupby("school_management", dropna=False).agg(
            schools=("SQAAF_Score_%", "count"), mean=("SQAAF_Score_%", "mean"), std=("SQAAF_Score_%", "std"),
        ).reset_index()
        mgmt_agg["mean"] = mgmt_agg["mean"].round(2)
        mgmt_agg["std"] = mgmt_agg["std"].fillna(0).round(2)
        cat_agg = df.groupby("school_category", dropna=False).agg(
            schools=("SQAAF_Score_%", "count"), mean=("SQAAF_Score_%", "mean"), std=("SQAAF_Score_%", "std"),
        ).reset_index()
        cat_agg["mean"] = cat_agg["mean"].round(2)
        cat_agg["std"] = cat_agg["std"].fillna(0).round(2)
        q_means = df[question_cols].mean() / 4.0 * 100
        bottom_questions = q_means.sort_values().head(10).reset_index()
        bottom_questions.columns = ["question", "mean_score_%"]
        bottom_questions["mean_score_%"] = bottom_questions["mean_score_%"].round(2)
        priority_domains = sorted(section_means.items(), key=lambda x: x[1])[:5]
        score_histogram = _histogram_bins(df["SQAAF_Score_%"].dropna(), 5)
        band_distribution = [
            {"band": b, "count": int(band_counts.get(b, 0)), "pct": round((band_counts.get(b, 0) / n_schools) * 100, 2) if n_schools else 0}
            for _, _, b in BANDS
        ]
        data = {
            "n_schools": n_schools, "n_questions": n_questions, "question_columns": question_cols,
            "sections_ordered": sections_ordered, "section_to_cols": section_to_cols,
            "district_mean": round(district_mean, 2), "district_median": round(district_median, 2), "district_std": round(district_std, 2),
            "equity_gap": equity_gap, "critical_pct": critical_pct, "needs_focus_pct": needs_focus_pct,
            "developing_pct": developing_pct, "strong_pct": strong_pct, "exemplary_pct": exemplary_pct,
            "completion_rate": round(completion_rate, 2), "full_compliance_rate": full_compliance_rate,
            "full_compliance_count": full_compliance, "intervention_load": intervention_load,
            "question_coverage": question_coverage, "block_gap": block_gap, "schools": schools,
            "block_summary": block_agg.to_dict("records"), "section_summary": section_summary,
            "section_means": section_means, "management_summary": mgmt_agg.to_dict("records"),
            "category_summary": cat_agg.to_dict("records"), "bottom_questions": bottom_questions.to_dict("records"),
            "priority_domains": [{"section": s, "mean": m} for s, m in priority_domains],
            "score_histogram": score_histogram, "band_distribution": band_distribution,
        }
        source_file = file.filename if file and file.filename else path
        import_id = await _etl_to_mongo(data, source_file=source_file or "Pune_District_SQAAF.xlsx")
        return {"ok": True, "import_id": import_id, "n_schools": n_schools}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


def _no_sqaaf_data_error():
    return HTTPException(
        status_code=404,
        detail="No SQAAF data in MongoDB. Run ETL: POST /api/sqaaf/import with Pune_District_SQAAF.xlsx or place file and call import.",
    )


@router.get("/overview")
async def get_sqaaf_overview(
    block: Optional[str] = Query(None),
    cluster: Optional[str] = Query(None),
    school_management: Optional[str] = Query(None),
    school_category: Optional[str] = Query(None),
):
    """District executive overview KPIs and charts (optionally filtered). Reads from MongoDB."""
    meta = await _get_meta_from_mongo()
    if not meta:
        raise _no_sqaaf_data_error()
    n_questions = meta.get("n_questions", 0)
    schools = await _get_schools_from_mongo(block=block, cluster=cluster, school_management=school_management, school_category=school_category, limit=100000)
    n = len(schools)
    if n == 0:
        return {
            "district_mean": 0, "district_median": 0, "district_std": 0, "equity_gap": 0,
            "critical_pct": 0, "needs_focus_pct": 0, "developing_pct": 0, "strong_pct": 0, "exemplary_pct": 0,
            "completion_rate": 0, "full_compliance_rate": 0, "intervention_load": 0,
            "block_gap": 0, "n_schools": 0,
            "score_histogram": [], "band_distribution": [],
            "top5_blocks": [], "bottom5_blocks": [], "block_gap_display": 0,
        }
    scores = [s["SQAAF_Score_%"] for s in schools]
    bands = [s["Band"] for s in schools]
    from collections import Counter
    band_counts = Counter(bands)
    return {
        "district_mean": round(sum(scores) / n, 2),
        "district_median": round(float(np.median(scores)), 2),
        "district_std": round(float(np.std(scores)), 2) if n > 1 else 0,
        "equity_gap": round(float(np.percentile(scores, 75) - np.percentile(scores, 25)), 2) if n >= 4 else 0,
        "critical_pct": round((band_counts.get("Critical", 0) / n) * 100, 2),
        "needs_focus_pct": round((band_counts.get("Needs Focus", 0) / n) * 100, 2),
        "developing_pct": round((band_counts.get("Developing", 0) / n) * 100, 2),
        "strong_pct": round((band_counts.get("Strong", 0) / n) * 100, 2),
        "exemplary_pct": round((band_counts.get("Exemplary", 0) / n) * 100, 2),
        "completion_rate": round(sum(s["Answered_%"] for s in schools) / n, 2),
        "full_compliance_count": sum(1 for s in schools if s.get("answered", 0) >= n_questions),
        "full_compliance_rate": round(sum(1 for s in schools if s.get("answered", 0) >= n_questions) / n * 100, 2),
        "intervention_load": round(sum(1 for s in schools if s["SQAAF_Score_%"] < 60) / n * 100, 2),
        "n_schools": n,
        "score_histogram": _histogram_bins(pd.Series(scores), 5),
        "band_distribution": [
            {"band": b, "count": band_counts.get(b, 0), "pct": round((band_counts.get(b, 0) / n) * 100, 2)}
            for _, _, b in BANDS
        ],
        "top5_blocks": _block_rank(schools, top=True, n=5),
        "bottom5_blocks": _block_rank(schools, top=False, n=5),
        "block_gap_display": _block_gap_from_schools(schools),
    }


def _block_rank(schools: List[Dict], top: bool, n: int) -> List[Dict]:
    from collections import defaultdict
    by_block = defaultdict(list)
    for s in schools:
        by_block[s.get("block") or "Unknown"].append(s["SQAAF_Score_%"])
    blocks = [(b, np.mean(scores)) for b, scores in by_block.items()]
    blocks.sort(key=lambda x: x[1], reverse=top)
    return [{"block": b, "mean_score": round(m, 2), "school_count": len(by_block[b])} for b, m in blocks[:n]]


def _block_gap_from_schools(schools: List[Dict]) -> float:
    from collections import defaultdict
    by_block = defaultdict(list)
    for s in schools:
        by_block[s.get("block") or "Unknown"].append(s["SQAAF_Score_%"])
    if not by_block:
        return 0
    means = [np.mean(scores) for scores in by_block.values()]
    return round(float(max(means) - min(means)), 2)


@router.get("/block-performance")
async def get_block_performance(
    block: Optional[str] = Query(None),
):
    """Block-level KPIs, ranked bar, boxplot data, heatmap (block x section). Reads from MongoDB."""
    meta = await _get_meta_from_mongo()
    if not meta:
        raise _no_sqaaf_data_error()
    blocks = await _get_blocks_from_mongo(block_filter=block)
    sections = (meta.get("sections_ordered") or [])[:10]
    schools = await _get_schools_from_mongo(block=block, limit=100000)
    # Normalize block names to strings for consistent matching and display
    for b in blocks:
        b["block"] = str(b.get("block") or "").strip() or "Unknown"
    heatmap = []
    for b in blocks[:12]:
        block_name = b.get("block") or "Unknown"
        row_schools = [s for s in schools if (str(s.get("block") or "").strip()) == block_name]
        row = {"block": block_name, "schools": b.get("schools", 0)}
        for sec in sections:
            col = f"Section_{sec}_Score_%"
            vals = [s[col] for s in row_schools if col in s]
            row[sec] = round(float(np.mean(vals)), 2) if vals else 0
        heatmap.append(row)
    boxplot_blocks = [b["block"] for b in blocks[:12]]
    boxplot_data = []
    for bn in boxplot_blocks:
        sc = [s["SQAAF_Score_%"] for s in schools if (str(s.get("block") or "").strip()) == bn]
        med = float(np.median(sc)) if sc else 0.0
        if math.isnan(med) or math.isinf(med):
            med = 0.0
        boxplot_data.append({"block": bn, "scores": sc, "min": min(sc) if sc else 0, "max": max(sc) if sc else 0, "median": round(med, 2)})
    payload = {
        "block_summary": blocks,
        "heatmap": heatmap,
        "heatmap_sections": sections,
        "boxplot_data": boxplot_data,
    }
    return _sanitize_for_json(payload)


@router.get("/section-analysis")
async def get_section_analysis():
    """Section (domain) mean scores, divergence from district mean, summary table. Reads from MongoDB."""
    meta = await _get_meta_from_mongo()
    if not meta:
        raise _no_sqaaf_data_error()
    district_mean = meta.get("district_mean", 0)
    section_summary = meta.get("section_summary", [])
    section_means = meta.get("section_means", {})
    sections_ordered = meta.get("sections_ordered", [])
    divergence = [{"section": s, "mean": section_means.get(s, 0), "gap": round(section_means.get(s, 0) - district_mean, 2)} for s in sections_ordered]
    divergence.sort(key=lambda x: x["mean"])
    return {
        "section_summary": section_summary,
        "section_means_sorted": divergence,
        "district_mean": district_mean,
    }


@router.get("/schools")
async def get_schools(
    block: Optional[str] = Query(None),
    cluster: Optional[str] = Query(None),
    school_management: Optional[str] = Query(None),
    school_category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(500, ge=1, le=10000),
    offset: int = Query(0, ge=0),
):
    """Paginated school list with optional filters and search. Reads from MongoDB."""
    meta = await _get_meta_from_mongo()
    if not meta:
        raise _no_sqaaf_data_error()
    total = await _get_schools_from_mongo(block=block, cluster=cluster, school_management=school_management, school_category=school_category, search=search, limit=0, offset=0, for_count=True)
    page = await _get_schools_from_mongo(block=block, cluster=cluster, school_management=school_management, school_category=school_category, search=search, limit=limit, offset=offset)
    return _sanitize_for_json({"schools": page, "total": total, "limit": limit, "offset": offset})


@router.get("/school-detail/{school_code}")
async def get_school_detail(
    school_code: str,
):
    """Section score profile for one school vs block vs district; lowest 10 questions. Reads from MongoDB."""
    meta = await _get_meta_from_mongo()
    if not meta:
        raise _no_sqaaf_data_error()
    school_code = school_code.strip()
    school_doc = await db.sqaaf_schools.find_one({"school_code": school_code}, {"_id": 0})
    if not school_doc:
        raise HTTPException(status_code=404, detail="School not found")
    block_name = school_doc.get("block") or ""
    block_schools = await _get_schools_from_mongo(block=block_name, limit=5000)
    district_mean = meta.get("district_mean", 0)
    sections_ordered = meta.get("sections_ordered", [])
    section_profile = []
    for sec in sections_ordered:
        col = f"Section_{sec}_Score_%"
        sch_val = school_doc.get(col, 0)
        try:
            sv = float(sch_val)
            if math.isnan(sv) or math.isinf(sv):
                sv = 0.0
        except (TypeError, ValueError):
            sv = 0.0
        bm = float(np.mean([s[col] for s in block_schools if col in s])) if block_schools else 0.0
        if math.isnan(bm) or math.isinf(bm):
            bm = 0.0
        section_profile.append({
            "section": sec,
            "school_score": round(sv, 2),
            "block_mean": round(bm, 2),
            "district_mean": district_mean,
        })
    question_scores = school_doc.get("question_scores") or {}
    q_vals = list(question_scores.items())
    q_vals.sort(key=lambda x: x[1])
    lowest_10 = []
    for q, v in q_vals[:10]:
        try:
            fv = float(v)
            if math.isnan(fv) or math.isinf(fv):
                fv = 0.0
        except (TypeError, ValueError):
            fv = 0.0
        lowest_10.append({"question": q, "score": round(fv, 2), "score_pct": round(fv / 4 * 100, 2)})
    school = {k: v for k, v in school_doc.items() if k != "question_scores"}
    return _sanitize_for_json({
        "school": school,
        "section_profile": section_profile,
        "lowest_10_questions": lowest_10,
    })


@router.get("/intervention")
async def get_intervention(
    block: Optional[str] = Query(None),
):
    """Critical schools list, bottom 10 questions, priority domains, block intervention index. Reads from MongoDB."""
    meta = await _get_meta_from_mongo()
    if not meta:
        raise _no_sqaaf_data_error()
    match = {"Band": "Critical"}
    if block:
        match["block"] = {"$regex": f"^{re.escape(block.strip())}$", "$options": "i"}
    critical = await db.sqaaf_schools.find(match, {"_id": 0}).sort("SQAAF_Score_%", 1).to_list(length=5000)
    critical_schools = [{k: v for k, v in s.items() if k != "question_scores"} for s in critical]
    blocks = await _get_blocks_from_mongo(block_filter=block)
    return _sanitize_for_json({
        "critical_schools": critical_schools,
        "bottom_questions": meta.get("bottom_questions", []),
        "priority_domains": meta.get("priority_domains", []),
        "block_intervention_index": [{"block": b.get("block", ""), "intervention_index": b.get("intervention_index", 0), "critical_pct": b.get("critical_pct", 0), "pct_below_60": b.get("pct_below_60", 0), "schools": b.get("schools", 0)} for b in blocks],
    })


@router.get("/question-coverage")
async def get_question_coverage():
    """Coverage % per question (non-null / total schools). Reads from MongoDB."""
    meta = await _get_meta_from_mongo()
    if not meta:
        raise _no_sqaaf_data_error()
    return {"question_coverage": meta.get("question_coverage", {}), "n_schools": meta.get("n_schools", 0)}


@router.get("/management-category")
async def get_management_category():
    """Mean score by School Management and School Category. Reads from MongoDB."""
    meta = await _get_meta_from_mongo()
    if not meta:
        raise _no_sqaaf_data_error()
    return {
        "management_summary": meta.get("management_summary", []),
        "category_summary": meta.get("category_summary", []),
    }
