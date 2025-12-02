from __future__ import annotations

import base64
from datetime import datetime
from typing import Any

import httpx

from app.core.config import get_settings

settings = get_settings()


class OcrServiceError(Exception):
    pass


class OcrService:
    def __init__(self):
        self.client = httpx.Client(timeout=120)  # PaddleOCR-VL 可能需要更长时间

    def classify_and_recognize(self, image_bytes: bytes, filename: str) -> dict[str, Any]:
        """调用 PaddleOCR-VL API 进行布局解析和文字识别"""
        if not settings.paddleocr_api_url:
            raise OcrServiceError("未配置 PaddleOCR-VL API 端点")

        # Base64 编码图片
        file_data = base64.b64encode(image_bytes).decode("ascii")

        # 构建请求头
        headers = {
            "Authorization": f"token {settings.paddleocr_token}",
            "Content-Type": "application/json",
        }

        # 构建请求体（图片类型 fileType=1）
        payload = {
            "file": file_data,
            "fileType": 1,  # 1 表示图片，0 表示 PDF
            "useDocOrientationClassify": False,
            "useDocUnwarping": False,
            "useChartRecognition": False,
        }

        try:
            response = self.client.post(
                settings.paddleocr_api_url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()

            result_data = response.json()
            if "result" not in result_data:
                raise OcrServiceError("API 返回格式异常：缺少 result 字段")

            result = result_data["result"]

            # 提取 markdown 文本（合并所有布局解析结果）
            raw_text_parts = []
            if "layoutParsingResults" in result:
                for layout_result in result["layoutParsingResults"]:
                    if "markdown" in layout_result and "text" in layout_result["markdown"]:
                        raw_text_parts.append(layout_result["markdown"]["text"])

            raw_ocr_text = "\n".join(raw_text_parts) if raw_text_parts else ""

            # 返回标准化的结果
            return {
                "raw_ocr_text": raw_ocr_text,
                "image_filename": filename,
                "scan_time": datetime.utcnow().isoformat(),
                # 原始 API 响应保留在 _raw_response 中，供调试使用
                "_raw_response": result,
            }
        except httpx.HTTPStatusError as e:
            error_msg = f"OCR API 调用失败 (HTTP {e.response.status_code})"
            try:
                error_detail = e.response.json()
                error_msg += f": {error_detail}"
            except Exception:
                error_msg += f": {e.response.text}"
            raise OcrServiceError(error_msg) from e
        except httpx.RequestError as e:
            raise OcrServiceError(f"OCR API 请求失败: {str(e)}") from e
        except Exception as e:
            raise OcrServiceError(f"OCR 处理异常: {str(e)}") from e


def get_ocr_service() -> OcrService:
    return OcrService()
