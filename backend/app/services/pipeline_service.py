from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from sqlmodel import select

from app.core.config import get_settings
from app.db.session import get_session
from app.models.pipeline import Pipeline, RecognitionResult

settings = get_settings()


def _generate_code(name: str) -> str:
    sanitized = "".join(ch for ch in name if ch.isalnum()) or "line"
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{sanitized.lower()}_{timestamp}"


def _excel_path(code: str) -> Path:
    filename = settings.excel_filename_template.format(pipeline_code=code)
    return settings.pipelines_root / filename


def create_pipeline(name: str) -> Pipeline:
    code = _generate_code(name)
    excel_path = _excel_path(code)

    with get_session() as session:
        pipeline = Pipeline(code=code, name=name, excel_path=str(excel_path))
        session.add(pipeline)
        session.commit()
        session.refresh(pipeline)

    excel_path.parent.mkdir(parents=True, exist_ok=True)
    if not excel_path.exists():
        from app.utils.excel_writer import initialize_excel

        initialize_excel(excel_path)
    return pipeline


def list_pipelines() -> list[Pipeline]:
    with get_session() as session:
        statement = select(Pipeline)
        pipelines = list(session.exec(statement).all())
        return pipelines


def get_pipeline(pipeline_id: int) -> Pipeline | None:
    with get_session() as session:
        pipeline = session.get(Pipeline, pipeline_id)
        return pipeline


def _count_scans(session, pipeline_id: int) -> int:
    statement = select(RecognitionResult).where(RecognitionResult.pipeline_id == pipeline_id)
    return len(session.exec(statement).all())


def store_result(pipeline: Pipeline, result_data: dict) -> RecognitionResult:
    excel_path = Path(pipeline.excel_path)
    excel_path.parent.mkdir(parents=True, exist_ok=True)

    with get_session() as session:
        # 确保 pipeline.id 不为空
        if pipeline.id is None:
            raise ValueError("Pipeline ID is None, cannot create RecognitionResult")
        
        result = RecognitionResult(pipeline_id=pipeline.id, **result_data)
        session.add(result)
        session.commit()
        session.refresh(result)

    from app.utils.excel_writer import append_result

    append_result(excel_path, result)
    return result
