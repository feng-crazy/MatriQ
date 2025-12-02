"""测试流水线服务"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from app.models.pipeline import Pipeline, RecognitionResult
from app.services.pipeline_service import (
    create_pipeline,
    get_pipeline,
    list_pipelines,
    store_result,
)


class TestPipelineService:
    """测试流水线服务"""

    @patch("app.services.pipeline_service.get_session")
    @patch("app.services.pipeline_service.get_settings")
    @patch("app.services.pipeline_service.initialize_excel")
    def test_create_pipeline(
        self, mock_init_excel, mock_get_settings, mock_get_session, temp_data_dir: Path, temp_db
    ):
        """测试创建流水线"""
        # 设置 mock
        mock_settings = pytest.MagicMock()
        mock_settings.pipelines_root = temp_data_dir / "pipelines"
        mock_settings.excel_filename_template = "{pipeline_code}_MatriQ.xlsx"
        mock_get_settings.return_value = mock_settings

        # 模拟 get_session
        from contextlib import contextmanager

        @contextmanager
        def mock_session():
            yield temp_db

        mock_get_session.return_value = mock_session()

        # 执行
        pipeline = create_pipeline("测试流水线")

        # 验证
        assert pipeline.name == "测试流水线"
        assert "test" in pipeline.code.lower() or "line" in pipeline.code.lower()
        mock_init_excel.assert_called_once()

    @patch("app.services.pipeline_service.get_session")
    def test_list_pipelines(self, mock_get_session, temp_db):
        """测试列出流水线"""
        # 创建测试数据
        pipeline1 = Pipeline(
            code="line_001", name="流水线1", excel_path="/tmp/line_001.xlsx"
        )
        pipeline2 = Pipeline(
            code="line_002", name="流水线2", excel_path="/tmp/line_002.xlsx"
        )
        temp_db.add(pipeline1)
        temp_db.add(pipeline2)
        temp_db.commit()
        temp_db.refresh(pipeline1)
        temp_db.refresh(pipeline2)

        # 模拟 get_session
        from contextlib import contextmanager

        @contextmanager
        def mock_session():
            yield temp_db

        mock_get_session.return_value = mock_session()

        # 执行
        pipelines = list_pipelines()

        # 验证
        assert len(pipelines) == 2
        assert pipelines[0].name in ["流水线1", "流水线2"]
        assert hasattr(pipelines[0], "total_scans")

    @patch("app.services.pipeline_service.get_session")
    def test_get_pipeline(self, mock_get_session, temp_db):
        """测试获取单个流水线"""
        # 创建测试数据
        pipeline = Pipeline(
            code="line_001", name="流水线1", excel_path="/tmp/line_001.xlsx"
        )
        temp_db.add(pipeline)
        temp_db.commit()
        temp_db.refresh(pipeline)

        # 模拟 get_session
        from contextlib import contextmanager

        @contextmanager
        def mock_session():
            yield temp_db

        mock_get_session.return_value = mock_session()

        # 执行
        result = get_pipeline(pipeline.id)

        # 验证
        assert result is not None
        assert result.id == pipeline.id
        assert result.name == "流水线1"

    @patch("app.services.pipeline_service.get_session")
    def test_get_nonexistent_pipeline(self, mock_get_session, temp_db):
        """测试获取不存在的流水线"""
        from contextlib import contextmanager

        @contextmanager
        def mock_session():
            yield temp_db

        mock_get_session.return_value = mock_session()

        result = get_pipeline(999)

        assert result is None

    @patch("app.services.pipeline_service.get_session")
    @patch("app.services.pipeline_service.append_result")
    def test_store_result(self, mock_append, mock_get_session, temp_db, temp_data_dir: Path):
        """测试存储识别结果"""
        # 创建测试流水线
        pipeline = Pipeline(
            code="line_001",
            name="流水线1",
            excel_path=str(temp_data_dir / "line_001.xlsx"),
        )
        temp_db.add(pipeline)
        temp_db.commit()
        temp_db.refresh(pipeline)

        # 模拟 get_session
        from contextlib import contextmanager

        @contextmanager
        def mock_session():
            yield temp_db

        mock_get_session.return_value = mock_session()

        # 执行
        result_data = {
            "material_code": "SL-IND-1008-100",
            "quantity": 4000,
            "batch": "B2511A",
            "raw_ocr_text": "Test OCR text",
            "image_filename": "test.jpg",
            "recognized_at": datetime.utcnow(),
        }

        result = store_result(pipeline, result_data)

        # 验证
        assert result.material_code == "SL-IND-1008-100"
        assert result.quantity == 4000
        assert result.pipeline_id == pipeline.id
        mock_append.assert_called_once()

