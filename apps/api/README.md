# API (backend)

FastAPI service that powers the Apologia backend. Milestone A implements a
simple flow to upload sermon PPTX files and list stored sermons (metadata +
file path). Slide extraction and AI-assisted processing will be layered on
later milestones.

## Configuration (Required for Bedrock)

The analyzer uses Amazon Bedrock Agents. Do NOT commit secrets.

Create a local `apps/api/.env` file (gitignored) with:

```
AWS_REGION=us-east-1
BEDROCK_AGENT_ID=your_agent_id
BEDROCK_AGENT_ALIAS_ID=your_alias_id
```

You also need AWS credentials on your machine (e.g. `aws configure`).
If these are missing or invalid, the `/analyze` endpoint will fail with
access errors.

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
