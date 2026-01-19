from datetime import datetime
from pathlib import Path
from typing import Type, TypeVar

from .config import STORAGE_DIR
from .schemas import AnalysisDocument, DecisionsDocument

SERMONS_DIR = STORAGE_DIR / "sermons"

T = TypeVar("T", AnalysisDocument, DecisionsDocument)


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _model_to_json_str(model) -> str:
    if hasattr(model, "model_dump_json"):
        return model.model_dump_json(indent=2)
    return model.json(indent=2)


def _model_from_json(model_cls: Type[T], raw: str) -> T:
    if hasattr(model_cls, "model_validate_json"):
        return model_cls.model_validate_json(raw)
    return model_cls.parse_raw(raw)


def sermon_state_dir(sermon_id: str) -> Path:
    return SERMONS_DIR / sermon_id


def analysis_path(sermon_id: str) -> Path:
    return sermon_state_dir(sermon_id) / "analysis.json"


def decisions_path(sermon_id: str) -> Path:
    return sermon_state_dir(sermon_id) / "decisions.json"


def init_sermon_state(sermon_id: str) -> None:
    _ensure_dir(SERMONS_DIR)
    sermon_dir = sermon_state_dir(sermon_id)
    _ensure_dir(sermon_dir)

    analysis_file = analysis_path(sermon_id)
    if not analysis_file.exists():
        analysis = AnalysisDocument(
            sermonId=sermon_id,
            createdAt=datetime.utcnow(),
            slides=[],
        )
        analysis_file.write_text(_model_to_json_str(analysis))

    decisions_file = decisions_path(sermon_id)
    if not decisions_file.exists():
        decisions = DecisionsDocument(
            sermonId=sermon_id,
            updatedAt=datetime.utcnow(),
            slides=[],
        )
        decisions_file.write_text(_model_to_json_str(decisions))


def load_analysis(sermon_id: str) -> AnalysisDocument:
    raw = analysis_path(sermon_id).read_text()
    return _model_from_json(AnalysisDocument, raw)


def save_analysis(analysis: AnalysisDocument) -> None:
    path = analysis_path(analysis.sermonId)
    path.write_text(_model_to_json_str(analysis))


def load_decisions(sermon_id: str) -> DecisionsDocument:
    raw = decisions_path(sermon_id).read_text()
    return _model_from_json(DecisionsDocument, raw)


def save_decisions(decisions: DecisionsDocument) -> None:
    path = decisions_path(decisions.sermonId)
    path.write_text(_model_to_json_str(decisions))
