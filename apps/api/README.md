# API (backend)

FastAPI service that powers the Apologia backend. Milestone A implements a
simple flow to upload sermon PPTX files and list stored sermons (metadata +
file path). Slide extraction and AI-assisted processing will be layered on
later milestones.

## Getting Started

```bash
cd apps/api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is then available at `http://127.0.0.1:8000` with interactive docs at
`/docs`.

## Endpoints (MVP0 Milestone A)

### `POST /sermons`
Multipart form request that accepts:
- `file` — PPTX upload (required)
- `sermonName` — string (required)
- `seriesName`, `weekOrDate`, `pastorName` — optional strings

Stores the binary on disk under `apps/api/uploads/{sermonId}` and persists the
metadata + file path in SQLite (`apps/api/data/sermons.db`). Responds with the
stored sermon record.

### `GET /sermons`
Returns all stored sermons ordered by `createdAt` (newest first).

## Sample Requests

```bash
curl -X POST http://localhost:8000/sermons \
  -F "sermonName=Hope in Christ" \
  -F "pastorName=Jude" \
  -F "file=@/path/to/sermon.pptx"

curl http://localhost:8000/sermons
```
