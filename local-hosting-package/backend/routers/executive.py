"""Executive Dashboard Router"""
from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timezone
from typing import List, Optional
from utils.scope import build_scope_match, prepend_match

router = APIRouter(prefix="/executive", tags=["Executive Dashboard"])

# Maharashtra district name -> code (used as fallback for map drilldowns)
MAHA_DISTRICT_CODES = {
    "AHMADNAGAR": "2701",
    "AKOLA": "2702",
    "AMRAVATI": "2703",
    "AURANGABAD": "2704",
    "BEED": "2705",
    "BHANDARA": "2706",
    "BULDHANA": "2707",
    "CHANDRAPUR": "2708",
    "DHULE": "2709",
    "GADCHIROLI": "2710",
    "GONDIA": "2711",
    "HINGOLI": "2712",
    "JALGAON": "2713",
    "JALNA": "2714",
    "KOLHAPUR": "2715",
    "LATUR": "2716",
    "MUMBAI CITY": "2717",
    "MUMBAI SUBURBAN": "2718",
    "NAGPUR": "2719",
    "NANDED": "2720",
    "NANDURBAR": "2721",
    "NASHIK": "2722",
    "OSMANABAD": "2723",
    "PALGHAR": "2724",
    "PUNE": "2725",
    "RAIGAD": "2726",
    "RATNAGIRI": "2727",
    "SANGLI": "2728",
    "SATARA": "2729",
    "SINDHUDURG": "2730",
    "SOLAPUR": "2731",
    "THANE": "2732",
    "WARDHA": "2733",
    "WASHIM": "2734",
    "YAVATMAL": "2735",
    "PARBHANI": "2736",
}

# Database will be injected
db = None

def init_db(database):
    global db
    db = database

@router.get("/student-identity")
async def get_student_identity_compliance(
    district_code: Optional[str] = Query(None),
    block_code: Optional[str] = Query(None),
    udise_code: Optional[str] = Query(None),
    district_name: Optional[str] = Query(None),
    block_name: Optional[str] = Query(None),
):
    """Get Student Identity & Compliance KPIs from Aadhaar and APAAR data"""
    dn = (district_name.strip().upper() or None) if (district_name and isinstance(district_name, str)) else None
    bn = (block_name.strip().upper() or None) if (block_name and isinstance(block_name, str)) else None
    scope_match = build_scope_match(district_code=district_code, block_code=block_code, udise_code=udise_code, district_name=dn, block_name=bn)
    
    # Get Aadhaar data - use correct field names from ETL
    aadhaar_pipeline = prepend_match([
        {"$group": {
            "_id": None,
            "total_schools": {"$sum": 1},
            "total_students": {"$sum": "$total_enrolment"},
            "aadhaar_available": {"$sum": "$aadhaar_passed"},
            "aadhaar_failed": {"$sum": "$aadhaar_failed"},
            "name_match": {"$sum": "$name_match"},
            "mbu_pending": {"$sum": {"$add": ["$mbu_pending_5_15", "$mbu_pending_15_above"]}},
            "exception_count": {"$sum": {"$multiply": ["$exception_rate", "$total_enrolment"]}}
        }}
    ], scope_match)
    aadhaar_cursor = db.aadhaar_analytics.aggregate(aadhaar_pipeline)
    aadhaar_data = await aadhaar_cursor.to_list(length=1)
    
    # Get APAAR data
    apaar_pipeline = prepend_match([
        {"$group": {
            "_id": None,
            "total_students": {"$sum": "$total_student"},
            "apaar_generated": {"$sum": "$total_generated"},
            "apaar_pending": {"$sum": {"$subtract": ["$total_student", "$total_generated"]}},
            "apaar_not_applied": {"$sum": "$total_not_applied"},
            "apaar_failed": {"$sum": "$total_failed"}
        }}
    ], scope_match)
    apaar_cursor = db.apaar_analytics.aggregate(apaar_pipeline)
    apaar_data = await apaar_cursor.to_list(length=1)
    
    # Get block-wise identity compliance - use correct field names
    block_pipeline = prepend_match([
        {"$group": {
            "_id": {"block_code": "$block_code", "block_name": "$block_name"},
            "block_code": {"$first": "$block_code"},
            "total_students": {"$sum": "$total_enrolment"},
            "aadhaar_available": {"$sum": "$aadhaar_passed"},
            "name_match": {"$sum": "$name_match"}
        }},
        {"$project": {
            "_id": 0,
            "block_code": "$_id.block_code",
            "block_name": "$_id.block_name",
            "total_students": 1,
            "aadhaar_pct": {"$round": [{"$multiply": [{"$divide": ["$aadhaar_available", {"$max": ["$total_students", 1]}]}, 100]}, 1]},
            "name_mismatch_pct": {"$round": [{"$multiply": [{"$divide": [{"$subtract": ["$total_students", "$name_match"]}, {"$max": ["$total_students", 1]}]}, 100]}, 1]}
        }},
        {"$sort": {"aadhaar_pct": -1}}
    ], scope_match)
    block_cursor = db.aadhaar_analytics.aggregate(block_pipeline)
    block_data = await block_cursor.to_list(length=30)
    
    if not aadhaar_data:
        aadhaar_data = [{"total_schools": 0, "total_students": 0, "aadhaar_available": 0, "aadhaar_failed": 0, "name_match": 0, "mbu_pending": 0, "exception_count": 0}]
    if not apaar_data:
        apaar_data = [{"total_students": 0, "apaar_generated": 0, "apaar_pending": 0, "apaar_not_applied": 0, "apaar_failed": 0}]
    
    a = aadhaar_data[0]
    p = apaar_data[0]
    
    total_students = a.get("total_students", 0) or 0
    aadhaar_available = a.get("aadhaar_available", 0) or 0
    apaar_generated = p.get("apaar_generated", 0) or 0
    name_match = a.get("name_match", 0) or 0
    name_mismatch = total_students - name_match if total_students > name_match else 0
    
    # Calculate compliance metrics
    aadhaar_coverage = round(aadhaar_available / total_students * 100, 1) if total_students > 0 else 0
    apaar_coverage = round(apaar_generated / p.get("total_students", 1) * 100, 1) if p.get("total_students", 0) > 0 else 0
    name_mismatch_rate = round(name_mismatch / total_students * 100, 2) if total_students > 0 else 0
    exception_rate = round(a.get("exception_count", 0) / total_students * 100, 2) if total_students > 0 else 0
    
    # Identity Compliance Index = (Aadhaar% * 0.4 + APAAR% * 0.4 + (100 - NameMismatch%) * 0.2)
    identity_compliance_index = round(aadhaar_coverage * 0.4 + apaar_coverage * 0.4 + (100 - name_mismatch_rate) * 0.2, 1)
    
    return {
        "summary": {
            "total_schools": a.get("total_schools", 0),
            "total_students": total_students,
            "aadhaar_coverage": aadhaar_coverage,
            "apaar_coverage": apaar_coverage,
            "identity_compliance_index": identity_compliance_index
        },
        "aadhaar_metrics": {
            "aadhaar_available": aadhaar_available,
            "aadhaar_coverage_pct": aadhaar_coverage,
            "name_mismatch_count": name_mismatch,
            "name_mismatch_rate": name_mismatch_rate,
            "mbu_pending": a.get("mbu_pending", 0),
            "exception_count": int(a.get("exception_count", 0) or 0),
            "exception_rate": exception_rate
        },
        "apaar_metrics": {
            "total_students": p.get("total_students", 0),
            "apaar_generated": apaar_generated,
            "apaar_coverage_pct": apaar_coverage,
            "apaar_pending": p.get("apaar_pending", 0),
            "apaar_not_applied": p.get("apaar_not_applied", 0),
            "apaar_failed": p.get("apaar_failed", 0)
        },
        "compliance_breakdown": [
            {"metric": "Aadhaar Coverage", "value": aadhaar_coverage, "target": 100, "color": "#10b981" if aadhaar_coverage >= 90 else "#f59e0b"},
            {"metric": "APAAR Generation", "value": apaar_coverage, "target": 100, "color": "#10b981" if apaar_coverage >= 85 else "#f59e0b"},
            {"metric": "Name Match Rate", "value": round(100 - name_mismatch_rate, 1), "target": 100, "color": "#10b981" if name_mismatch_rate < 5 else "#ef4444"},
            {"metric": "Data Quality", "value": round(100 - exception_rate, 1), "target": 100, "color": "#10b981" if exception_rate < 10 else "#f59e0b"}
        ],
        "block_performance": [
            {
                "block_code": b.get("block_code", ""),
                "block_name": b.get("block_name", ""),
                "aadhaar_pct": round(b.get("aadhaar_pct", 0) or 0, 1),
                "name_mismatch_pct": round(b.get("name_mismatch_pct", 0) or 0, 2),
            }
            for b in block_data
        ]
    }


