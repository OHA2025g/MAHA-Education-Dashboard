# Scripts

Utility scripts for the Pune Education Dashboard. Run from the **project root** (`local-hosting-package/`) unless noted.

| Script | Purpose |
|--------|---------|
| `START_SERVICES.sh` | Start backend/frontend (and optionally MongoDB) locally |
| `run_tests.sh` | Run backend pytest from project root |
| `run_comprehensive_tests.sh` | Full comprehensive test suite |
| `create_admin_user.py` | Create admin user in MongoDB (requires backend env) |
| `run_create_admin_in_container.sh` | Create admin user inside Docker backend container |
| `run_ctteacher_etl.py` | Load CT Teacher Excel into MongoDB (Retirement Risk data). Usage: `python scripts/run_ctteacher_etl.py /path/to/CTTeacher_Data.xlsx` |
| `migrate_to_production_db.py` | Migrate data to production DB |
| `migrate_db.sh` | DB migration wrapper |
| `deploy_production.sh` | Production deployment |
| `production_fix_login.sh` | Apply login fix in production |
| `check_test_requirements.py` | Check test dependencies |
| `comprehensive_test_suite.py` | Test suite entry point |
| `setup_test_env.sh` | Set up test environment |
