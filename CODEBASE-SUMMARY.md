# Apologia Codebase Summary

**Project**: MVP0 Sermon PPTX Proofreading Platform  
**Status**: ✅ Running (http://127.0.0.1:8000)  
**Last Updated**: January 19, 2026

---

## 📋 Project Overview

Apologia is a FastAPI backend service that enables pastors to:
1. Upload sermon PPTX files with metadata
2. Extract and review slide-by-slide content
3. Generate AI-assisted proofreading suggestions
4. Apply accepted changes and download updated PPTXs

---

## 🗂️ Project Structure

```
/apps/api/
├── app/
│   ├── __init__.py           # Package marker
│   ├── main.py               # FastAPI application & endpoints (429 lines)
│   ├── config.py             # Configuration & directory setup
│   ├── db.py                 # SQLite initialization & connection mgmt
│   ├── schemas.py            # Pydantic models for API data
│   └── state.py              # JSON-based state persistence (analysis/decisions)
├── data/                     # SQLite database storage
├── uploads/                  # PPTX file storage by sermon ID
├── storage/                  # Generated outputs (updated PPTXs)
├── requirements.txt          # Python dependencies
└── README.md                 # Getting started guide

/apps/web/
├── index.html               # Frontend UI
├── app.js                   # Frontend logic
├── styles.css               # Styling
└── README.md
```

---

## 🔧 Technology Stack

**Backend:**
- **Framework**: FastAPI 0.110.0
- **Server**: Uvicorn 0.27.1 (ASGI)
- **Database**: SQLite 3 (synchronous)
- **PPTX Processing**: python-pptx 0.6.23
- **HTTP Client**: httpx 0.27.2 (for testing)
- **File Uploads**: python-multipart 0.0.9

**Frontend:**
- Vanilla JavaScript
- HTML5
- CSS3

---

## 📦 Core Modules Breakdown

### 1. **config.py** - Configuration Management
```python
- BASE_DIR: Project root
- DATA_DIR: SQLite database storage
- UPLOAD_DIR: Sermon PPTX uploads (by ID)
- STORAGE_DIR: Generated output files
- DB_PATH: SQLite database file location
```
**Key Feature**: Auto-creates directories on import

### 2. **db.py** - Database Layer
```python
Functions:
- init_db(): Creates sermons table with schema
- get_db(): FastAPI dependency for DB connections per request
  
Schema:
  sermons (
    id TEXT PRIMARY KEY,
    sermon_name TEXT,
    series_name TEXT,
    week_or_date TEXT,
    pastor_name TEXT,
    status TEXT,
    file_path TEXT,
    original_filename TEXT,
    created_at TEXT,
    INDEX on created_at DESC
  )
```

### 3. **schemas.py** - Data Models (Pydantic)
```python
Models:
- Sermon: Metadata + upload status
- SlideContent: Slide ID, number, extracted text
- Suggestion: Proofreading suggestion (id, category, original, proposed)
- SlideAnalysis: Analysis for a single slide
- AnalysisDocument: All analyses for a sermon
- SlideDecision: User decision per slide
- DecisionsDocument: All decisions for a sermon
- SuggestionDecision: Accept/reject/edit decision
```

### 4. **state.py** - State Persistence
```python
Persistence Strategy:
- JSON files stored in STORAGE_DIR/sermons/{sermon_id}/
- analysis.json: Slide analysis data
- decisions.json: User decisions

Functions:
- init_sermon_state(): Create initial state files
- load_analysis()/save_analysis(): Manage analysis persistence
- load_decisions()/save_decisions(): Manage decision persistence
```

### 5. **main.py** - FastAPI Application (429 lines)

#### Core Endpoints

**Sermon Management:**
```
POST /sermons
  Upload PPTX + metadata → returns Sermon record
  
GET /sermons
  List all sermons (newest first)

GET /sermons/{sermon_id}/slides
  Extract text from all slides in a sermon
```

**Analysis & Suggestions:**
```
POST /sermons/{sermon_id}/slides/{slide_number}/analyze
  Analyze a single slide → returns suggestions
  
GET /sermons/{sermon_id}/analysis
  Get all analysis for a sermon
  
GET /sermons/{sermon_id}/slides/{slide_number}/analysis
  Get analysis for a specific slide
```

**Decision Management:**
```
POST /sermons/{sermon_id}/slides/{slide_number}/decisions
  Save user decisions (accept/reject/edit)
  
GET /sermons/{sermon_id}/decisions
  Retrieve all decisions for a sermon
```

**PPTX Generation & Download:**
```
POST /sermons/{sermon_id}/generate-updated-pptx
  Generate updated PPTX from accepted decisions
  
GET /sermons/{sermon_id}/download-updated-pptx
  Download the generated PPTX file
```

#### Helper Functions

```python
_ensure_pptx(file): Validate file is .pptx format
_row_to_sermon(row): Convert DB row to Sermon model
_extract_slide_text(slide): Extract text from slide shapes + notes
_resolve_upload_path(): Resolve file path from multiple sources
_ensure_sermon_exists(): Validate sermon exists in DB
_get_presentation(): Load PowerPoint file
_analyze_text_stub(): Placeholder for AI suggestions (currently returns [])
_output_pptx_path(): Determine output PPTX file path
_apply_text_replacements(): Replace text in slide shapes + notes
```

---

## 🚀 Running the Application

### Prerequisites
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Start Server
```bash
cd apps/api
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Access Points
- **API Base**: http://127.0.0.1:8000
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

---

## 📊 Current Data State

**Existing Sermons** (from database):
1. "Test Sermon 1" by Jermiah (10/28/1987, TestSeries 1)
2. "Test Sermon" by Tester (2024-09-01, Test Series)

All test PPTXs are stored in `uploads/{sermon_id}/` directories.

---

## 🔄 Data Flow

### Upload Flow
```
User uploads PPTX + metadata
  ↓
POST /sermons endpoint
  ↓
Validate file is .pptx
  ↓
Generate UUID for sermon
  ↓
Save file to uploads/{id}/
  ↓
Store metadata in SQLite
  ↓
Initialize state files (analysis.json, decisions.json)
  ↓
Return Sermon record
```

### Analysis Flow
```
User requests slide analysis
  ↓
Load PPTX from uploads/
  ↓
Extract text from slide
  ↓
Call _analyze_text_stub() [placeholder]
  ↓
Store analysis in JSON state
  ↓
Return SlideAnalysis
```

### Decision & Generation Flow
```
User makes accept/reject/edit decisions
  ↓
POST /slides/{number}/decisions
  ↓
Load analysis + decisions
  ↓
Build replacement map
  ↓
POST /generate-updated-pptx
  ↓
Apply replacements to slide text
  ↓
Save output PPTX to storage/
  ↓
GET /download-updated-pptx returns file
```

---

## 🛠️ Recent Implementation Details

### Key Features Implemented

✅ **File Upload & Storage**
- Multipart form handling
- File validation (.pptx only)
- Directory structure per sermon

✅ **Text Extraction**
- Extracts from slide shapes (title, body)
- Extracts from notes section
- Preserves formatting context

✅ **State Management**
- JSON-based persistence (no extra DB tables)
- Sermon-isolated state directories
- Handles concurrent sermon processing

✅ **PPTX Manipulation**
- Text replacement in shapes
- Text replacement in notes
- Preserves layout/formatting
- Binary file download support

✅ **Error Handling**
- PPTX validation
- 404 for missing sermons/slides
- 400 for invalid requests
- Graceful missing file handling

### CORS Configuration
```python
allow_origins=["*"]  # Ready for web frontend
```

---

## 📝 API Contract Compliance

The implementation fully adheres to the API-CONTRACT.md specification:

| Endpoint | Status | Response Model |
|----------|--------|-----------------|
| POST /sermons | ✅ | Sermon |
| GET /sermons | ✅ | List[Sermon] |
| GET /sermons/{id}/slides | ✅ | List[SlideContent] |
| POST /slides/{num}/analyze | ✅ | SlideAnalysis |
| GET /analysis | ✅ | AnalysisDocument |
| GET /slides/{num}/analysis | ✅ | SlideAnalysis |
| POST /slides/{num}/decisions | ✅ | SlideDecision |
| GET /decisions | ✅ | DecisionsDocument |
| POST /generate-updated-pptx | ✅ | {status: "ready"} |
| GET /download-updated-pptx | ✅ | FileResponse |

---

## 🎯 MVP0 Charter Alignment

| Feature | Status | Location |
|---------|--------|----------|
| Upload PPTX + metadata | ✅ | POST /sermons |
| Extract slide text | ✅ | main.py:_extract_slide_text() |
| Generate suggestions | 🔄 | main.py:_analyze_text_stub() (placeholder) |
| Review UI | 🔄 | Frontend needed |
| Accept/Reject/Edit decisions | ✅ | POST /slides/{num}/decisions |
| Generate updated PPTX | ✅ | POST /generate-updated-pptx |
| Download updated PPTX | ✅ | GET /download-updated-pptx |
| Store sermon + decisions | ✅ | SQLite + JSON state |

---

## ⚙️ Configuration Notes

**Port**: 8000 (configurable via uvicorn args)  
**Reload**: Enabled for development (watches for file changes)  
**CORS**: All origins allowed (suitable for MVP)  
**Database**: SQLite (file-based, no external service needed)  
**State**: JSON files (easier debugging than DB tables)

---

## 🐛 Known Limitations

1. **AI Suggestions Placeholder**: `_analyze_text_stub()` returns empty list. Real implementation needed.
2. **Synchronous DB**: SQLite with `check_same_thread=False` (works but not ideal for production)
3. **No Authentication**: MVP0 assumes single-user/local environment
4. **No Async File I/O**: Using synchronous file operations

---

## 📈 Next Steps (Post-MVP0)

1. Implement real suggestion engine (replace _analyze_text_stub)
2. Add frontend UI for review workflow
3. Add authentication/multi-user support
4. Migrate to async database (PostgreSQL)
5. Add logging and monitoring
6. Add sermon history/versioning
7. Add batch processing

---

## 🔗 Related Documentation

- [MVP0-CHARTER.md](./docs/MVP0-CHARTER.md) - Project requirements
- [API-CONTRACT.md](./docs/API-CONTRACT.md) - Endpoint specifications
- [apps/api/README.md](./apps/api/README.md) - Setup instructions
- [apps/web/README.md](./apps/web/README.md) - Frontend information

---

**Server Status**: ✅ Running on http://127.0.0.1:8000  
**Interactive API Docs**: http://127.0.0.1:8000/docs
