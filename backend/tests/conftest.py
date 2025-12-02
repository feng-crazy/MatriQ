"""Pytest 配置和共享 fixtures"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pytest
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import Settings
from app.models.pipeline import Pipeline, RecognitionResult


@pytest.fixture
def temp_db() -> Generator[Session, None, None]:
    """创建临时数据库用于测试"""
    # 创建临时数据库文件
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    
    # 创建测试数据库引擎
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    
    # 创建会话
    with Session(engine) as session:
        yield session
    
    # 清理
    try:
        os.unlink(db_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def temp_data_dir() -> Generator[Path, None, None]:
    """创建临时数据目录用于测试"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_settings(temp_data_dir: Path) -> Settings:
    """创建测试配置"""
    return Settings(
        sqlite_path=temp_data_dir / "test.db",
        pipelines_root=temp_data_dir / "pipelines",
        paddleocr_api_url="https://test-api.example.com/layout-parsing",
        paddleocr_token="test-token",
    )


@pytest.fixture
def sample_pipeline(temp_db: Session) -> Pipeline:
    """创建示例流水线"""
    pipeline = Pipeline(
        code="test_line_001",
        name="测试流水线",
        excel_path="/tmp/test_line_001_MatriQ.xlsx",
    )
    temp_db.add(pipeline)
    temp_db.commit()
    temp_db.refresh(pipeline)
    return pipeline


@pytest.fixture
def sample_ocr_response() -> dict:
    """模拟 PaddleOCR-VL API 响应"""
    return {
        "result": {
            "layoutParsingResults": [
                {
                    "markdown": {
                        "text": "Sunlord SL-IND-1008-100 Qty:4000 Batch:B2511A Date:30/11/2025 L=10uH±10%"
                    }
                }
            ]
        }
    }


@pytest.fixture
def sample_image_bytes() -> bytes:
    """创建模拟图片字节数据"""
    # 创建一个最小的有效 JPEG 文件头（仅用于测试）
    return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xd9"

