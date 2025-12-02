from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Iterable

from sqlmodel import select

from app.core.config import get_settings
from app.core.logger import get_logger
from app.db.session import get_session
from app.models.pipeline import Pipeline, RecognitionResult

settings = get_settings()
logger = get_logger("services.pipeline")


def _generate_code(name: str) -> str:
    sanitized = "".join(ch for ch in name if ch.isalnum()) or "line"
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"{sanitized.lower()}_{timestamp}"


def _excel_path(code: str) -> Path:
    filename = settings.excel_filename_template.format(pipeline_code=code)
    return settings.pipelines_root / filename


def create_pipeline(name: str) -> Pipeline:
    logger.info(f"创建流水线: {name}")
    code = _generate_code(name)
    excel_path = _excel_path(code)
    logger.debug(f"生成流水线代码: {code}, Excel路径: {excel_path}")

    with get_session() as session:
        pipeline = Pipeline(code=code, name=name, excel_path=str(excel_path))
        session.add(pipeline)
        session.commit()
        session.refresh(pipeline)
        logger.info(f"流水线数据库记录创建完成: ID={pipeline.id}")

    excel_path.parent.mkdir(parents=True, exist_ok=True)
    if not excel_path.exists():
        logger.debug("初始化Excel文件")
        from app.utils.excel_writer import initialize_excel

        initialize_excel(excel_path)
        logger.debug("Excel文件初始化完成")
    
    logger.info(f"流水线创建成功: {code}")
    return pipeline


def list_pipelines() -> list[Pipeline]:
    logger.debug("查询所有流水线")
    with get_session() as session:
        statement = select(Pipeline)
        pipelines = list(session.exec(statement).all())
        logger.debug(f"找到 {len(pipelines)} 个流水线")
        return pipelines


def get_pipeline(pipeline_id: int) -> Pipeline | None:
    logger.debug(f"根据ID查询流水线: {pipeline_id}")
    with get_session() as session:
        pipeline = session.get(Pipeline, pipeline_id)
        if pipeline:
            logger.debug(f"找到流水线: ID={pipeline.id}, Code={pipeline.code}")
        else:
            logger.debug(f"未找到流水线: ID={pipeline_id}")
        return pipeline


def _count_scans(session, pipeline_id: int) -> int:
    logger.debug(f"统计流水线扫描次数: ID={pipeline_id}")
    statement = select(RecognitionResult).where(RecognitionResult.pipeline_id == pipeline_id)
    count = len(session.exec(statement).all())
    logger.debug(f"流水线 {pipeline_id} 的扫描次数: {count}")
    return count


def store_result(pipeline: Pipeline, result_data: dict) -> RecognitionResult:
    logger.info(f"存储识别结果到流水线: {pipeline.code}")
    excel_path = Path(pipeline.excel_path)
    excel_path.parent.mkdir(parents=True, exist_ok=True)

    with get_session() as session:
        # 确保 pipeline.id 不为空
        if pipeline.id is None:
            logger.error("Pipeline ID为None，无法创建识别结果")
            raise ValueError("Pipeline ID is None, cannot create RecognitionResult")
        
        result = RecognitionResult(pipeline_id=pipeline.id, **result_data)
        session.add(result)
        session.commit()
        session.refresh(result)
        logger.debug(f"识别结果存储到数据库: ID={result.id}")

    from app.utils.excel_writer import append_result

    logger.debug("将结果追加到Excel文件")
    append_result(excel_path, result)
    logger.info(f"识别结果存储完成: 流水线={pipeline.code}, 结果ID={result.id}")
    return result