@router.get("/infrastructure-facilities")
async def get_infrastructure_facilities(
    district_code: Optional[str] = Query(None),
    block_code: Optional[str] = Query(None),
    udise_code: Optional[str] = Query(None),
    district_name: Optional[str] = Query(None),
    block_name: Optional[str] = Query(None),
):
    """Get Infrastructure & Facilities KPIs from Classrooms/Toilets and Infrastructure data"""
    dn = (district_name.strip().upper() or None) if (district_name and isinstance(district_name, str)) else None
    bn = (block_name.strip().upper() or None) if (block_name and isinstance(block_name, str)) else None
    scope_match = build_scope_match(district_code=district_code, block_code=block_code, udise_code=udise_code, district_name=dn, block_name=bn)
    
    # Get Classrooms & Toilets data
    ct_pipeline = prepend_match([
        {"$group": {
            "_id": None,
            "total_schools": {"$sum": 1},
            "total_classrooms": {"$sum": "$classrooms_instructional"},
            "good_classrooms": {"$sum": {"$add": ["$pucca_good", "$part_pucca_good"]}},
            "repair_needed": {"$sum": {"$add": ["$pucca_minor", "$pucca_major", "$part_pucca_minor", "$part_pucca_major"]}},
            "total_toilets": {"$sum": {"$add": ["$boys_toilets_total", "$girls_toilets_total"]}},
            "functional_toilets": {"$sum": {"$add": ["$boys_toilets_functional", "$girls_toilets_functional"]}},
            "toilets_with_water": {"$sum": {"$add": ["$boys_toilets_functional", "$girls_toilets_functional"]}},
            "handwash_points": {"$sum": "$handwash_points"},
            "schools_with_electricity": {"$sum": {"$cond": [{"$or": [{"$eq": ["$electricity", 1]}, {"$eq": ["$electricity", "1"]}, {"$gt": ["$electricity", 0]}]}, 1, 0]}},
            "schools_with_library": {"$sum": {"$cond": [{"$gt": ["$library_available", 0]}, 1, 0]}},
            "computer_labs": {"$sum": "$computer_labs"}
        }}
    ], scope_match)
    ct_cursor = db.classrooms_toilets.aggregate(ct_pipeline)
    ct_data = await ct_cursor.to_list(length=1)
    
    # Get Infrastructure analytics
    infra_pipeline = prepend_match([
        {"$group": {
            "_id": None,
            "total_schools": {"$sum": 1},
            "tap_water": {"$sum": {"$cond": [{"$or": [{"$eq": ["$tap_water", "yes"]}, {"$eq": ["$tap_water", 1]}, {"$gt": [{"$ifNull": ["$tap_water", 0]}, 0]}]}, 1, 0]}},
            "purified_water": {"$sum": {"$cond": [{"$or": [{"$eq": ["$water_purification", "yes"]}, {"$eq": ["$water_purifier", 1]}, {"$gt": [{"$ifNull": ["$water_purifier", 0]}, 0]}]}, 1, 0]}},
            "water_tested": {"$sum": {"$cond": [{"$or": [{"$eq": ["$water_testing", "yes"]}, {"$eq": ["$water_quality_tested", 1]}, {"$gt": [{"$ifNull": ["$water_quality_tested", 0]}, 0]}]}, 1, 0]}},
            "rainwater_harvest": {"$sum": {"$cond": [{"$or": [{"$eq": ["$rainwater_harvesting", "yes"]}, {"$and": [{"$ne": ["$rainwater_harvesting", "no"]}, {"$ne": ["$rainwater_harvesting", None]}, {"$ne": ["$rainwater_harvesting", ""]}]}, {"$gt": [{"$ifNull": ["$rain_water_harvesting", 0]}, 0]}]}, 1, 0]}},
            "ramp_available": {"$sum": {"$cond": [{"$eq": ["$ramp", True]}, 1, 0]}},
            "medical_checkup": {"$sum": {"$cond": [{"$eq": ["$medical_checkup", True]}, 1, 0]}},
            "first_aid": {"$sum": {"$cond": [{"$eq": ["$first_aid", True]}, 1, 0]}}
        }}
    ], scope_match)
    infra_cursor = db.infrastructure_analytics.aggregate(infra_pipeline)
    infra_data = await infra_cursor.to_list(length=1)
    
    # Block-wise infrastructure
    block_pipeline = prepend_match([
        {"$group": {
            "_id": {"block_code": "$block_code", "block_name": "$block_name"},
            "schools": {"$sum": 1},
            "classrooms": {"$sum": "$classrooms_instructional"},
            "good_classrooms": {"$sum": {"$add": ["$pucca_good", "$part_pucca_good"]}},
            "toilets": {"$sum": {"$add": ["$boys_toilets_total", "$girls_toilets_total"]}},
            "functional_toilets": {"$sum": {"$add": ["$boys_toilets_functional", "$girls_toilets_functional"]}}
        }},
        {"$project": {
            "_id": 0,
            "block_code": "$_id.block_code",
            "block_name": "$_id.block_name",
            "schools": 1,
            "classroom_health": {"$multiply": [{"$divide": ["$good_classrooms", {"$max": ["$classrooms", 1]}]}, 100]},
            "toilet_functional_pct": {"$multiply": [{"$divide": ["$functional_toilets", {"$max": ["$toilets", 1]}]}, 100]}
        }},
        {"$sort": {"classroom_health": -1}}
    ], scope_match)
    block_cursor = db.classrooms_toilets.aggregate(block_pipeline)
    block_data = await block_cursor.to_list(length=30)
    
    if not ct_data:
        ct_data = [{}]
    if not infra_data:
        infra_data = [{}]
    
    ct = ct_data[0]
    inf = infra_data[0]
    
    total_schools = ct.get("total_schools", 0) or inf.get("total_schools", 0)
    total_classrooms = ct.get("total_classrooms", 0)
    good_classrooms = ct.get("good_classrooms", 0)
    total_toilets = ct.get("total_toilets", 0)
    functional_toilets = ct.get("functional_toilets", 0)
    toilets_with_water = ct.get("toilets_with_water", 0)
    
    # Calculate KPIs
    classroom_health = round(good_classrooms / total_classrooms * 100, 1) if total_classrooms > 0 else 0
    toilet_functional = round(functional_toilets / total_toilets * 100, 1) if total_toilets > 0 else 0
    water_availability = round(toilets_with_water / functional_toilets * 100, 1) if functional_toilets > 0 else 0
    electricity_pct = round(ct.get("schools_with_electricity", 0) / total_schools * 100, 1) if total_schools > 0 else 0
    
    # Water safety metrics - use total_schools from infrastructure_analytics or fallback to classrooms_toilets
    infra_total_schools = inf.get("total_schools", 0) or total_schools or 1
    tap_water_pct = round(inf.get("tap_water", 0) / infra_total_schools * 100, 1) if infra_total_schools > 0 else 0
    purified_water_pct = round(inf.get("purified_water", 0) / infra_total_schools * 100, 1) if infra_total_schools > 0 else 0
    water_tested_pct = round(inf.get("water_tested", 0) / infra_total_schools * 100, 1) if infra_total_schools > 0 else 0
    
    # Infrastructure Readiness Index = (Classroom Health * 0.3 + Toilet Functional * 0.25 + Water * 0.25 + Electricity * 0.2)
    infrastructure_index = round(classroom_health * 0.3 + toilet_functional * 0.25 + water_availability * 0.25 + electricity_pct * 0.2, 1)
    
    return {
        "summary": {
            "total_schools": total_schools,
            "total_classrooms": total_classrooms,
            "total_toilets": total_toilets,
            "infrastructure_index": infrastructure_index
        },
        "classroom_metrics": {
            "total_classrooms": total_classrooms,
            "avg_per_school": round(total_classrooms / total_schools, 1) if total_schools > 0 else 0,
            "good_condition": good_classrooms,
            "repair_needed": ct.get("repair_needed", 0),
            "classroom_health_pct": classroom_health
        },
        "toilet_metrics": {
            "total_toilets": total_toilets,
            "functional_toilets": functional_toilets,
            "functional_pct": toilet_functional,
            "with_water": toilets_with_water,
            "water_coverage_pct": water_availability,
            "handwash_points": ct.get("handwash_points", 0)
        },
        "facility_metrics": {
            "electricity_pct": electricity_pct,
            "library_pct": round(ct.get("schools_with_library", 0) / total_schools * 100, 1) if total_schools > 0 else 0,
            "computer_labs": ct.get("computer_labs", 0),
            "ramp_pct": round(inf.get("ramp_available", 0) / inf.get("total_schools", 1) * 100, 1)
        },
        "water_safety": {
            "tap_water_pct": tap_water_pct,
            "purified_water_pct": purified_water_pct,
            "water_tested_pct": water_tested_pct,
            "rainwater_harvest_pct": round(inf.get("rainwater_harvest", 0) / infra_total_schools * 100, 1) if infra_total_schools > 0 else 0
        },
        "health_safety": {
            "medical_checkup_pct": round(inf.get("medical_checkup", 0) / inf.get("total_schools", 1) * 100, 1),
            "first_aid_pct": round(inf.get("first_aid", 0) / inf.get("total_schools", 1) * 100, 1)
        },
        "index_breakdown": [
            {"metric": "Classroom Health", "value": classroom_health, "weight": 30, "color": "#10b981" if classroom_health >= 90 else "#f59e0b"},
            {"metric": "Toilet Functional", "value": toilet_functional, "weight": 25, "color": "#10b981" if toilet_functional >= 95 else "#f59e0b"},
            {"metric": "Water Availability", "value": water_availability, "weight": 25, "color": "#3b82f6" if water_availability >= 90 else "#f59e0b"},
            {"metric": "Electricity", "value": electricity_pct, "weight": 20, "color": "#8b5cf6" if electricity_pct >= 95 else "#f59e0b"}
        ],
        "block_performance": [
            {
                "block_code": b.get("block_code", ""),
                "block_name": b.get("block_name", ""),
                "classroom_health": round(b.get("classroom_health", 0) or 0, 1),
                "toilet_pct": round(b.get("toilet_functional_pct", 0) or 0, 1),
            }
            for b in block_data
        ]
    }


