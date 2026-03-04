# Project Structure

This document describes the organization and structure of the Pune School Dashboard project.

## 📁 Directory Structure

```
local-hosting-package/
├── backend/                    # FastAPI backend application
│   ├── data_import/           # Data import utilities
│   ├── etl/                    # ETL pipeline
│   ├── models/                 # Pydantic models
│   ├── routers/                # API route handlers
│   ├── tests/                  # Test suite
│   ├── utils/                  # Utility functions
│   ├── uploads/                # Uploaded files (Excel)
│   ├── venv/                   # Python virtual environment (gitignored)
│   ├── Dockerfile              # Backend Docker image
│   ├── pytest.ini              # Pytest configuration
│   ├── requirements.txt        # Python dependencies
│   └── server.py               # FastAPI application entry point
│
├── frontend/                   # React frontend application
│   ├── public/                 # Static assets
│   │   ├── geo/                # GeoJSON files
│   │   └── index.html          # HTML template
│   ├── src/                    # Source code
│   │   ├── components/        # React components
│   │   │   └── ui/            # UI component library
│   │   ├── context/           # React context providers
│   │   ├── hooks/             # Custom React hooks
│   │   ├── lib/               # Utility libraries
│   │   └── pages/             # Page components
│   ├── scripts/               # Build scripts
│   ├── Dockerfile             # Frontend Docker image
│   ├── nginx.conf             # Nginx configuration
│   └── package.json           # Node.js dependencies
│
├── config/                     # Configuration templates (see config/README.md)
│   ├── env.example             # Environment variables template
│   ├── env.local.template      # Local environment template
│   ├── env.prod.example        # Production env example
│   └── README.md
│
├── data/                       # Data files (see data/README.md)
│   ├── excel/                  # Source Excel files
│   ├── mongodb/                # MongoDB dumps (e.g. maharashtra_edu/)
│   └── README.md
│
├── docs/                       # All documentation (see docs/README.md)
│   ├── api/                    # API reference
│   ├── deployment/             # Docker, production, login fixes
│   ├── development/            # Development guides
│   ├── guides/                 # User/feature guides (Executive Dashboard, metrics, etc.)
│   ├── testing/                # Test docs and outputs (TESTING.md, test_results.txt, etc.)
│   ├── archive/                # One-off completed notes
│   └── README.md               # Documentation index
│
├── scripts/                    # Utility scripts (see scripts/README.md)
│   ├── run_comprehensive_tests.sh
│   ├── run_tests.sh
│   ├── run_ctteacher_etl.py
│   ├── START_SERVICES.sh
│   ├── create_admin_user.py
│   └── ...
│
├── docker-compose.yml          # Docker Compose configuration
├── docker-compose.prod.yml     # Production override
├── Makefile                    # Make commands
├── README.md                   # Main project README
└── PROJECT_STRUCTURE.md       # This file
```

## 📂 Key Directories

### Backend (`backend/`)

- **`routers/`**: API route handlers organized by feature
  - `auth.py` - Authentication endpoints
  - `executive.py` - Executive dashboard endpoints
  - `ctteacher.py` - CTTeacher analytics endpoints
  - `apaar.py` - APAAR entry status endpoints
  - `classrooms_toilets.py` - Infrastructure endpoints
  - And more...

- **`models/`**: Pydantic models for data validation
- **`utils/`**: Utility functions (auth, scope, etc.)
- **`tests/`**: Comprehensive test suite
  - `test_api_endpoints.py` - API endpoint tests
  - `test_security.py` - Security tests
  - `test_performance.py` - Performance tests
  - And more...

- **`etl/`**: ETL pipeline for data import
- **`data_import/`**: Data import utilities

### Frontend (`frontend/`)

- **`src/pages/`**: Page components (dashboards)
  - `ExecutiveDashboard.jsx`
  - `CTTeacherDashboard.jsx`
  - `APAARDashboard.jsx`
  - And more...

- **`src/components/`**: Reusable components
  - `ui/` - UI component library (shadcn/ui)
  - Dashboard-specific components

- **`src/context/`**: React context providers
  - `ScopeContext.jsx` - Scope/filter context

- **`public/geo/`**: GeoJSON files for maps

### Documentation (`docs/`)

- **`deployment/`**: Docker, production deployment, login fixes
- **`testing/`**: Testing docs, test results, and reports
- **`guides/`**: Executive Dashboard verification, metric info, feature guides
- **`archive/`**: Completed one-off notes
- **`api/`**: API reference (Swagger at /docs when backend runs)
- **`development/`**: Development guides

### Scripts (`scripts/`)

- **`START_SERVICES.sh`**: Start Docker or local services
- **`run_tests.sh`**: Run backend pytest
- **`run_comprehensive_tests.sh`**: Full test suite (writes to docs/testing/)
- **`run_ctteacher_etl.py`**: Load CT Teacher Excel into MongoDB
- **`create_admin_user.py`**, **`setup_test_env.sh`**, etc. — see `scripts/README.md`

### Configuration (`config/`)

- **`env.example`**, **`env.local.template`**, **`env.prod.example`**: Env templates (copy to root as `.env`)

### Data (`data/`)

- **`excel/`**: Source Excel files (10 datasets)
- **`mongodb/`**: MongoDB database dumps

## 🔧 Configuration Files

### Root Level

- **`docker-compose.yml`**: Main Docker Compose configuration
- **`docker-compose.prod.yml`**: Production overrides
- **`Makefile`**: Common commands (build, up, down, etc.)
- **`.dockerignore`**: Files excluded from Docker builds

### Backend

- **`requirements.txt`**: Python dependencies
- **`pytest.ini`**: Pytest configuration
- **`Dockerfile`**: Backend Docker image definition

### Frontend

- **`package.json`**: Node.js dependencies
- **`Dockerfile`**: Frontend Docker image definition
- **`nginx.conf`**: Nginx configuration for production

## 📝 Documentation Files

### Root (minimal)

- **`README.md`**: Main project README and setup
- **`PROJECT_STRUCTURE.md`**: This file — all other docs live under **`docs/`**

### Docs index

- **`docs/README.md`**: Index of all documentation (deployment, testing, guides, archive)

## 🚀 Quick Navigation

### Starting the Project

```bash
# Using Docker (recommended)
docker compose up -d

# Or using scripts
./scripts/START_SERVICES.sh
```

### Running Tests

```bash
# From project root
cd backend && pytest

# Or using script
./scripts/run_tests.sh
```

### Accessing Documentation

- Main README: `README.md`
- Docker Guide: `docs/deployment/DOCKER_DEPLOYMENT.md`
- Testing Guide: `docs/testing/TESTING.md`
- API Docs: http://localhost:8002/docs (when running)

## 📊 File Organization Principles

1. **Separation of Concerns**: Backend and frontend are separate
2. **Documentation Centralization**: All docs in `docs/`
3. **Script Centralization**: All scripts in `scripts/`
4. **Configuration Templates**: All config templates in `config/`
5. **Data Isolation**: All data files in `data/`
6. **Test Organization**: Tests mirror source structure

## 🔄 Migration Notes

If you're migrating from the old structure:

- Documentation moved from root → `docs/`
- Scripts moved from `backend/` → `scripts/`
- Config templates moved → `config/`
- Test docs moved from `backend/` → `docs/testing/`

All references have been updated in:
- `README.md`
- `Makefile`
- Scripts in `scripts/`

## 📚 Related Documentation

- [Main README](./README.md)
- [Docker Deployment](./docs/deployment/DOCKER_DEPLOYMENT.md)
- [Testing Guide](./docs/testing/TESTING.md)
- [Documentation Index](./docs/README.md)

