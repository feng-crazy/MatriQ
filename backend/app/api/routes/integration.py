from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException

from app.core.config import get_settings
from app.schemas.pipeline import ScanResult
from app.services.pipeline_service import get_pipeline, store_result

router = APIRouter(prefix="", tags=["系统集成"])

settings = get_settings()


@router.post("/scan-result", status_code=201)
def receive_scan_result(
    payload: ScanResult,
    pipeline_id: int | None = None,
    pipeline_code: str | None = None,
    x_api_key: str = Header(None),
):
    """
    接收外部系统推送的识别结果
    
    参数:
    - payload: 识别结果数据
    - pipeline_id: 流水线ID（与 pipeline_code 二选一）
    - pipeline_code: 流水线编码（与 pipeline_id 二选一）
    - x_api_key: API密钥（用于认证）
    
    注意：必须提供 pipeline_id 或 pipeline_code 之一，用于指定结果存储到哪个流水线
    """
    if settings.ocr_api_key and x_api_key != settings.ocr_api_key:
        raise HTTPException(status_code=401, detail="未授权")
    
    # 确定目标流水线
    pipeline = None
    if pipeline_id:
        pipeline = get_pipeline(pipeline_id)
    elif pipeline_code:
        # 需要通过 code 查找流水线
        from app.db.session import get_session
        from app.models.pipeline import Pipeline
        from sqlmodel import select
        
        with get_session() as session:
            statement = select(Pipeline).where(Pipeline.code == pipeline_code)
            pipeline = session.exec(statement).first()
    else:
        raise HTTPException(
            status_code=400,
            detail="必须提供 pipeline_id 或 pipeline_code 参数以指定目标流水线"
        )
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="指定的流水线不存在")
    
    # 将 ScanResult 转换为数据库格式并存储
    db_payload = {
        "material_code": payload.material_code,
        "quantity": payload.quantity,
        "batch": payload.batch,
        "date": payload.date,
        "brand": payload.brand,
        "electrical_characteristics": payload.electrical_characteristics,
        "raw_ocr_text": payload.raw_ocr_text,
        "image_filename": payload.image_filename,
        "recognized_at": payload.scan_time,
    }
    
    result = store_result(pipeline, db_payload)
    
    return {
        "status": "accepted",
        "pipeline_id": pipeline.id,
        "pipeline_code": pipeline.code,
        "result_id": result.id,
    }
