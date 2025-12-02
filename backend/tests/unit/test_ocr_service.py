"""测试 OCR 服务（使用 Mock）"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from app.services.ocr_service import OcrService, OcrServiceError


class TestOcrService:
    """测试 OCR 服务"""

    @patch("app.services.ocr_service.settings")
    @patch("app.services.ocr_service.httpx.Client")
    def test_successful_ocr_call(self, mock_client_class, mock_settings):
        """测试成功的 OCR 调用"""
        # 设置 mock
        mock_settings.paddleocr_api_url = "https://test-api.example.com/layout-parsing"
        mock_settings.paddleocr_token = "test-token"

        # 模拟 HTTP 响应
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {
                "layoutParsingResults": [
                    {
                        "markdown": {
                            "text": "Sunlord SL-IND-1008-100 Qty:4000"
                        }
                    }
                ]
            }
        }
        mock_response.raise_for_status = MagicMock()

        # 模拟客户端
        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        # 执行测试
        service = OcrService()
        result = service.classify_and_recognize(b"fake image data", "test.jpg")

        # 验证
        assert result["raw_ocr_text"] == "Sunlord SL-IND-1008-100 Qty:4000"
        assert result["image_filename"] == "test.jpg"
        assert "scan_time" in result
        assert "_raw_response" in result

        # 验证请求参数
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[0][0] == "https://test-api.example.com/layout-parsing"
        assert call_args[1]["headers"]["Authorization"] == "token test-token"
        assert call_args[1]["json"]["fileType"] == 1

    @patch("app.services.ocr_service.settings")
    def test_missing_api_url(self, mock_settings):
        """测试缺少 API URL"""
        mock_settings.paddleocr_api_url = None

        service = OcrService()
        with pytest.raises(OcrServiceError, match="未配置 PaddleOCR-VL API 端点"):
            service.classify_and_recognize(b"fake image data", "test.jpg")

    @patch("app.services.ocr_service.settings")
    @patch("app.services.ocr_service.httpx.Client")
    def test_http_error(self, mock_client_class, mock_settings):
        """测试 HTTP 错误"""
        mock_settings.paddleocr_api_url = "https://test-api.example.com/layout-parsing"
        mock_settings.paddleocr_token = "test-token"

        # 模拟 HTTP 错误响应
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.side_effect = ValueError("Not JSON")

        mock_http_error = httpx.HTTPStatusError(
            "Server Error", request=MagicMock(), response=mock_response
        )

        mock_client = MagicMock()
        mock_client.post.side_effect = mock_http_error
        mock_client_class.return_value = mock_client

        service = OcrService()
        with pytest.raises(OcrServiceError, match="OCR API 调用失败"):
            service.classify_and_recognize(b"fake image data", "test.jpg")

    @patch("app.services.ocr_service.settings")
    @patch("app.services.ocr_service.httpx.Client")
    def test_invalid_response_format(self, mock_client_class, mock_settings):
        """测试无效的响应格式"""
        mock_settings.paddleocr_api_url = "https://test-api.example.com/layout-parsing"
        mock_settings.paddleocr_token = "test-token"

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"error": "Invalid format"}
        mock_response.raise_for_status = MagicMock()

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_client_class.return_value = mock_client

        service = OcrService()
        with pytest.raises(OcrServiceError, match="缺少 result 字段"):
            service.classify_and_recognize(b"fake image data", "test.jpg")

    @patch("app.services.ocr_service.settings")
    @patch("app.services.ocr_service.httpx.Client")
    def test_request_error(self, mock_client_class, mock_settings):
        """测试请求错误（网络问题等）"""
        mock_settings.paddleocr_api_url = "https://test-api.example.com/layout-parsing"
        mock_settings.paddleocr_token = "test-token"

        mock_client = MagicMock()
        mock_client.post.side_effect = httpx.RequestError("Connection failed", request=MagicMock())
        mock_client_class.return_value = mock_client

        service = OcrService()
        with pytest.raises(OcrServiceError, match="OCR API 请求失败"):
            service.classify_and_recognize(b"fake image data", "test.jpg")

