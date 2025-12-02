from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import Settings, get_settings
from app.schemas.pipeline import PipelineCreate, PipelineDetail, PipelineSummary, RecognitionResponse
from app.services.pipeline_service import create_pipeline, get_pipeline, list_pipelines, store_result, _count_scans, get_session
from app.services.ocr_service import OcrServiceError, get_ocr_service
from app.services.parser_service import parse_ocr_payload

router = APIRouter(prefix="/pipelines", tags=["流水线管理"])


@router.get("", response_model=list[PipelineSummary])
def get_pipelines():
    pipelines = list_pipelines()
    summaries = []
    for pipeline in pipelines:
        with get_session() as session:
            total_scans = _count_scans(session, pipeline.id) if pipeline.id is not None else 0
        summaries.append(
            PipelineSummary(
                id=pipeline.id if pipeline.id is not None else 0,  # type: ignore
                code=pipeline.code,
                name=pipeline.name,
                created_at=pipeline.created_at,
                total_scans=total_scans,
            )
        )
    return summaries


@router.post("", response_model=PipelineDetail, status_code=201)
def create_pipeline_endpoint(payload: PipelineCreate):
    pipeline = create_pipeline(payload.name)
    return PipelineDetail(
        id=pipeline.id if pipeline.id is not None else 0,  # type: ignore
        code=pipeline.code,
        name=pipeline.name,
        created_at=pipeline.created_at,
        total_scans=0,
        excel_path=pipeline.excel_path,
    )


@router.get("/{pipeline_id}", response_model=PipelineDetail)
def get_pipeline_endpoint(pipeline_id: int):
    pipeline = get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="流水线不存在")
    
    with get_session() as session:
        total_scans = _count_scans(session, pipeline.id) if pipeline.id is not None else 0
    
    return PipelineDetail(
        id=pipeline.id if pipeline.id is not None else 0,  # type: ignore
        code=pipeline.code,
        name=pipeline.name,
        created_at=pipeline.created_at,
        total_scans=total_scans,
        excel_path=pipeline.excel_path,
    )


@router.post("/{pipeline_id}/scan", response_model=RecognitionResponse)
def scan_image(
    pipeline_id: int,
    image: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
):
    pipeline = get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="流水线不存在")

    ext = Path(image.filename or "").suffix.lower()
    if ext not in settings.allowed_extensions:
        raise HTTPException(status_code=400, detail="文件格式不支持")

    content = image.file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_upload_mb:
        raise HTTPException(status_code=400, detail="文件超过大小限制")

    ocr_client = get_ocr_service()
    try:
        ocr_payload = ocr_client.classify_and_recognize(content, image.filename or "upload.jpg")
    except OcrServiceError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    normalized = parse_ocr_payload(ocr_payload)
    normalized.setdefault("raw_ocr_text", "")
    normalized.setdefault("image_filename", image.filename)
    normalized.setdefault("scan_time", datetime.utcnow())
    normalized.setdefault("recognized_at", normalized["scan_time"])

    db_payload = {
        "material_code": normalized.get("material_code"),
        "quantity": normalized.get("quantity"),
        "batch": normalized.get("batch"),
        "date": normalized.get("date"),
        "brand": normalized.get("brand"),
        "electrical_characteristics": normalized.get("electrical_characteristics"),
        "raw_ocr_text": normalized.get("raw_ocr_text"),
        "image_filename": normalized.get("image_filename"),
        "recognized_at": normalized.get("recognized_at"),
    }

    result = store_result(pipeline, db_payload)

    return RecognitionResponse(
        pipeline_id=pipeline.id if pipeline.id is not None else 0,  # type: ignore,
        pipeline_code=pipeline.code,
        material_code=result.material_code,
        quantity=result.quantity,
        batch=result.batch,
        date=result.date,
        brand=result.brand,
        electrical_characteristics=result.electrical_characteristics,
        raw_ocr_text=result.raw_ocr_text or "",
        image_filename=result.image_filename or image.filename or "",  # type: ignore,
        scan_time=result.recognized_at,
    )


@router.get("/{pipeline_id}/export")
def export_excel(pipeline_id: int):
    pipeline = get_pipeline(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="流水线不存在")

    excel_path = Path(pipeline.excel_path)
    if not excel_path.exists():
        raise HTTPException(status_code=404, detail="Excel 文件不存在")

    return FileResponse(
        path=excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=excel_path.name,
    )
