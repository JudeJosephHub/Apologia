from datetime import datetime
import shutil
from typing import List, Optional
from uuid import uuid4

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile, status

from .config import UPLOAD_DIR
from .db import get_db, init_db
from .schemas import Sermon

app = FastAPI(title="Apologia API", version="0.1.0")


@app.on_event("startup")
def startup_event() -> None:
    init_db()


def _ensure_pptx(file: UploadFile) -> None:
    filename = file.filename or ""
    if not filename.lower().endswith(".pptx"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .pptx files are supported in MVP0.",
        )


def _row_to_sermon(row) -> Sermon:
    created_at = datetime.fromisoformat(row["created_at"])
    return Sermon(
        id=row["id"],
        sermonName=row["sermon_name"],
        seriesName=row["series_name"],
        weekOrDate=row["week_or_date"],
        pastorName=row["pastor_name"],
        status=row["status"],
        filePath=row["file_path"],
        originalFilename=row["original_filename"],
        createdAt=created_at,
    )


@app.post("/sermons", response_model=Sermon, status_code=status.HTTP_201_CREATED)
async def upload_sermon(
    file: UploadFile = File(...),
    weekOrDate: Optional[str] = Form(None),
    seriesName: Optional[str] = Form(None),
    sermonName: str = Form(...),
    pastorName: Optional[str] = Form(None),
    db=Depends(get_db),
) -> Sermon:
    """
    Store a sermon PPTX file with optional metadata.
    """
    _ensure_pptx(file)

    sermon_id = str(uuid4())
    created_at = datetime.utcnow().isoformat()
    sermon_dir = UPLOAD_DIR / sermon_id
    sermon_dir.mkdir(parents=True, exist_ok=True)
    destination = sermon_dir / file.filename
    with destination.open("wb") as out_file:
        shutil.copyfileobj(file.file, out_file)

    db.execute(
        """
        INSERT INTO sermons (
            id, sermon_name, series_name, week_or_date, pastor_name,
            status, file_path, original_filename, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            sermon_id,
            sermonName,
            seriesName,
            weekOrDate,
            pastorName,
            "uploaded",
            str(destination),
            file.filename,
            created_at,
        ),
    )
    db.commit()

    return Sermon(
        id=sermon_id,
        sermonName=sermonName,
        seriesName=seriesName,
        weekOrDate=weekOrDate,
        pastorName=pastorName,
        status="uploaded",
        filePath=str(destination),
        originalFilename=file.filename,
        createdAt=datetime.fromisoformat(created_at),
    )


@app.get("/sermons", response_model=List[Sermon])
def list_sermons(db=Depends(get_db)) -> List[Sermon]:
    rows = db.execute(
        """
        SELECT
            id, sermon_name, series_name, week_or_date, pastor_name,
            status, file_path, original_filename, created_at
        FROM sermons
        ORDER BY created_at DESC
        """
    ).fetchall()
    return [_row_to_sermon(row) for row in rows]
