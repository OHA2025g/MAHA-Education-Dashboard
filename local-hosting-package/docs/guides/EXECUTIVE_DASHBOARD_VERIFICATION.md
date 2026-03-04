# Executive Dashboard – Overview, Teacher & Staffing, SHI Tabs Verification

## Step-by-step fixes applied

### Step 1: Backend scope and seed data
- **Overview / SHI / domain APIs** now accept `district_name` and `block_name` and pass them through so scope matching works when only names are set.
- **Seed data** for `classrooms_toilets` was updated with `pucca_minor`, `pucca_major`, `part_pucca_minor`, `part_pucca_major` (all 0) so aggregation does not fail on missing fields.

### Step 2: Teacher & Staffing aggregation fix
- **Teacher-staffing** was returning 500 due to `$toInt` on empty/invalid DOB/DoJ strings in `ctteacher_analytics`.
- **Change:** Replaced `$toInt` with `$convert` using `onError: 0` and `onNull: 0` for `birth_year` and `doj_year` so invalid or empty values no longer break the pipeline.

### Step 3: API verification (after fixes)
- **Overview:** `GET /api/executive/overview` → `quick_stats` has non-zero `total_schools`, `total_teachers`; `shi.school_health_index` is non-zero (e.g. 76.1).
- **Teacher & Staffing:** `GET /api/executive/teacher-staffing` → returns 200 with `summary.total_teachers`, `compliance_metrics`, etc.
- **School Health Index:** `GET /api/executive/school-health-index` → returns 200 with `summary.school_health_index`, `block_rankings`, `domain_scores`.

## How to verify in the browser (and take a screenshot)

1. Open the app: **http://localhost:3000**
2. Go to **Executive Dashboard** (sidebar).
3. If you see “No data”, click **Load demo data**, then **Refresh**.
4. **Overview tab:** You should see:
   - School Health Index gauge (e.g. 76.1)
   - Quick stats: Schools, Students, Teachers, Classrooms (non-zero)
   - Domain cards (Identity, Infrastructure, Teacher, Operational) with scores
   - SHI domain contribution chart and block rankings table
5. **Teacher & Staffing tab:** You should see:
   - Total teachers, Teacher Quality Index, compliance metrics (CTET %, etc.)
   - Charts and block performance table
6. **School Health Index tab:** You should see:
   - SHI gauge and RAG status
   - Green/Amber/Red block counts
   - Domain score cards and full block rankings table

Take a screenshot of each tab (Overview, Teacher & Staffing, School Health Index) to confirm data is visible. If any tab still shows no data, run **Refresh** or **Load demo data** again and re-check.

## Quick API check (no UI)

```bash
# Overview
curl -s http://localhost:8002/api/executive/overview | python3 -c "import sys,json; d=json.load(sys.stdin); print('Schools:', d['quick_stats']['total_schools'], 'Teachers:', d['quick_stats']['total_teachers'], 'SHI:', d['shi']['school_health_index'])"

# Teacher staffing
curl -s http://localhost:8002/api/executive/teacher-staffing | python3 -c "import sys,json; d=json.load(sys.stdin); print('Total teachers:', d['summary']['total_teachers'])"

# School Health Index
curl -s http://localhost:8002/api/executive/school-health-index | python3 -c "import sys,json; d=json.load(sys.stdin); print('SHI:', d['summary']['school_health_index'], 'Blocks:', len(d.get('block_rankings',[])))"
```

All three should print non-zero values when the backend and DB are correctly set up and (if needed) demo data is loaded.

---

## Retirement Risk (Teacher & Staffing → Risk Metrics)

**Source:** Collection `ctteacher_analytics`. Count = number of teachers with `effective_age >= 55`.  
`effective_age` = `age` (coerced to int) when 18–75, else derived from DOB (`current_year - birth_year`) when available.

**Fixes applied (if the card showed 0% / 0 teachers):**
1. **Age coercion:** `age` is converted with `$convert(..., onError: 0)` so string values (e.g. from Excel) are treated as numbers.
2. **Pipeline stages:** `effective_age` and `effective_service_years` are computed in a second `$addFields` stage so they can reference `numeric_age` and `birth_year` from the first stage.
3. **Demo data:** Seed adds a second CT Teacher (T002) with `age: 56` so “Load demo data” shows a non-zero Retirement Risk when scoped to demo (e.g. district 2725).

**Verify from API:**
```bash
# Count and % (no scope = all data)
curl -s "http://localhost:8002/api/executive/teacher-staffing" | python3 -c "import sys,json; d=json.load(sys.stdin); r=d['risk_metrics']; print('retirement_risk_count:', r['retirement_risk_count'], 'retirement_risk_pct:', r['retirement_risk_pct'])"

# Optional: sample docs with age / effective_age (debug=1)
curl -s "http://localhost:8002/api/executive/teacher-staffing?district_code=2725&debug=1" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('_debug_sample', []))"
```

---

## Using real data for Retirement Risk (Teacher & Staffing)

Retirement Risk is computed from the **ctteacher_analytics** collection. To load **real data** from Excel and verify end-to-end:

### Step 1: Get real Excel

- Ensure you have the CT Teacher Excel file (e.g. **8. CTTeacher Data 2025-26.xlsx**) with columns: **Udise Code**, **DOB**, **Doj Service**, **Teaching Staff Name**, **Teaching Staff Code**, **District Name & Code**, **Block Name & Code**, etc.

### Step 2: Load data into MongoDB (choose one)

**Option A – Upload via API (recommended)**  
1. Start the backend (e.g. `uvicorn server:app --host 0.0.0.0 --port 8002`).  
2. Upload the file:
   ```bash
   curl -X POST -F "file=@/path/to/8. CTTeacher Data 2025-26.xlsx" "http://localhost:8002/api/ctteacher/import/upload"
   ```
   Response: `"status": "processing"`. Wait a few seconds for the background job to finish (large files may take 1–2 minutes).  
3. Or use **CT Teacher Dashboard** in the app: use the “Import” option that supports file upload if the UI exposes it.

**Option B – ETL script (local Excel path)**  
1. From `local-hosting-package`:
   ```bash
   python scripts/run_ctteacher_etl.py "/path/to/8. CTTeacher Data 2025-26.xlsx"
   ```
   Or: `CTTEACHER_EXCEL=/path/to/file.xlsx python scripts/run_ctteacher_etl.py`  
2. Script clears **ctteacher_analytics**, loads the Excel, and prints the record count.

### Step 3: Verify from DB / API

1. **Record count in DB**  
   In MongoDB:
   ```javascript
   db.ctteacher_analytics.countDocuments()
   ```
   Should match the number of teacher rows in your Excel (after skipping empty Udise rows).

2. **Retirement Risk from API**  
   ```bash
   curl -s "http://localhost:8002/api/executive/teacher-staffing" | python3 -c "import sys,json; d=json.load(sys.stdin); r=d['risk_metrics']; print('retirement_risk_count:', r['retirement_risk_count'], 'retirement_risk_pct:', r['retirement_risk_pct'])"
   ```
   These values are computed from **ctteacher_analytics** (teachers with effective_age ≥ 55). Confirm the count matches your expectation from the Excel.

### Step 4: Verify on frontend

1. Open **Executive Dashboard** → **Teacher & Staffing** tab.  
2. Check the **Risk Metrics** card: **Retirement Risk** should show the same **count** and **%** as the API.  
3. If the card shows 0 or old numbers, refresh the page; ensure the backend is using the same MongoDB that you loaded.

If the UI still does not show the new data, repeat Step 2 (re-run upload or ETL), then Step 3 and 4 again.
