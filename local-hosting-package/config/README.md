# Configuration

Environment and config templates for the Pune Education Dashboard.

| File | Purpose |
|------|---------|
| `env.example` | Example env vars for local/development |
| `env.local.template` | Local overrides template |
| `env.prod.example` | Production env vars example |

Copy the appropriate file to the project root as `.env` and fill in values. Do not commit `.env` (it is gitignored).

**Production database:** The app is linked to MongoDB at `31.97.207.166:27017` (see `env.prod.example` and `docker-compose.prod.yml`). Use `scripts/migrate_to_production_db.py` or `scripts/migrate_db.sh` to push local data to this DB.
