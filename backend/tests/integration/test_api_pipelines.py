"""测试流水线 API 端点"""
from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


@pytest.fixture
def mock_ocr_service():
    """模拟 OCR 服务"""
    with patch("app.api.routes.pipelines.get_ocr_service") as mock:
        mock_service = MagicMock()
        mock_service.classify_and_recognize.return_value = {
            "raw_ocr_text": "Sunlord SL-IND-1008-100 Qty:4000 Batch:B2511A Date:30/11/2025 L=10uH±10%",
            "image_filename": "test.jpg",
            "scan_time": "2025-11-30T12:00:00",
        }
        mock.return_value = mock_service
        yield mock_service


@pytest.fixture
def sample_image():
    """创建示例图片文件"""
    # 创建一个最小的有效 JPEG 文件头
    return b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xd9"


class TestPipelineAPI:
    """测试流水线 API"""

    def test_create_pipeline(self, client):
        """测试创建流水线"""
        response = client.post(
            "/api/v1/pipelines",
            json={"name": "测试流水线"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "测试流水线"
        assert "code" in data
        assert "id" in data
        assert "excel_path" in data

    def test_list_pipelines(self, client):
        """测试列出流水线"""
        # 先创建一个流水线
        client.post("/api/v1/pipelines", json={"name": "流水线1"})

        # 获取列表
        response = client.get("/api/v1/pipelines")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert "id" in data[0]
        assert "name" in data[0]
        assert "total_scans" in data[0]

    def test_get_pipeline(self, client):
        """测试获取单个流水线"""
        # 先创建一个流水线
        create_response = client.post(
            "/api/v1/pipelines",
            json={"name": "测试流水线"},
        )
        pipeline_id = create_response.json()["id"]

        # 获取流水线详情
        response = client.get(f"/api/v1/pipelines/{pipeline_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pipeline_id
        assert data["name"] == "测试流水线"
        assert "excel_path" in data

    def test_get_nonexistent_pipeline(self, client):
        """测试获取不存在的流水线"""
        response = client.get("/api/v1/pipelines/99999")

        assert response.status_code == 404
        assert "流水线不存在" in response.json()["detail"]

    @patch("app.api.routes.pipelines.get_ocr_service")
    def test_scan_image(
        self, mock_get_ocr, client, sample_image, temp_data_dir: Path
    ):
        """测试图片扫描"""
        # 创建流水线
        create_response = client.post(
            "/api/v1/pipelines",
            json={"name": "测试流水线"},
        )
        pipeline_id = create_response.json()["id"]

        # 模拟 OCR 服务
        mock_service = MagicMock()
        mock_service.classify_and_recognize.return_value = {
            "raw_ocr_text": "Sunlord SL-IND-1008-100 Qty:4000 Batch:B2511A",
            "image_filename": "test.jpg",
            "scan_time": "2025-11-30T12:00:00",
        }
        mock_get_ocr.return_value = mock_service

        # 上传图片
        response = client.post(
            f"/api/v1/pipelines/{pipeline_id}/scan",
            files={"image": ("test.jpg", sample_image, "image/jpeg")},
        )

        assert response.status_code == 200
        data = response.json()
        assert "material_code" in data
        assert "quantity" in data
        assert "raw_ocr_text" in data
        assert data["pipeline_id"] == pipeline_id

        # 验证 OCR 服务被调用
        mock_service.classify_and_recognize.assert_called_once()

    def test_scan_image_invalid_format(self, client, sample_image):
        """测试无效图片格式"""
        # 创建流水线
        create_response = client.post(
            "/api/v1/pipelines",
            json={"name": "测试流水线"},
        )
        pipeline_id = create_response.json()["id"]

        # 上传无效格式文件
        response = client.post(
            f"/api/v1/pipelines/{pipeline_id}/scan",
            files={"image": ("test.txt", b"not an image", "text/plain")},
        )

        assert response.status_code == 400
        assert "文件格式不支持" in response.json()["detail"]

    def test_scan_image_nonexistent_pipeline(self, client, sample_image):
        """测试扫描不存在的流水线"""
        response = client.post(
            "/api/v1/pipelines/99999/scan",
            files={"image": ("test.jpg", sample_image, "image/jpeg")},
        )

        assert response.status_code == 404
        assert "流水线不存在" in response.json()["detail"]

    @patch("app.api.routes.pipelines.get_ocr_service")
    def test_scan_image_ocr_error(self, mock_get_ocr, client, sample_image):
        """测试 OCR 服务错误"""
        # 创建流水线
        create_response = client.post(
            "/api/v1/pipelines",
            json={"name": "测试流水线"},
        )
        pipeline_id = create_response.json()["id"]

        # 模拟 OCR 服务错误
        from app.services.ocr_service import OcrServiceError

        mock_service = MagicMock()
        mock_service.classify_and_recognize.side_effect = OcrServiceError("OCR 服务失败")
        mock_get_ocr.return_value = mock_service

        # 上传图片
        response = client.post(
            f"/api/v1/pipelines/{pipeline_id}/scan",
            files={"image": ("test.jpg", sample_image, "image/jpeg")},
        )

        assert response.status_code == 500
        assert "OCR" in response.json()["detail"]

    def test_export_excel(self, client, sample_image, mock_ocr_service):
        """测试导出 Excel"""
        # 创建流水线并扫描一张图片
        create_response = client.post(
            "/api/v1/pipelines",
            json={"name": "测试流水线"},
        )
        pipeline_id = create_response.json()["id"]

        # 上传图片（这会创建 Excel 文件）
        client.post(
            f"/api/v1/pipelines/{pipeline_id}/scan",
            files={"image": ("test.jpg", sample_image, "image/jpeg")},
        )

        # 导出 Excel
        response = client.get(f"/api/v1/pipelines/{pipeline_id}/export")

        assert response.status_code == 200
        assert (
            response.headers["content-type"]
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert len(response.content) > 0

    def test_export_nonexistent_excel(self, client):
        """测试导出不存在的 Excel"""
        # 创建流水线但不扫描图片
        create_response = client.post(
            "/api/v1/pipelines",
            json={"name": "测试流水线"},
        )
        pipeline_id = create_response.json()["id"]

        # 尝试导出（Excel 文件不存在）
        response = client.get(f"/api/v1/pipelines/{pipeline_id}/export")

        assert response.status_code == 404
        assert "Excel 文件不存在" in response.json()["detail"]


class TestHealthCheck:
    """测试健康检查端点"""

    def test_health_check(self, client):
        """测试根路径健康检查"""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "app" in data

