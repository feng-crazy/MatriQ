from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.core.config import Settings, get_settings
from app.core.logger import get_logger
from app.schemas.pipeline import PipelineCreate, PipelineDetail, PipelineSummary, RecognitionResponse
from app.db.session import get_session
from app.services.pipeline_service import create_pipeline, get_pipeline, list_pipelines, store_result, _count_scans
from app.services.ocr_service import OcrServiceError, get_ocr_service
from app.services.parser_service import parse_ocr_payload

logger = get_logger("routes.pipelines")

router = APIRouter(prefix="/pipelines", tags=["流水线管理"])


@router.get("", response_model=list[PipelineSummary])
def get_pipelines():
    logger.info("获取所有流水线列表")
    pipelines = list_pipelines()
    logger.debug(f"找到 {len(pipelines)} 个流水线")
    
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
    
    logger.info(f"返回 {len(summaries)} 个流水线摘要")
    return summaries


@router.post("", response_model=PipelineDetail, status_code=201)
def create_pipeline_endpoint(payload: PipelineCreate):
    logger.info(f"创建新流水线: {payload.name}")
    pipeline = create_pipeline(payload.name)
    logger.info(f"流水线创建成功: ID={pipeline.id}, Code={pipeline.code}")
    
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
    logger.info(f"获取流水线详情: ID={pipeline_id}")
    pipeline = get_pipeline(pipeline_id)
    if not pipeline:
        logger.warning(f"流水线不存在: ID={pipeline_id}")
        raise HTTPException(status_code=404, detail="流水线不存在")
    
    with get_session() as session:
        total_scans = _count_scans(session, pipeline.id) if pipeline.id is not None else 0
    
    logger.debug(f"流水线详情: {pipeline.code}, 扫描次数: {total_scans}")
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
    logger.info(f"开始扫描图像: 流水线ID={pipeline_id}, 文件名={image.filename}")
    pipeline = get_pipeline(pipeline_id)
    if not pipeline:
        logger.warning(f"流水线不存在: ID={pipeline_id}")
        raise HTTPException(status_code=404, detail="流水线不存在")

    ext = Path(image.filename or "").suffix.lower()
    if ext not in settings.allowed_extensions:
        logger.warning(f"不支持的文件格式: {ext}")
        raise HTTPException(status_code=400, detail="文件格式不支持")

    content = image.file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_upload_mb:
        logger.warning(f"文件大小超过限制: {size_mb:.2f}MB > {settings.max_upload_mb}MB")
        raise HTTPException(status_code=400, detail="文件超过大小限制")

    logger.debug(f"调用OCR服务处理图像: 大小={len(content)} bytes")
    ocr_client = get_ocr_service()
    try:
        ocr_payload = ocr_client.classify_and_recognize(content, image.filename or "upload.jpg")
        logger.debug("OCR处理完成")
    except OcrServiceError as exc:
        logger.error(f"OCR服务错误: {exc}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    normalized = parse_ocr_payload(ocr_payload)
    normalized.setdefault("raw_ocr_text", "")
    normalized.setdefault("image_filename", image.filename)
    scan_time = datetime.utcnow()
    normalized.setdefault("scan_time", scan_time)
    normalized.setdefault("recognized_at", scan_time)

    db_payload = {
        "material_code": normalized.get("material_code"),
        "quantity": normalized.get("quantity"),
        "batch": normalized.get("batch"),
        "date": normalized.get("date"),
        "brand": normalized.get("brand"),
        "electrical_characteristics": normalized.get("electrical_characteristics"),
        "raw_ocr_text": normalized.get("raw_ocr_text"),
        "image_filename": normalized.get("image_filename"),
        "recognized_at": scan_time,  # 确保是 datetime 对象而不是字符串
    }

    logger.debug(f"存储识别结果: {db_payload}")
    result = store_result(pipeline, db_payload)
    logger.info(f"扫描结果存储成功: 流水线={pipeline.code}, 物料代码={result.material_code}")

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
    logger.info(f"导出Excel文件: 流水线ID={pipeline_id}")
    pipeline = get_pipeline(pipeline_id)
    if not pipeline:
        logger.warning(f"流水线不存在: ID={pipeline_id}")
        raise HTTPException(status_code=404, detail="流水线不存在")

    excel_path = Path(pipeline.excel_path)
    if not excel_path.exists():
        logger.warning(f"Excel文件不存在: {excel_path}")
        raise HTTPException(status_code=404, detail="Excel 文件不存在")

    logger.info(f"返回Excel文件: {excel_path.name}")
    return FileResponse(
        path=excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=excel_path.name,
    )