@router.get("/teacher-staffing")
async def get_teacher_staffing(
    district_code: Optional[str] = Query(None),
    block_code: Optional[str] = Query(None),
    udise_code: Optional[str] = Query(None),
    district_name: Optional[str] = Query(None),
    block_name: Optional[str] = Query(None),
    debug: Optional[bool] = Query(None, description="Include sample docs with age/numeric_age/effective_age"),
):
    """Get Teacher & Staffing Analytics KPIs. Matches scope by district/block code or name."""
    # Normalize names to uppercase for match (many collections store "PUNE" not "Pune")
    dn = (district_name.strip().upper() or None) if (district_name and isinstance(district_name, str)) else None
    bn = (block_name.strip().upper() or None) if (block_name and isinstance(block_name, str)) else None
    scope_match = build_scope_match(
        district_code=district_code,
        block_code=block_code,
        udise_code=udise_code,
        district_name=dn,
        block_name=bn,
    )
    current_year = datetime.now().year

    # Compute age and service_years from dob/doj when stored values are missing or zero (CT Teacher may store 0 if DOB/DoJ columns missing or parse failed)
    # Use $convert with onError: 0 so empty string or invalid values do not break aggregation
    # Coerce age to int so "58" (string from Excel) is treated as 58 for retirement risk (55+)
    dob_str = {"$ifNull": ["$dob", ""]}
    doj_str = {"$ifNull": ["$doj_service", ""]}
    safe_int = lambda expr: {"$convert": {"input": expr, "to": "int", "onError": 0, "onNull": 0}}
    numeric_age_expr = safe_int({"$ifNull": ["$age", 0]})
    ct_add_fields = {
        "$addFields": {
            "numeric_age": numeric_age_expr,
            "birth_year": {
                "$let": {
                    "vars": {
                        "by_slash": {"$split": [dob_str, "/"]},
                        "by_dash": {"$split": [dob_str, "-"]}
                    },
                    "in": {"$cond": {
                        "if": {"$gte": [{"$size": "$$by_slash"}, 3]},
                        "then": safe_int({"$arrayElemAt": ["$$by_slash", 2]}),
                        "else": {"$cond": {
                            "if": {"$gte": [{"$size": "$$by_dash"}, 1]},
                            "then": safe_int({"$arrayElemAt": ["$$by_dash", 0]}),
                            "else": 0
                        }}
                    }}
                }
            },
            "doj_year": {
                "$let": {
                    "vars": {
                        "by_slash": {"$split": [doj_str, "/"]},
                        "by_dash": {"$split": [doj_str, "-"]}
                    },
                    "in": {"$cond": {
                        "if": {"$gte": [{"$size": "$$by_slash"}, 3]},
                        "then": safe_int({"$arrayElemAt": ["$$by_slash", 2]}),
                        "else": {"$cond": {
                            "if": {"$gte": [{"$size": "$$by_dash"}, 1]},
                            "then": safe_int({"$arrayElemAt": ["$$by_dash", 0]}),
                            "else": 0
                        }}
                    }}
                }
            }
        }
    }
    # Second $addFields so effective_age/effective_service_years can reference numeric_age, birth_year, doj_year
    ct_add_fields_2 = {
        "$addFields": {
            "effective_age": {
                "$cond": {
                    "if": {"$and": [{"$gte": ["$numeric_age", 18]}, {"$lte": ["$numeric_age", 75]}]},
                    "then": "$numeric_age",
                    "else": {"$cond": {"if": {"$gt": ["$birth_year", 0]}, "then": {"$subtract": [current_year, "$birth_year"]}, "else": 0}}
                }
            },
            "effective_service_years": {
                "$cond": {
                    "if": {"$and": [{"$gte": [{"$ifNull": ["$service_years", 0]}, 0]}, {"$lte": [{"$ifNull": ["$service_years", 0]}, 45]}]},
                    "then": "$service_years",
                    "else": {"$cond": {"if": {"$and": [{"$gt": ["$doj_year", 1950]}, {"$lte": ["$doj_year", current_year]}]}, "then": {"$subtract": [current_year, "$doj_year"]}, "else": 0}}
                }
            }
        }
    }

    # Get CTTeacher data - data uses integers: 1=Yes, 2=No
    # Use teacher_code (not teacher_id) to match CTTeacher dashboard
    ct_pipeline = prepend_match([
        ct_add_fields,
        ct_add_fields_2,
        {"$group": {
            "_id": None,
            "total_records": {"$sum": 1},
            "unique_teachers": {"$addToSet": "$teacher_code"},
            "total_schools": {"$addToSet": "$udise_code"},
            "aadhaar_verified": {"$sum": {"$cond": [{"$or": [
                {"$eq": ["$aadhaar_verified", "Verified From UIDAI against Name,Gender & DOB"]},
                {"$eq": ["$aadhaar_verified", 1]},
                {"$and": [
                    {"$regexMatch": {"input": {"$ifNull": [{"$toString": "$aadhaar_verified"}, ""]}, "regex": "verified", "options": "i"}},
                    {"$not": {"$regexMatch": {"input": {"$ifNull": [{"$toString": "$aadhaar_verified"}, ""]}, "regex": "not verified|unverified|pending", "options": "i"}}}
                ]}
            ]}, 1, 0]}},
            "ctet_qualified": {"$sum": {"$cond": [{"$eq": ["$ctet_qualified", 1]}, 1, 0]}},
            "nishtha_completed": {"$sum": {"$cond": [{"$eq": ["$training_nishtha", 1]}, 1, 0]}},
            "female_count": {"$sum": {"$cond": [{"$or": [{"$eq": ["$gender", "2-Female"]}, {"$eq": ["$gender", "Female"]}, {"$regexMatch": {"input": {"$toString": "$gender"}, "regex": "Female|2-"}}]}, 1, 0]}},
            "male_count": {"$sum": {"$cond": [{"$or": [{"$eq": ["$gender", "1-Male"]}, {"$eq": ["$gender", "Male"]}, {"$regexMatch": {"input": {"$toString": "$gender"}, "regex": "Male|1-"}}]}, 1, 0]}},
            "retirement_risk": {"$sum": {"$cond": [{"$gte": ["$effective_age", 55]}, 1, 0]}},
            "total_age": {"$sum": "$effective_age"},
            "total_service_years": {"$sum": "$effective_service_years"},
            "records_with_service_years": {"$sum": {"$cond": [{"$gt": ["$effective_service_years", 0]}, 1, 0]}}
        }}
    ], scope_match)
    ct_cursor = db.ctteacher_analytics.aggregate(ct_pipeline)
    ct_data = await ct_cursor.to_list(length=1)
    
    # Optional: run a sample pipeline to verify age/numeric_age/effective_age (for debugging retirement_risk)
    sample_pipeline = prepend_match([
        ct_add_fields,
        ct_add_fields_2,
        {"$project": {"teacher_code": 1, "age": 1, "numeric_age": 1, "birth_year": 1, "effective_age": 1}},
        {"$limit": 5}
    ], scope_match)
    try:
        sample_cursor = db.ctteacher_analytics.aggregate(sample_pipeline)
        sample_docs = await sample_cursor.to_list(length=5)
    except Exception:
        sample_docs = []
    
    # Get Teacher analytics for comparison
    teacher_pipeline = prepend_match([
        {"$group": {
            "_id": None,
            "total_schools": {"$sum": 1},
            "teachers_cy": {"$sum": "$teacher_tot_cy"},
            "teachers_py": {"$sum": "$teacher_tot_py"},
            "ctet_cy": {"$sum": "$tot_teacher_tr_ctet_cy"},
            "cwsn_trained": {"$sum": "$tot_teacher_tr_cwsn_cy"},
            "computer_trained": {"$sum": "$tot_teacher_tr_computers_cy"}
        }}
    ], scope_match)
    teacher_cursor = db.teacher_analytics.aggregate(teacher_pipeline)
    teacher_data = await teacher_cursor.to_list(length=1)
    
    # Block-wise teacher distribution
    block_pipeline = prepend_match([
        {"$group": {
            "_id": {"block_code": "$block_code", "block_name": "$block_name"},
            "teachers": {"$sum": 1},
            "ctet": {"$sum": {"$cond": [{"$eq": ["$ctet_qualified", 1]}, 1, 0]}},
            "nishtha": {"$sum": {"$cond": [{"$eq": ["$training_nishtha", 1]}, 1, 0]}}
        }},
        {"$project": {
            "_id": 0,
            "block_code": "$_id.block_code",
            "block_name": "$_id.block_name",
            "teachers": 1,
            "ctet_pct": {"$multiply": [{"$divide": ["$ctet", {"$max": ["$teachers", 1]}]}, 100]},
            "nishtha_pct": {"$multiply": [{"$divide": ["$nishtha", {"$max": ["$teachers", 1]}]}, 100]}
        }},
        {"$sort": {"ctet_pct": -1}}
    ], scope_match)
    block_cursor = db.ctteacher_analytics.aggregate(block_pipeline)
    block_data = await block_cursor.to_list(length=30)
    
    if not ct_data:
        ct_data = [{}]
    if not teacher_data:
        teacher_data = [{}]
    
    ct = ct_data[0]
    t = teacher_data[0]
    
    total_records = ct.get("total_records", 0)
    unique_teachers_list = ct.get("unique_teachers", [])
    unique_teachers = len(unique_teachers_list) if unique_teachers_list else 0
    total_schools = len(ct.get("total_schools", [])) if ct.get("total_schools") else 0
    
    # Use teachers_cy from teacher_analytics to match Teacher Dashboard "Total Teachers (CY)"
    # This ensures consistency across dashboards
    teachers_cy = t.get("teachers_cy", 0) or 0
    teachers_py = t.get("teachers_py", 0) or 0
    
    # Use teachers_cy as primary count to match Teacher Dashboard
    # Fallback to unique_teachers if teacher_analytics doesn't have data
    total_teachers = teachers_cy if teachers_cy > 0 else (unique_teachers if unique_teachers > 0 else total_records)
    
    # Calculate KPIs using total_records for percentages (matching CTTeacher dashboard logic)
    aadhaar_verified_pct = round(ct.get("aadhaar_verified", 0) / total_records * 100, 1) if total_records > 0 else 0
    ctet_pct = round(ct.get("ctet_qualified", 0) / total_records * 100, 1) if total_records > 0 else 0
    nishtha_pct = round(ct.get("nishtha_completed", 0) / total_records * 100, 1) if total_records > 0 else 0
    female_pct = round(ct.get("female_count", 0) / total_records * 100, 1) if total_records > 0 else 0
    
    # Calculate retirement risk: Teachers aged 55+ (retirement age in India is typically 58-60, but 55+ indicates high risk)
    retirement_risk_count = ct.get("retirement_risk", 0)
    retirement_risk_pct = round(retirement_risk_count / total_records * 100, 1) if total_records > 0 else 0
    
    # Calculate average service years from aggregated data (use count of records with valid service years when available)
    total_service_years = ct.get("total_service_years", 0)
    records_with_service = ct.get("records_with_service_years", 0) or 0
    denom = records_with_service if records_with_service > 0 else total_records
    avg_service_years = round(total_service_years / denom, 1) if denom > 0 else 0
    
    # Teacher growth (teachers_cy and teachers_py already calculated above)
    growth_rate = round((teachers_cy - teachers_py) / teachers_py * 100, 1) if teachers_py > 0 else 0
    
    # Teacher Quality Index = (CTET * 0.4 + NISHTHA * 0.3 + Aadhaar Verified * 0.3)
    teacher_quality_index = round(ctet_pct * 0.4 + nishtha_pct * 0.3 + aadhaar_verified_pct * 0.3, 1)
    
    # Professional Qualification Distribution (run after total_records is calculated)
    prof_qual_pipeline = prepend_match([
        {"$group": {
            "_id": "$professional_qualification",
            "count": {"$sum": 1}
        }},
        {"$project": {
            "_id": 0,
            "qualification": "$_id",
            "count": 1
        }},
        {"$sort": {"count": -1}}
    ], scope_match)
    prof_qual_cursor = db.ctteacher_analytics.aggregate(prof_qual_pipeline)
    prof_qual_data = await prof_qual_cursor.to_list(length=20)
    # Calculate percentages manually after getting total_records
    for item in prof_qual_data:
        item["percentage"] = round(item["count"] / total_records * 100, 1) if total_records > 0 else 0
    
    # Academic Qualification Distribution (run after total_records is calculated)
    acad_qual_pipeline = prepend_match([
        {"$group": {
            "_id": "$academic_qualification",
            "count": {"$sum": 1}
        }},
        {"$project": {
            "_id": 0,
            "qualification": "$_id",
            "count": 1
        }},
        {"$sort": {"count": -1}}
    ], scope_match)
    acad_qual_cursor = db.ctteacher_analytics.aggregate(acad_qual_pipeline)
    acad_qual_data = await acad_qual_cursor.to_list(length=20)
    # Calculate percentages manually after getting total_records
    for item in acad_qual_data:
        item["percentage"] = round(item["count"] / total_records * 100, 1) if total_records > 0 else 0
    
    # Calculate summary KPIs for qualifications
    b_ed_or_higher_count = sum(item["count"] for item in prof_qual_data if item.get("qualification") and ("B.Ed" in str(item["qualification"]) or "M.Ed" in str(item["qualification"])))
    post_graduate_count = sum(item["count"] for item in acad_qual_data if item.get("qualification") and ("Post graduate" in str(item["qualification"]) or "M.Phil" in str(item["qualification"]) or "Ph.D" in str(item["qualification"]) or "Post Doctoral" in str(item["qualification"])))
    
    # Count schools by number of teachers (0, 1, 2 teachers)
    school_teacher_count_pipeline = prepend_match([
        {"$group": {
            "_id": "$udise_code",
            "teacher_count": {"$sum": 1}
        }},
        {"$group": {
            "_id": "$teacher_count",
            "school_count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ], scope_match)
    school_teacher_cursor = db.ctteacher_analytics.aggregate(school_teacher_count_pipeline)
    school_teacher_data = await school_teacher_cursor.to_list(length=100)
    
    # Initialize counts
    one_teacher_schools = 0
    two_teacher_schools = 0
    
    # Process the aggregated data
    for item in school_teacher_data:
        teacher_count = item.get("_id", 0)
        school_count = item.get("school_count", 0)
        if teacher_count == 1:
            one_teacher_schools = school_count
        elif teacher_count == 2:
            two_teacher_schools = school_count
    
    # Count schools with zero teachers (schools not in ctteacher_analytics)
    # Get all unique schools from ctteacher_analytics
    schools_query = scope_match if scope_match else {}
    schools_with_teachers_list = await db.ctteacher_analytics.distinct("udise_code", schools_query)
    schools_with_teachers_count = len(schools_with_teachers_list) if schools_with_teachers_list else 0
    
    # Get total schools in scope - prefer infrastructure_analytics; if empty, use ctteacher_analytics so teacher stats still show
    total_schools_pipeline = prepend_match([
        {"$group": {
            "_id": None,
            "total_schools": {"$addToSet": "$udise_code"}
        }}
    ], scope_match)
    total_schools_cursor = db.infrastructure_analytics.aggregate(total_schools_pipeline)
    total_schools_data = await total_schools_cursor.to_list(length=1)
    total_schools_all = len(total_schools_data[0].get("total_schools", [])) if total_schools_data and total_schools_data[0] else None
    if total_schools_all is None:
        total_schools_all = max(total_schools, schools_with_teachers_count)
    
    # Schools with zero teachers = total schools - schools with at least 1 teacher
    zero_teacher_schools = max(0, total_schools_all - schools_with_teachers_count)
    
    out = {
        "summary": {
            "total_teachers": total_teachers,  # Use unique_teachers count (or total_records if unique is 0)
            "unique_teachers": unique_teachers,
            "total_records": total_records,  # Add total_records for reference
            "total_schools": total_schools,
            "avg_per_school": round(total_records / total_schools, 1) if total_schools > 0 else 0,  # Use total_records for avg calculation
            "teacher_quality_index": teacher_quality_index
        },
        "compliance_metrics": {
            "aadhaar_verified": ct.get("aadhaar_verified", 0),
            "aadhaar_verified_pct": aadhaar_verified_pct,
            "ctet_qualified": ct.get("ctet_qualified", 0),
            "ctet_pct": ctet_pct,
            "nishtha_completed": ct.get("nishtha_completed", 0),
            "nishtha_pct": nishtha_pct
        },
        "demographic_metrics": {
            "female_count": ct.get("female_count", 0),
            "male_count": ct.get("male_count", 0),
            "female_pct": female_pct,
            "gender_parity_index": round(ct.get("female_count", 0) / ct.get("male_count", 1), 2) if ct.get("male_count", 0) > 0 else 0,
            "avg_service_years": avg_service_years
        },
        "risk_metrics": {
            "retirement_risk_count": retirement_risk_count,
            "retirement_risk_pct": retirement_risk_pct,
            "growth_rate": growth_rate,
            "teachers_cy": teachers_cy,
            "teachers_py": teachers_py
        },
        "training_coverage": {
            "cwsn_trained": t.get("cwsn_trained", 0),
            "computer_trained": t.get("computer_trained", 0)
        },
        "quality_breakdown": [
            {"metric": "CTET Qualified", "value": ctet_pct, "color": "#10b981" if ctet_pct >= 50 else "#f59e0b"},
            {"metric": "NISHTHA Completed", "value": nishtha_pct, "color": "#3b82f6" if nishtha_pct >= 50 else "#f59e0b"},
            {"metric": "Aadhaar Verified", "value": aadhaar_verified_pct, "color": "#8b5cf6" if aadhaar_verified_pct >= 90 else "#f59e0b"},
            {"metric": "Female Representation", "value": female_pct, "color": "#ec4899"}
        ],
        "block_performance": [
            {
                "block_code": b.get("block_code", ""),
                "block_name": b.get("block_name", ""),
                "teachers": b.get("teachers", 0),
                "ctet_pct": round(b.get("ctet_pct", 0) or 0, 1),
                "nishtha_pct": round(b.get("nishtha_pct", 0) or 0, 1),
            }
            for b in block_data
        ],
        "qualification_metrics": {
            "professional_qualification_distribution": prof_qual_data,
            "academic_qualification_distribution": acad_qual_data,
            "top_professional_qualification": prof_qual_data[0] if prof_qual_data else None,
            "top_academic_qualification": acad_qual_data[0] if acad_qual_data else None,
            "b_ed_or_higher_pct": round(b_ed_or_higher_count / total_records * 100, 1) if total_records > 0 else 0,
            "post_graduate_pct": round(post_graduate_count / total_records * 100, 1) if total_records > 0 else 0
        },
        "school_teacher_distribution": {
            "zero_teacher_schools": zero_teacher_schools,
            "one_teacher_schools": one_teacher_schools,
            "two_teacher_schools": two_teacher_schools,
            "total_schools": total_schools_all
        }
    }
    if debug and sample_docs:
        from bson import ObjectId
        def _serialize(d):
            if not d:
                return d
            return {k: (str(v) if isinstance(v, ObjectId) else v) for k, v in d.items()}
        out["_debug_sample"] = [_serialize(d) for d in sample_docs]
    return out


@router.get("/schools-by-teacher-count")
async def get_schools_by_teacher_count(
    teacher_count: int = Query(..., description="Number of teachers: 0, 1, or 2"),
    district_code: Optional[str] = Query(None),
    block_code: Optional[str] = Query(None),
    udise_code: Optional[str] = Query(None),
    limit: int = Query(100, description="Maximum number of schools to return"),
):
    """Get list of schools with specified number of teachers, including student counts"""
    scope_match = build_scope_match(district_code=district_code, block_code=block_code, udise_code=udise_code)
    
    if teacher_count == 0:
        # Schools with zero teachers - schools not in ctteacher_analytics
        schools_query = scope_match if scope_match else {}
        schools_with_teachers_list = await db.ctteacher_analytics.distinct("udise_code", schools_query)
        schools_with_teachers = set(schools_with_teachers_list) if schools_with_teachers_list else set()
        
        # Get all schools in scope from infrastructure_analytics
        total_schools_pipeline = prepend_match([
            {"$group": {
                "_id": "$udise_code",
                "school_name": {"$first": "$school_name"},
                "block_name": {"$first": "$block_name"},
                "block_code": {"$first": "$block_code"},
                "district_name": {"$first": "$district_name"},
                "district_code": {"$first": "$district_code"}
            }}
        ], scope_match)
        total_schools_cursor = db.infrastructure_analytics.aggregate(total_schools_pipeline)
        all_schools = await total_schools_cursor.to_list(length=10000)
        
        # Filter to get schools with zero teachers
        zero_teacher_schools = [s for s in all_schools if s.get("_id") not in schools_with_teachers]
        
        # Get student counts from aadhaar_analytics
        schools_list = []
        for school in zero_teacher_schools[:limit]:
            udise = school.get("_id")
            # Get student count from aadhaar_analytics
            student_data = await db.aadhaar_analytics.find_one(
                {"udise_code": udise},
                {"total_enrolment": 1}
            )
            student_count = student_data.get("total_enrolment", 0) if student_data else 0
            
            schools_list.append({
                "udise_code": udise,
                "school_name": school.get("school_name", ""),
                "block_name": school.get("block_name", ""),
                "block_code": school.get("block_code", ""),
                "district_name": school.get("district_name", ""),
                "district_code": school.get("district_code", ""),
                "teacher_count": 0,
                "student_count": student_count
            })
        
        return {
            "teacher_count": 0,
            "total_schools": len(zero_teacher_schools),
            "schools": sorted(schools_list, key=lambda x: x["student_count"], reverse=True)
        }
    
    else:
        # Schools with 1 or 2 teachers - from ctteacher_analytics
        school_teacher_pipeline = prepend_match([
            {"$group": {
                "_id": "$udise_code",
                "teacher_count": {"$sum": 1},
                "school_name": {"$first": "$school_name"},
                "block_name": {"$first": "$block_name"},
                "block_code": {"$first": "$block_code"},
                "district_name": {"$first": "$district_name"},
                "district_code": {"$first": "$district_code"}
            }},
            {"$match": {"teacher_count": teacher_count}},
            {"$limit": limit}
        ], scope_match)
        school_teacher_cursor = db.ctteacher_analytics.aggregate(school_teacher_pipeline)
        school_teacher_data = await school_teacher_cursor.to_list(length=limit)
        
        # Get student counts from aadhaar_analytics
        schools_list = []
        for school in school_teacher_data:
            udise = school.get("_id")
            # Get student count from aadhaar_analytics
            student_data = await db.aadhaar_analytics.find_one(
                {"udise_code": udise},
                {"total_enrolment": 1}
            )
            student_count = student_data.get("total_enrolment", 0) if student_data else 0
            
            schools_list.append({
                "udise_code": udise,
                "school_name": school.get("school_name", ""),
                "block_name": school.get("block_name", ""),
                "block_code": school.get("block_code", ""),
                "district_name": school.get("district_name", ""),
                "district_code": school.get("district_code", ""),
                "teacher_count": teacher_count,
                "student_count": student_count
            })
        
        # Get total count
        total_count_pipeline = prepend_match([
            {"$group": {
                "_id": "$udise_code",
                "teacher_count": {"$sum": 1}
            }},
            {"$match": {"teacher_count": teacher_count}},
            {"$count": "total"}
        ], scope_match)
        total_count_cursor = db.ctteacher_analytics.aggregate(total_count_pipeline)
        total_count_data = await total_count_cursor.to_list(length=1)
        total_schools = total_count_data[0].get("total", len(schools_list)) if total_count_data else len(schools_list)
        
        return {
            "teacher_count": teacher_count,
            "total_schools": total_schools,
            "schools": sorted(schools_list, key=lambda x: x["student_count"], reverse=True)
    }


@router.get("/operational-performance")
async def get_operational_performance(
    district_code: Optional[str] = Query(None),
    block_code: Optional[str] = Query(None),
    udise_code: Optional[str] = Query(None),
    district_name: Optional[str] = Query(None),
    block_name: Optional[str] = Query(None),
):
    """Get Operational Performance KPIs from Data Entry and Dropbox data"""
    dn = (district_name.strip().upper() or None) if (district_name and isinstance(district_name, str)) else None
    bn = (block_name.strip().upper() or None) if (block_name and isinstance(block_name, str)) else None
    scope_match = build_scope_match(district_code=district_code, block_code=block_code, udise_code=udise_code, district_name=dn, block_name=bn)
    
    # Get Data Entry Status - certified is "Yes"/"No" string
    de_pipeline = prepend_match([
        {"$group": {
            "_id": None,
            "total_schools": {"$sum": 1},
            "total_students": {"$sum": "$total_students"},
            "completed_students": {"$sum": "$completed"},
            "pending_students": {"$sum": {"$add": ["$not_started", "$in_progress"]}},
            "certified_schools": {"$sum": {"$cond": [{"$eq": ["$certified", "Yes"]}, 1, 0]}},
            "repeaters": {"$sum": "$repeaters"}
        }}
    ], scope_match)
    de_cursor = db.data_entry_analytics.aggregate(de_pipeline)
    de_data = await de_cursor.to_list(length=1)
    
    # Get Dropbox Remarks
    dropbox_pipeline = prepend_match([
        {"$group": {
            "_id": None,
            "total_schools": {"$sum": 1},
            "total_remarks": {"$sum": "$total_remarks"},
            "dropout_count": {"$sum": "$dropout"},
            "migration_count": {"$sum": "$migration"},
            "class12_passed": {"$sum": "$class12_passed"},
            "wrong_entry": {"$sum": "$wrong_entry"}
        }}
    ], scope_match)
    dropbox_cursor = db.dropbox_analytics.aggregate(dropbox_pipeline)
    dropbox_data = await dropbox_cursor.to_list(length=1)
    
    # Get Enrolment data
    enrol_pipeline = prepend_match([
        {"$group": {
            "_id": None,
            "total_schools": {"$sum": 1},
            "total_enrolment": {"$sum": "$total_enrolment"},
            "girls_enrolment": {"$sum": "$girls_enrolment"},
            "boys_enrolment": {"$sum": "$boys_enrolment"}
        }}
    ], scope_match)
    enrol_cursor = db.enrolment_analytics.aggregate(enrol_pipeline)
    enrol_data = await enrol_cursor.to_list(length=1)
    
    # Block-wise operational metrics - certified is "Yes"/"No" string
    block_pipeline = prepend_match([
        {"$group": {
            "_id": {"block_code": "$block_code", "block_name": "$block_name"},
            "schools": {"$sum": 1},
            "students": {"$sum": "$total_students"},
            "completed": {"$sum": "$completed"},
            "certified": {"$sum": {"$cond": [{"$eq": ["$certified", "Yes"]}, 1, 0]}}
        }},
        {"$project": {
            "_id": 0,
            "block_code": "$_id.block_code",
            "block_name": "$_id.block_name",
            "schools": 1,
            "completion_rate": {"$multiply": [{"$divide": ["$completed", {"$max": ["$students", 1]}]}, 100]},
            "certification_rate": {"$multiply": [{"$divide": ["$certified", {"$max": ["$schools", 1]}]}, 100]}
        }},
        {"$sort": {"completion_rate": -1}}
    ], scope_match)
    block_cursor = db.data_entry_analytics.aggregate(block_pipeline)
    block_data = await block_cursor.to_list(length=30)
    
    if not de_data:
        de_data = [{}]
    if not dropbox_data:
        dropbox_data = [{}]
    if not enrol_data:
        enrol_data = [{}]
    
    de = de_data[0]
    dr = dropbox_data[0]
    en = enrol_data[0]
    
    total_schools = de.get("total_schools", 0) or dr.get("total_schools", 0)
    total_students = de.get("total_students", 0)
    completed = de.get("completed_students", 0)
    
    # Calculate KPIs
    completion_rate = round(completed / total_students * 100, 2) if total_students > 0 else 0
    certification_rate = round(de.get("certified_schools", 0) / total_schools * 100, 1) if total_schools > 0 else 0
    repeater_rate = round(de.get("repeaters", 0) / total_students * 100, 2) if total_students > 0 else 0
    
    # Dropbox metrics
    total_remarks = dr.get("total_remarks", 0)
    dropout_count = dr.get("dropout_count", 0)
    dropout_rate = round(dropout_count / total_remarks * 100, 2) if total_remarks > 0 else 0
    data_accuracy = round((total_remarks - dr.get("wrong_entry", 0)) / total_remarks * 100, 1) if total_remarks > 0 else 0
    
    # Enrolment metrics
    total_enrolment = en.get("total_enrolment", 0)
    girls_pct = round(en.get("girls_enrolment", 0) / total_enrolment * 100, 1) if total_enrolment > 0 else 0
    
    # Operational Performance Index = (Completion * 0.3 + Certification * 0.25 + Data Accuracy * 0.25 + (100 - Dropout) * 0.2)
    operational_index = round(completion_rate * 0.3 + certification_rate * 0.25 + data_accuracy * 0.25 + (100 - dropout_rate) * 0.2, 1)
    
    return {
        "summary": {
            "total_schools": total_schools,
            "total_students": total_students,
            "total_enrolment": total_enrolment,
            "operational_index": operational_index
        },
        "data_entry_metrics": {
            "completion_rate": completion_rate,
            "completed_students": completed,
            "pending_students": de.get("pending_students", 0),
            "certified_schools": de.get("certified_schools", 0),
            "certification_rate": certification_rate,
            "repeaters": de.get("repeaters", 0),
            "repeater_rate": repeater_rate
        },
        "dropbox_metrics": {
            "total_remarks": total_remarks,
            "dropout_count": dropout_count,
            "dropout_rate": dropout_rate,
            "migration_count": dr.get("migration_count", 0),
            "class12_passed": dr.get("class12_passed", 0),
            "wrong_entry": dr.get("wrong_entry", 0),
            "data_accuracy": data_accuracy
        },
        "enrolment_metrics": {
            "total_enrolment": total_enrolment,
            "girls_enrolment": en.get("girls_enrolment", 0),
            "boys_enrolment": en.get("boys_enrolment", 0),
            "girls_pct": girls_pct,
            "gender_parity": round(en.get("girls_enrolment", 0) / en.get("boys_enrolment", 1), 2) if en.get("boys_enrolment", 0) > 0 else 0
        },
        "index_breakdown": [
            {"metric": "Data Completion", "value": completion_rate, "color": "#10b981" if completion_rate >= 99 else "#f59e0b"},
            {"metric": "School Certification", "value": certification_rate, "color": "#3b82f6" if certification_rate >= 50 else "#f59e0b"},
            {"metric": "Data Accuracy", "value": data_accuracy, "color": "#8b5cf6" if data_accuracy >= 90 else "#f59e0b"},
            {"metric": "Retention Rate", "value": round(100 - dropout_rate, 2), "color": "#ec4899" if dropout_rate < 5 else "#ef4444"}
        ],
        "block_performance": [
            {
                "block_code": b.get("block_code", ""),
                "block_name": b.get("block_name", ""),
                "completion_rate": round(b.get("completion_rate", 0) or 0, 2),
                "certification_rate": round(b.get("certification_rate", 0) or 0, 1),
            }
            for b in block_data
        ]
    }


def _default_shi_response():
    return {
        "summary": {"school_health_index": 0, "total_schools": 0, "total_students": 0, "rag_status": {"status": "Red", "color": "#ef4444"}},
        "domain_scores": {
            "identity_compliance": {"score": 0, "weight": 25, "rag": {"status": "Red", "color": "#ef4444"}},
            "infrastructure": {"score": 0, "weight": 25, "rag": {"status": "Red", "color": "#ef4444"}},
            "teacher_quality": {"score": 0, "weight": 25, "rag": {"status": "Red", "color": "#ef4444"}},
            "operational": {"score": 0, "weight": 25, "rag": {"status": "Red", "color": "#ef4444"}},
        },
        "shi_breakdown": [],
        "key_metrics": {},
        "block_rankings": [],
        "rag_distribution": {"green": 0, "amber": 0, "red": 0},
    }


@router.get("/school-health-index")
async def get_school_health_index(
    district_code: Optional[str] = Query(None),
    block_code: Optional[str] = Query(None),
    udise_code: Optional[str] = Query(None),
    district_name: Optional[str] = Query(None),
    block_name: Optional[str] = Query(None),
):
    """Get School Health Index (SHI) - Composite index from all domains. Returns default on any error."""
    try:
        identity = await get_student_identity_compliance(district_code=district_code, block_code=block_code, udise_code=udise_code, district_name=district_name, block_name=block_name)
        infrastructure = await get_infrastructure_facilities(district_code=district_code, block_code=block_code, udise_code=udise_code, district_name=district_name, block_name=block_name)
        teacher = await get_teacher_staffing(district_code=district_code, block_code=block_code, udise_code=udise_code, district_name=district_name, block_name=block_name)
        operational = await get_operational_performance(district_code=district_code, block_code=block_code, udise_code=udise_code, district_name=district_name, block_name=block_name)
    except Exception:
        return _default_shi_response()

    try:
        identity_index = identity.get("summary", {}).get("identity_compliance_index", 0)
        infra_index = infrastructure.get("summary", {}).get("infrastructure_index", 0)
        teacher_index = teacher.get("summary", {}).get("teacher_quality_index", 0)
        operational_index = operational.get("summary", {}).get("operational_index", 0)

        # Calculate School Health Index (SHI)
        # SHI = Identity (25%) + Infrastructure (25%) + Teacher (20%) + Operational (20%)
        shi = round(identity_index * 0.25 + infra_index * 0.25 + teacher_index * 0.25 + operational_index * 0.25, 1)

        def get_rag(value):
            if value >= 85:
                return {"status": "Green", "color": "#10b981"}
            elif value >= 70:
                return {"status": "Amber", "color": "#f59e0b"}
            else:
                return {"status": "Red", "color": "#ef4444"}

        # Block-wise SHI calculation
        block_shi = []
        for i, block in enumerate(infrastructure.get("block_performance", [])[:20]):
            block_name = block.get("block_name")
            block_code = block.get("block_code")
            identity_block = next(
                (b for b in identity.get("block_performance", []) if (block_code and b.get("block_code") == block_code) or b.get("block_name") == block_name),
                {},
            )
            teacher_block = next(
                (b for b in teacher.get("block_performance", []) if (block_code and b.get("block_code") == block_code) or b.get("block_name") == block_name),
                {},
            )
            operational_block = next(
                (b for b in operational.get("block_performance", []) if (block_code and b.get("block_code") == block_code) or b.get("block_name") == block_name),
                {},
            )
            block_identity = identity_block.get("aadhaar_pct", 85)
            block_infra = block.get("classroom_health", 90)
            block_teacher = teacher_block.get("ctet_pct", 10) * 2
            block_ops = operational_block.get("completion_rate", 99)
            block_shi_value = round((block_identity * 0.25 + block_infra * 0.25 + block_teacher * 0.25 + block_ops * 0.25), 1)
            block_shi.append({
                "rank": i + 1,
                "block_code": block_code,
                "block_name": block_name,
                "shi_score": block_shi_value,
                "identity_score": round(block_identity, 1),
                "infra_score": round(block_infra, 1),
                "teacher_score": round(block_teacher, 1),
                "ops_score": round(block_ops, 1),
                "rag": get_rag(block_shi_value)
            })

        block_shi.sort(key=lambda x: x["shi_score"], reverse=True)
        for i, b in enumerate(block_shi):
            b["rank"] = i + 1

        return {
            "summary": {
                "school_health_index": shi,
                "total_schools": identity.get("summary", {}).get("total_schools", 0),
                "total_students": identity.get("summary", {}).get("total_students", 0),
                "rag_status": get_rag(shi)
            },
            "domain_scores": {
                "identity_compliance": {"score": identity_index, "weight": 25, "rag": get_rag(identity_index)},
                "infrastructure": {"score": infra_index, "weight": 25, "rag": get_rag(infra_index)},
                "teacher_quality": {"score": teacher_index, "weight": 25, "rag": get_rag(teacher_index)},
                "operational": {"score": operational_index, "weight": 25, "rag": get_rag(operational_index)}
            },
            "shi_breakdown": [
                {"domain": "Student Identity", "score": identity_index, "weight": 25, "contribution": round(identity_index * 0.25, 1), "color": "#3b82f6"},
                {"domain": "Infrastructure", "score": infra_index, "weight": 25, "contribution": round(infra_index * 0.25, 1), "color": "#10b981"},
                {"domain": "Teacher Quality", "score": teacher_index, "weight": 25, "contribution": round(teacher_index * 0.25, 1), "color": "#8b5cf6"},
                {"domain": "Operational", "score": operational_index, "weight": 25, "contribution": round(operational_index * 0.25, 1), "color": "#f59e0b"}
            ],
            "key_metrics": {
                "aadhaar_coverage": identity.get("aadhaar_metrics", {}).get("aadhaar_coverage_pct", 0),
                "apaar_coverage": identity.get("apaar_metrics", {}).get("apaar_coverage_pct", 0),
                "classroom_health": infrastructure.get("classroom_metrics", {}).get("classroom_health_pct", 0),
                "toilet_functional": infrastructure.get("toilet_metrics", {}).get("functional_pct", 0),
                "teacher_quality": teacher.get("summary", {}).get("teacher_quality_index", 0),
                "data_completion": operational.get("data_entry_metrics", {}).get("completion_rate", 0)
            },
            "block_rankings": block_shi,
            "rag_distribution": {
                "green": len([b for b in block_shi if b.get("rag", {}).get("status") == "Green"]),
                "amber": len([b for b in block_shi if b.get("rag", {}).get("status") == "Amber"]),
                "red": len([b for b in block_shi if b.get("rag", {}).get("status") == "Red"])
            }
        }
    except Exception:
        return _default_shi_response()


@router.get("/overview")
async def get_executive_overview(
    district_code: Optional[str] = Query(None),
    block_code: Optional[str] = Query(None),
    udise_code: Optional[str] = Query(None),
    district_name: Optional[str] = Query(None),
    block_name: Optional[str] = Query(None),
):
    """Get complete executive overview with all domain KPIs. Resilient to individual domain failures."""
    empty_identity = {"summary": {"total_schools": 0, "total_students": 0, "identity_compliance_index": 0}, "aadhaar_metrics": {"aadhaar_coverage_pct": 0}, "apaar_metrics": {"apaar_coverage_pct": 0}}
    empty_infra = {"summary": {"total_classrooms": 0, "total_toilets": 0, "infrastructure_index": 0}, "classroom_metrics": {"classroom_health_pct": 0}, "toilet_metrics": {"functional_pct": 0}}
    empty_teacher = {"summary": {"teacher_quality_index": 0, "total_teachers": 0}, "compliance_metrics": {"ctet_pct": 0}}
    empty_operational = {"summary": {"operational_index": 0}, "data_entry_metrics": {"completion_rate": 0, "certification_rate": 0}}
    empty_shi = {"summary": {"school_health_index": 0, "rag_status": {"status": "Red", "color": "#ef4444"}}}
    try:
        identity = await get_student_identity_compliance(district_code=district_code, block_code=block_code, udise_code=udise_code, district_name=district_name, block_name=block_name)
    except Exception:
        identity = empty_identity
    try:
        infrastructure = await get_infrastructure_facilities(district_code=district_code, block_code=block_code, udise_code=udise_code, district_name=district_name, block_name=block_name)
    except Exception:
        infrastructure = empty_infra
    try:
        teacher = await get_teacher_staffing(district_code=district_code, block_code=block_code, udise_code=udise_code, district_name=district_name, block_name=block_name)
    except Exception:
        teacher = empty_teacher
    try:
        operational = await get_operational_performance(district_code=district_code, block_code=block_code, udise_code=udise_code, district_name=district_name, block_name=block_name)
    except Exception:
        operational = empty_operational
    try:
        shi = await get_school_health_index(district_code=district_code, block_code=block_code, udise_code=udise_code, district_name=district_name, block_name=block_name)
    except Exception:
        shi = empty_shi
    return {
        "shi": shi.get("summary", empty_shi["summary"]),
        "domain_summary": {
            "identity": {
                "index": identity.get("summary", {}).get("identity_compliance_index", 0),
                "aadhaar_pct": identity.get("aadhaar_metrics", {}).get("aadhaar_coverage_pct", 0),
                "apaar_pct": identity.get("apaar_metrics", {}).get("apaar_coverage_pct", 0),
            },
            "infrastructure": {
                "index": infrastructure.get("summary", {}).get("infrastructure_index", 0),
                "classroom_health": infrastructure.get("classroom_metrics", {}).get("classroom_health_pct", 0),
                "toilet_functional": infrastructure.get("toilet_metrics", {}).get("functional_pct", 0),
            },
            "teacher": {
                "index": teacher.get("summary", {}).get("teacher_quality_index", 0),
                "total_teachers": teacher.get("summary", {}).get("total_teachers", 0),
                "ctet_pct": teacher.get("compliance_metrics", {}).get("ctet_pct", 0),
            },
            "operational": {
                "index": operational.get("summary", {}).get("operational_index", 0),
                "completion_rate": operational.get("data_entry_metrics", {}).get("completion_rate", 0),
                "certification_rate": operational.get("data_entry_metrics", {}).get("certification_rate", 0),
            },
        },
        "quick_stats": {
            "total_schools": identity.get("summary", {}).get("total_schools", 0),
            "total_students": identity.get("summary", {}).get("total_students", 0),
            "total_teachers": teacher.get("summary", {}).get("total_teachers", 0),
            "total_classrooms": infrastructure.get("summary", {}).get("total_classrooms", 0),
            "total_toilets": infrastructure.get("summary", {}).get("total_toilets", 0),
        },
        "alerts": [
            {"type": "warning", "message": f"APAAR Coverage at {identity.get('apaar_metrics', {}).get('apaar_coverage_pct', 0)}%", "domain": "Identity"} if identity.get("apaar_metrics", {}).get("apaar_coverage_pct", 0) < 90 else None,
            {"type": "info", "message": f"Teacher CTET Rate at {teacher.get('compliance_metrics', {}).get('ctet_pct', 0)}%", "domain": "Teacher"} if teacher.get("compliance_metrics", {}).get("ctet_pct", 0) < 50 else None,
            {"type": "success", "message": f"Data Completion at {operational.get('data_entry_metrics', {}).get('completion_rate', 0)}%", "domain": "Operational"} if operational.get("data_entry_metrics", {}).get("completion_rate", 0) >= 99 else None,
        ],
    }



def _default_map_response():
    all_d = [
        "Ahmadnagar", "Akola", "Amravati", "Aurangabad", "Bhandara", "Bid", "Buldana",
        "Chandrapur", "Dhule", "Gadchiroli", "Gondiya", "Hingoli", "Jalgaon", "Jalna",
        "Kolhapur", "Latur", "Mumbai", "Mumbai Suburban", "Nagpur", "Nanded", "Nandurbar",
        "Nashik", "Osmanabad", "Palghar", "Parbhani", "Pune", "Raigarh", "Ratnagiri",
        "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"
    ]
    return {
        "districts": [
            {"district_name": d, "has_data": False, "total_schools": 0, "total_students": 0, "total_teachers": 0, "metrics": {"shi": None, "aadhaar_coverage": None, "apaar_coverage": None, "infrastructure_index": None}}
            for d in all_d
        ],
        "summary": {"total_districts": len(all_d), "districts_with_data": 0, "districts_no_data": len(all_d), "avg_shi": 0, "avg_aadhaar": 0, "avg_apaar": 0},
        "metric_options": [
            {"key": "shi", "label": "School Health Index", "unit": "%"},
            {"key": "aadhaar_coverage", "label": "Aadhaar Coverage", "unit": "%"},
            {"key": "apaar_coverage", "label": "APAAR Generation", "unit": "%"},
            {"key": "infrastructure_index", "label": "Infrastructure Index", "unit": "%"},
            {"key": "ctet_qualified_pct", "label": "CTET Qualified Teachers", "unit": "%"}
        ]
    }


@router.get("/district-map-data")
async def get_district_map_data(
    district_code: Optional[str] = Query(None),
    block_code: Optional[str] = Query(None),
    udise_code: Optional[str] = Query(None),
):
    """Get district-wise metrics for choropleth map visualization"""
    scope_match = build_scope_match(district_code=district_code, block_code=block_code, udise_code=udise_code)
    
    # Maharashtra districts list - will show "no data" for districts without data
    all_districts = [
        "Ahmadnagar", "Akola", "Amravati", "Aurangabad", "Bhandara", "Bid", "Buldana",
        "Chandrapur", "Dhule", "Gadchiroli", "Gondiya", "Hingoli", "Jalgaon", "Jalna",
        "Kolhapur", "Latur", "Mumbai", "Mumbai Suburban", "Nagpur", "Nanded", "Nandurbar",
        "Nashik", "Osmanabad", "Palghar", "Parbhani", "Pune", "Raigarh", "Ratnagiri",
        "Sangli", "Satara", "Sindhudurg", "Solapur", "Thane", "Wardha", "Washim", "Yavatmal"
    ]
    
    # Get district-wise aggregated data from aadhaar_analytics
    aadhaar_pipeline = prepend_match([
        {"$group": {
            "_id": "$district_name",
            "district_code": {"$first": "$district_code"},
            "total_schools": {"$sum": 1},
            "total_students": {"$sum": "$total_enrolment"},
            "aadhaar_passed": {"$sum": "$aadhaar_passed"},
            "name_match": {"$sum": "$name_match"}
        }}
    ], scope_match)
    aadhaar_cursor = db.aadhaar_analytics.aggregate(aadhaar_pipeline)
    aadhaar_data = {d["_id"]: d for d in await aadhaar_cursor.to_list(length=50)}
    
    # Get APAAR data
    apaar_pipeline = prepend_match([
        {"$group": {
            "_id": "$district_name",
            "district_code": {"$first": "$district_code"},
            "total_students": {"$sum": "$total_student"},
            "apaar_generated": {"$sum": "$total_generated"}
        }}
    ], scope_match)
    apaar_cursor = db.apaar_analytics.aggregate(apaar_pipeline)
    apaar_data = {d["_id"]: d for d in await apaar_cursor.to_list(length=50)}
    
    # Get Infrastructure data
    infra_pipeline = prepend_match([
        {"$group": {
            "_id": "$district_name",
            "district_code": {"$first": "$district_code"},
            "total_schools": {"$sum": 1},
            "functional_classrooms": {"$sum": "$functional_classrooms"},
            "functional_toilets": {"$sum": {"$add": ["$boys_toilets_functional", "$girls_toilets_functional"]}},
            "tap_water": {"$sum": {"$cond": [{"$eq": ["$tap_water", 1]}, 1, 0]}},
            "electricity": {"$sum": {"$cond": [{"$eq": ["$electricity", 1]}, 1, 0]}}
        }}
    ], scope_match)
    infra_cursor = db.infrastructure_analytics.aggregate(infra_pipeline)
    infra_data = {d["_id"]: d for d in await infra_cursor.to_list(length=50)}
    
    # Get Teacher data
    teacher_pipeline = [
        {"$group": {
            "_id": "$district_name",
            "district_code": {"$first": "$district_code"},
            "total_teachers": {"$sum": 1},
            "ctet_qualified": {"$sum": {"$cond": [{"$eq": ["$ctet_qualified", 1]}, 1, 0]}},
            "nishtha_completed": {"$sum": {"$cond": [{"$eq": ["$training_nishtha", 1]}, 1, 0]}}
        }}
    ]
    teacher_cursor = db.ctteacher_analytics.aggregate(teacher_pipeline)
    teacher_data = {d["_id"]: d for d in await teacher_cursor.to_list(length=50)}
    
    # Get Data Entry completion data
    data_entry_pipeline = [
        {"$group": {
            "_id": "$district_name",
            "district_code": {"$first": "$district_code"},
            "total_students": {"$sum": "$total_students"},
            "completed": {"$sum": "$completed"}
        }}
    ]
    data_entry_cursor = db.data_entry_analytics.aggregate(data_entry_pipeline)
    data_entry_data = {d["_id"]: d for d in await data_entry_cursor.to_list(length=50)}
    
    # Build district metrics
    district_metrics = []
    
    for district in all_districts:
        # Normalize district name for matching (database has uppercase PUNE)
        db_district = district.upper()
        
        aadhaar = aadhaar_data.get(db_district, {})
        apaar = apaar_data.get(db_district, {})
        infra = infra_data.get(db_district, {})
        teacher = teacher_data.get(db_district, {})
        data_entry = data_entry_data.get(db_district, {})
        
        has_data = bool(aadhaar or apaar or infra or teacher or data_entry)
        
        # Calculate metrics
        total_students = aadhaar.get("total_students", 0) or 0
        total_schools = aadhaar.get("total_schools", 0) or infra.get("total_schools", 0) or 0
        
        # Aadhaar Coverage
        aadhaar_coverage = round(aadhaar.get("aadhaar_passed", 0) / total_students * 100, 1) if total_students > 0 else None
        
        # APAAR Coverage
        apaar_students = apaar.get("total_students", 0) or 0
        apaar_coverage = round(apaar.get("apaar_generated", 0) / apaar_students * 100, 1) if apaar_students > 0 else None
        
        # Infrastructure Index (avg of electricity, tap water, functional classrooms)
        infra_schools = infra.get("total_schools", 0) or 1
        electricity_pct = round(infra.get("electricity", 0) / infra_schools * 100, 1) if infra_schools > 0 else None
        tap_water_pct = round(infra.get("tap_water", 0) / infra_schools * 100, 1) if infra_schools > 0 else None
        infra_index = round((electricity_pct + tap_water_pct) / 2, 1) if electricity_pct is not None and tap_water_pct is not None else None
        
        # Teacher Quality (CTET %)
        total_teachers = teacher.get("total_teachers", 0) or 0
        ctet_pct = round(teacher.get("ctet_qualified", 0) / total_teachers * 100, 1) if total_teachers > 0 else None
        
        # Data Completion
        data_students = data_entry.get("total_students", 0) or 0
        completion_rate = round(data_entry.get("completed", 0) / data_students * 100, 1) if data_students > 0 else None
        
        # School Health Index (composite)
        shi = None
        if has_data and aadhaar_coverage is not None:
            shi_components = []
            if aadhaar_coverage is not None:
                shi_components.append(aadhaar_coverage * 0.2)
            if apaar_coverage is not None:
                shi_components.append(apaar_coverage * 0.2)
            if infra_index is not None:
                shi_components.append(infra_index * 0.25)
            if ctet_pct is not None:
                shi_components.append(ctet_pct * 0.15)
            if completion_rate is not None:
                shi_components.append(completion_rate * 0.2)
            
            if shi_components:
                shi = round(sum(shi_components) / (len(shi_components) / 5), 1)  # Normalize to 100
        
        district_code_out = (
            aadhaar.get("district_code")
            or apaar.get("district_code")
            or infra.get("district_code")
            or teacher.get("district_code")
            or data_entry.get("district_code")
            or MAHA_DISTRICT_CODES.get(db_district)
        )

        district_metrics.append({
            "district_name": district,
            "district_code": district_code_out,
            "has_data": has_data,
            "total_schools": total_schools,
            "total_students": total_students,
            "total_teachers": total_teachers,
            "metrics": {
                "shi": shi,
                "aadhaar_coverage": aadhaar_coverage,
                "apaar_coverage": apaar_coverage,
                "infrastructure_index": infra_index,
                "ctet_qualified_pct": ctet_pct,
                "completion_rate": completion_rate
            }
        })
    
    # Summary statistics
    districts_with_data = [d for d in district_metrics if d["has_data"]]
    
    return {
        "districts": district_metrics,
        "summary": {
            "total_districts": len(all_districts),
            "districts_with_data": len(districts_with_data),
            "districts_no_data": len(all_districts) - len(districts_with_data),
            "avg_shi": round(sum(d["metrics"]["shi"] for d in districts_with_data if d["metrics"]["shi"]) / len(districts_with_data), 1) if districts_with_data else 0,
            "avg_aadhaar": round(sum(d["metrics"]["aadhaar_coverage"] for d in districts_with_data if d["metrics"]["aadhaar_coverage"]) / len(districts_with_data), 1) if districts_with_data else 0,
            "avg_apaar": round(sum(d["metrics"]["apaar_coverage"] for d in districts_with_data if d["metrics"]["apaar_coverage"]) / len(districts_with_data), 1) if districts_with_data else 0
        },
        "metric_options": [
            {"key": "shi", "label": "School Health Index", "unit": "%"},
            {"key": "aadhaar_coverage", "label": "Aadhaar Coverage", "unit": "%"},
            {"key": "apaar_coverage", "label": "APAAR Generation", "unit": "%"},
            {"key": "infrastructure_index", "label": "Infrastructure Index", "unit": "%"},
            {"key": "ctet_qualified_pct", "label": "CTET Qualified Teachers", "unit": "%"}
        ]
    }


DEMO_SCOPE = {"district_code": "2725", "district_name": "PUNE", "block_code": "001", "block_name": "Haveli", "udise_code": "27250100101", "school_name": "Demo School"}


@router.post("/seed-demo-data")
async def seed_executive_demo_data():
    """Insert minimal documents so Executive Dashboard (Overview, Teacher, SHI) show sample data. Idempotent: uses demo scope and replaces demo docs."""
    if db is None:
        raise HTTPException(status_code=503, detail="Database not initialized")
    try:
        # Remove existing demo docs (same scope) so we don't duplicate
        demo_filter = {"district_code": DEMO_SCOPE["district_code"], "block_code": DEMO_SCOPE["block_code"], "udise_code": DEMO_SCOPE["udise_code"]}
        await db.aadhaar_analytics.delete_many(demo_filter)
        await db.apaar_analytics.delete_many(demo_filter)
        await db.infrastructure_analytics.delete_many(demo_filter)
        await db.ctteacher_analytics.delete_many(demo_filter)
        await db.teacher_analytics.delete_many(demo_filter)
        await db.classrooms_toilets.delete_many(demo_filter)
        await db.data_entry_analytics.delete_many(demo_filter)
        await db.enrolment_analytics.delete_many(demo_filter)
        await db.dropbox_analytics.delete_many(demo_filter)

        base = {**DEMO_SCOPE}

        # One school row so identity/infra/operational aggregations return non-zero
        await db.aadhaar_analytics.insert_one({
            **base,
            "total_enrolment": 500,
            "aadhaar_passed": 450,
            "aadhaar_failed": 50,
            "name_match": 440,
            "mbu_pending_5_15": 5,
            "mbu_pending_15_above": 5,
            "exception_rate": 0.02,
        })
        await db.apaar_analytics.insert_one({
            **base,
            "total_student": 500,
            "total_generated": 400,
            "total_not_applied": 50,
            "total_failed": 50,
        })
        await db.infrastructure_analytics.insert_one({
            **base,
            "tap_water": 1,
            "water_purifier": 1,
            "water_quality_tested": 1,
            "rain_water_harvesting": 1,
            "ramp": True,
            "medical_checkup": True,
            "first_aid": True,
        })
        await db.classrooms_toilets.insert_one({
            **base,
            "classrooms_instructional": 12,
            "pucca_good": 10,
            "part_pucca_good": 2,
            "pucca_minor": 0,
            "pucca_major": 0,
            "part_pucca_minor": 0,
            "part_pucca_major": 0,
            "boys_toilets_total": 8,
            "girls_toilets_total": 8,
            "boys_toilets_functional": 8,
            "girls_toilets_functional": 8,
            "electricity": 1,
            "library_available": 1,
            "computer_labs": 1,
            "handwash_points": 4,
        })
        await db.ctteacher_analytics.insert_one({
            **base,
            "teacher_code": "T001",
            "aadhaar_verified": "Verified From UIDAI against Name,Gender & DOB",
            "ctet_qualified": 1,
            "training_nishtha": 1,
            "gender": "2-Female",
            "dob": "15/06/1985",
            "doj_service": "01/06/2010",
            "age": 39,
            "service_years": 15,
            "professional_qualification": "B.Ed",
            "academic_qualification": "Post graduate",
        })
        await db.ctteacher_analytics.insert_one({
            **base,
            "teacher_code": "T002",
            "aadhaar_verified": "Verified From UIDAI against Name,Gender & DOB",
            "ctet_qualified": 0,
            "training_nishtha": 1,
            "gender": "1-Male",
            "dob": "01/04/1968",
            "doj_service": "01/06/1990",
            "age": 56,
            "service_years": 34,
            "professional_qualification": "B.Ed",
            "academic_qualification": "Graduate",
        })
        await db.teacher_analytics.insert_one({
            **base,
            "teacher_tot_cy": 5,
            "teacher_tot_py": 4,
            "tot_teacher_tr_ctet_cy": 3,
            "tot_teacher_tr_cwsn_cy": 2,
            "tot_teacher_tr_computers_cy": 4,
        })
        await db.data_entry_analytics.insert_one({
            **base,
            "total_students": 500,
            "completed": 495,
            "not_started": 3,
            "in_progress": 2,
            "certified": "Yes",
            "repeaters": 10,
        })
        await db.enrolment_analytics.insert_one({
            **base,
            "total_enrolment": 500,
            "girls_enrolment": 240,
            "boys_enrolment": 260,
        })
        await db.dropbox_analytics.insert_one({
            **base,
            "total_remarks": 500,
            "dropout": 5,
            "migration": 2,
            "class12_passed": 450,
            "wrong_entry": 3,
        })
        return {"ok": True, "message": "Demo data seeded. Refresh the Executive Dashboard."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

