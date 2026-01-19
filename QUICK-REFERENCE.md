# Quick Reference - Apologia API

## Server Status
✅ **Running on**: http://127.0.0.1:8000 (Process ID: 48659)

## Quick API Tests

### List all sermons
```bash
curl http://127.0.0.1:8000/sermons
```

### Upload a sermon
```bash
curl -X POST http://127.0.0.1:8000/sermons \
  -F "sermonName=My Sermon" \
  -F "seriesName=Series Name" \
  -F "weekOrDate=2024-01-19" \
  -F "pastorName=Your Name" \
  -F "file=@/path/to/sermon.pptx"
```

### Get slides from a sermon
```bash
curl http://127.0.0.1:8000/sermons/{sermon_id}/slides
```

### Analyze a slide
```bash
curl -X POST http://127.0.0.1:8000/sermons/{sermon_id}/slides/1/analyze
```

### Save decisions for a slide
```bash
curl -X POST http://127.0.0.1:8000/sermons/{sermon_id}/slides/1/decisions \
  -H "Content-Type: application/json" \
  -d '{
    "decisions": [
      {
        "suggestionId": "sug-1",
        "decision": "accepted"
      }
    ]
  }'
```

### Generate updated PPTX
```bash
curl -X POST http://127.0.0.1:8000/sermons/{sermon_id}/generate-updated-pptx
```

### Download updated PPTX
```bash
curl http://127.0.0.1:8000/sermons/{sermon_id}/download-updated-pptx \
  -o updated_sermon.pptx
```

## Documentation Links
- **Interactive API Docs**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc
- **OpenAPI JSON**: http://127.0.0.1:8000/openapi.json

## Project Files
- Backend: `/apps/api/app/`
  - main.py (429 lines) - All endpoints
  - config.py - Configuration
  - db.py - SQLite management
  - schemas.py - Pydantic models
  - state.py - JSON persistence

- Database: `/apps/api/data/sermons.db`
- Uploads: `/apps/api/uploads/{sermon_id}/`
- Outputs: `/apps/api/storage/sermons/{sermon_id}/output.pptx`

## Stop Server
```bash
kill 48659
```

## Restart Server
```bash
cd /Users/judejosephmanuel/Documents/GitHub/Apologia/apps/api && \
nohup /Users/judejosephmanuel/Documents/GitHub/Apologia/.venv/bin/python \
-m uvicorn app.main:app --host 127.0.0.1 --port 8000 > /tmp/apologia.log 2>&1 &
```

## Key Statistics
- **Total API Endpoints**: 10
- **Total Lines of Code**: 
  - main.py: 429 lines
  - schemas.py: ~80 lines
  - state.py: ~70 lines
  - db.py: ~50 lines
  - config.py: ~15 lines
- **Dependencies**: 5 packages
- **Database Tables**: 1 (sermons)
- **Sample Data**: 2 existing sermons

## Recent Implementation Status
✅ File upload & storage
✅ Text extraction from slides
✅ Database persistence
✅ Decision tracking
✅ PPTX generation & download
✅ Error handling & validation
🔄 AI suggestion engine (placeholder - needs implementation)
🔄 Frontend UI (separate repo/folder)

## File Locations
```
Apologia/
├── CODEBASE-SUMMARY.md          ← Full documentation
├── QUICK-REFERENCE.md           ← This file
├── docs/
│   ├── MVP0-CHARTER.md          ← Project requirements
│   └── API-CONTRACT.md          ← API specifications
└── apps/
    ├── api/
    │   ├── app/main.py          ← FastAPI app
    │   ├── data/                ← SQLite DB
    │   ├── uploads/             ← PPTX files
    │   └── storage/             ← Generated outputs
    └── web/                     ← Frontend (TODO)
```

## Environment
- Python: 3.12.3
- OS: macOS
- Virtual Env: `/Users/judejosephmanuel/Documents/GitHub/Apologia/.venv/`
