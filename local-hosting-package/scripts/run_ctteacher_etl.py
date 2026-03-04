#!/usr/bin/env python3
"""
Run CT Teacher ETL only: load Excel into MongoDB ctteacher_analytics.
Use this to load real CT Teacher data so Retirement Risk on Executive Dashboard uses real counts.

Usage:
  # From repo root (local-hosting-package)
  python scripts/run_ctteacher_etl.py [path/to/CTTeacher_Data_2025-26.xlsx]

  # Or set Excel path via env
  CTTEACHER_EXCEL=/path/to/file.xlsx python scripts/run_ctteacher_etl.py

  # Mongo (optional)
  MONGO_URL=mongodb://localhost:27017 DB_NAME=maharashtra_edu python scripts/run_ctteacher_etl.py /path/to/file.xlsx

After running, verify:
  1. API: GET /api/executive/teacher-staffing → risk_metrics.retirement_risk_count, retirement_risk_pct
  2. UI: Executive Dashboard → Teacher & Staffing → Risk Metrics card
"""
import asyncio
import os
import sys
from pathlib import Path

# Add backend so etl_pipeline can be imported
repo_root = Path(__file__).resolve().parent.parent
backend = repo_root / "backend"
if str(backend) not in sys.path:
    sys.path.insert(0, str(backend))

# Load .env from backend
from dotenv import load_dotenv
load_dotenv(backend / ".env")
load_dotenv(repo_root / ".env")


async def main():
    mongo_url = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.environ.get("DB_NAME", "maharashtra_edu")
    excel_path = os.environ.get("CTTEACHER_EXCEL") or (sys.argv[1] if len(sys.argv) > 1 else None)

    if not excel_path or not os.path.isfile(excel_path):
        print("Usage: python scripts/run_ctteacher_etl.py <path/to/CTTeacher_Data.xlsx>")
        print("   or: CTTEACHER_EXCEL=/path/to/file.xlsx python scripts/run_ctteacher_etl.py")
        if excel_path:
            print(f"Error: File not found: {excel_path}")
        sys.exit(1)

    from etl.etl_pipeline import ETLPipeline

    pipeline = ETLPipeline(mongo_url, db_name)
    await pipeline.run_ctteacher_only(excel_path=excel_path)
    count = pipeline.stats.get("ctteacher", 0)
    print()
    print("Verify from API:")
    print('  curl -s "http://localhost:8002/api/executive/teacher-staffing" | python3 -c "import sys,json; d=json.load(sys.stdin); r=d.get(\'risk_metrics\',{}); print(\'retirement_risk_count:\', r.get(\'retirement_risk_count\'), \'retirement_risk_pct:\', r.get(\'retirement_risk_pct\'))"')
    print()
    print("Then open Executive Dashboard → Teacher & Staffing tab and check Risk Metrics card.")


if __name__ == "__main__":
    asyncio.run(main())
