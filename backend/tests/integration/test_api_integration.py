"""测试系统集成 API"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


class TestIntegrationAPI:
    """测试系统集成 API"""

    def test_scan_result_endpoint_without_auth(self, client):
        """测试扫描结果端点（无认证）"""
        payload = {
            "material_code": "SL-IND-1008-100",
            "quantity": 4000,
            "batch": "B2511A",
            "date": "2025-11-30",
            "brand": "Sunlord",
            "electrical_characteristics": "10uH ±10%",
            "raw_ocr_text": "Test OCR text",
            "image_filename": "test.jpg",
            "scan_time": "2025-11-30T12:00:00",
        }

        response = client.post("/api/v1/scan-result", json=payload)

        # 如果没有配置 API Key，应该接受请求
        assert response.status_code in [201, 401]
        if response.status_code == 201:
            data = response.json()
            assert data["status"] == "accepted"

