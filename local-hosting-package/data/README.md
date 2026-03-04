# Data

This folder holds data-related assets. The repo may **not** commit large raw dumps (MongoDB `.bson`) or Excel (`.xlsx`) to Git.

### Structure

| Path | Purpose |
|------|---------|
| `excel/` | Source Excel files for ETL/import (e.g. CT Teacher, Aadhaar). Add locally as needed. |
| `mongodb/` | MongoDB dumps (e.g. `maharashtra_edu/` with `.bson` and `.metadata.json`). Use `mongorestore --db maharashtra_edu data/mongodb/maharashtra_edu/` to restore. |

### Notes

- **MongoDB**: Restore a dump into your local Mongo, then start the backend.
- **Excel**: Keep source files here or in `backend/uploads/` if you run ETL/Data Import.
- Duplicate filenames (e.g. `*.metadata 2.json`) in dumps are safe to remove; keep the main `.metadata.json` and `.bson` per collection.


