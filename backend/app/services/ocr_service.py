from __future__ import annotations

import base64
from datetime import datetime
from typing import Any

import httpx

from app.core.config import get_settings
from app.core.logger import get_logger

settings = get_settings()
logger = get_logger("services.ocr")


class OcrServiceError(Exception):
    pass


class OcrService:
    def __init__(self):
        self.client = httpx.Client(timeout=120)  # PaddleOCR-VL 可能需要更长时间
        logger.info("OCR服务初始化完成")

    def classify_and_recognize(self, image_bytes: bytes, filename: str) -> dict[str, Any]:
        """调用 PaddleOCR-VL API 进行布局解析和文字识别"""
        logger.info(f"开始OCR处理: 文件名={filename}, 大小={len(image_bytes)} bytes")
        
        if not settings.paddleocr_api_url:
            logger.error("未配置PaddleOCR-VL API端点")
            raise OcrServiceError("未配置 PaddleOCR-VL API 端点")

        # Base64 编码图片
        file_data = base64.b64encode(image_bytes).decode("ascii")
        logger.debug("图片Base64编码完成")

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
        logger.debug("构建OCR API请求")

        try:
            logger.debug(f"发送OCR API请求到: {settings.paddleocr_api_url}")
            response = self.client.post(
                settings.paddleocr_api_url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            logger.debug("OCR API请求成功")

            result_data = response.json()
            if "result" not in result_data:
                logger.error("OCR API返回格式异常：缺少result字段")
                raise OcrServiceError("API 返回格式异常：缺少 result 字段")

            result = result_data["result"]
            logger.debug(f"OCR API响应解析成功 {result}")

            # 提取 markdown 文本（合并所有布局解析结果）
            raw_text_parts = []
            if "layoutParsingResults" in result:
                for layout_result in result["layoutParsingResults"]:
                    if "markdown" in layout_result and "text" in layout_result["markdown"]:
                        raw_text_parts.append(layout_result["markdown"]["text"])

            raw_ocr_text = "\n".join(raw_text_parts) if raw_text_parts else ""
            logger.debug(f"提取到OCR文本: 长度={len(raw_ocr_text)} 字符")

            # 返回标准化的结果
            result_payload = {
                "raw_ocr_text": raw_ocr_text,
                "image_filename": filename,
                "scan_time": datetime.utcnow().isoformat(),
                # 原始 API 响应保留在 _raw_response 中，供调试使用
                "_raw_response": result,
            }
            
            logger.info("OCR处理完成")
            return result_payload
        except httpx.HTTPStatusError as e:
            error_msg = f"OCR API 调用失败 (HTTP {e.response.status_code})"
            logger.error(f"HTTP错误: {error_msg}")
            try:
                error_detail = e.response.json()
                error_msg += f": {error_detail}"
                logger.error(f"错误详情: {error_detail}")
            except Exception:
                error_msg += f": {e.response.text}"
                logger.error(f"错误响应: {e.response.text}")
            raise OcrServiceError(error_msg) from e
        except httpx.RequestError as e:
            logger.error(f"OCR API请求失败: {str(e)}")
            raise OcrServiceError(f"OCR API 请求失败: {str(e)}") from e
        except Exception as e:
            logger.error(f"OCR处理异常: {str(e)}")
            raise OcrServiceError(f"OCR 处理异常: {str(e)}") from e


def get_ocr_service() -> OcrService:
    return OcrService()
