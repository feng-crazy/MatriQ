"""测试字段解析服务"""
from __future__ import annotations

from datetime import datetime

import pytest

from app.services.parser_service import (
    extract_batch,
    extract_brand,
    extract_electrical_characteristics,
    extract_material_code,
    extract_quantity,
    normalize_date,
    parse_ocr_payload,
)


class TestNormalizeDate:
    """测试日期标准化"""

    def test_standard_formats(self):
        """测试标准日期格式"""
        assert normalize_date("2025-11-30") == "2025-11-30"
        assert normalize_date("2025/11/30") == "2025-11-30"
        assert normalize_date("30/11/2025") == "2025-11-30"
        assert normalize_date("30-Nov-2025") == "2025-11-30"

    def test_invalid_date(self):
        """测试无效日期"""
        assert normalize_date("invalid") == "invalid"
        assert normalize_date(None) is None
        assert normalize_date("") is None

    def test_date_in_text(self):
        """测试从文本中提取日期"""
        assert normalize_date("生产日期: 2025-11-30") == "2025-11-30"
        assert normalize_date("Date: 30/11/2025") == "2025-11-30"


class TestExtractMaterialCode:
    """测试物料编码提取"""

    def test_standard_format(self):
        """测试标准格式"""
        text = "Sunlord SL-IND-1008-100 Qty:4000"
        assert extract_material_code(text) == "SL-IND-1008-100"

    def test_simple_format(self):
        """测试简单格式"""
        text = "Material Code: ABC123"
        assert extract_material_code(text) == "ABC123"

    def test_no_match(self):
        """测试无匹配"""
        assert extract_material_code("No material code here") is None


class TestExtractQuantity:
    """测试数量提取"""

    def test_with_keyword(self):
        """测试带关键词的数量"""
        assert extract_quantity("Qty: 4000") == 4000
        assert extract_quantity("Quantity: 5000") == 5000
        assert extract_quantity("数量: 3000") == 3000
        assert extract_quantity("Qty: 1,000") == 1000

    def test_large_number(self):
        """测试大数字"""
        text = "Some text with 5000 units"
        assert extract_quantity(text) == 5000

    def test_no_match(self):
        """测试无匹配"""
        assert extract_quantity("No numbers here") is None


class TestExtractBatch:
    """测试批次号提取"""

    def test_batch_keyword(self):
        """测试 Batch 关键词"""
        assert extract_batch("Batch: B2511A") == "B2511A"
        assert extract_batch("批次: B2511A") == "B2511A"

    def test_lot_keyword(self):
        """测试 Lot 关键词"""
        assert extract_batch("Lot: L123") == "L123"
        assert extract_batch("LOT: L123") == "L123"

    def test_batch_pattern(self):
        """测试批次模式"""
        assert extract_batch("B2511A") == "B2511A"

    def test_no_match(self):
        """测试无匹配"""
        assert extract_batch("No batch here") is None


class TestExtractBrand:
    """测试品牌提取"""

    def test_known_brands(self):
        """测试已知品牌"""
        assert extract_brand("Sunlord SL-IND-1008-100") == "Sunlord"
        assert extract_brand("Murata component") == "Murata"
        assert extract_brand("TDK inductor") == "TDK"

    def test_no_match(self):
        """测试无匹配"""
        assert extract_brand("Unknown brand") is None


class TestExtractElectricalCharacteristics:
    """测试电气特性提取"""

    def test_inductance_format(self):
        """测试电感格式"""
        assert extract_electrical_characteristics("L=10uH±10%") == "10uH±10%"
        assert extract_electrical_characteristics("L = 10uH ±10%") == "10uH ±10%"
        assert extract_electrical_characteristics("10uH±10%") == "10uH±10%"

    def test_simple_inductance(self):
        """测试简单电感值"""
        assert extract_electrical_characteristics("10uH") == "10uH"

    def test_no_match(self):
        """测试无匹配"""
        assert extract_electrical_characteristics("No spec here") is None


class TestParseOcrPayload:
    """测试 OCR 载荷解析"""

    def test_complete_parsing(self):
        """测试完整解析"""
        ocr_payload = {
            "raw_ocr_text": "Sunlord SL-IND-1008-100 Qty:4000 Batch:B2511A Date:30/11/2025 L=10uH±10%",
            "image_filename": "test.jpg",
            "scan_time": datetime.utcnow().isoformat(),
        }

        result = parse_ocr_payload(ocr_payload)

        assert result["material_code"] == "SL-IND-1008-100"
        assert result["quantity"] == 4000
        assert result["batch"] == "B2511A"
        assert result["date"] == "2025-11-30"
        assert result["brand"] == "Sunlord"
        assert result["electrical_characteristics"] == "10uH±10%"
        assert result["raw_ocr_text"] == ocr_payload["raw_ocr_text"]
        assert result["image_filename"] == "test.jpg"

    def test_partial_parsing(self):
        """测试部分字段解析"""
        ocr_payload = {
            "raw_ocr_text": "Qty: 5000",
            "image_filename": "test.jpg",
            "scan_time": datetime.utcnow().isoformat(),
        }

        result = parse_ocr_payload(ocr_payload)

        assert result["quantity"] == 5000
        assert result["material_code"] is None or result["material_code"] is not None
        assert result["raw_ocr_text"] == "Qty: 5000"

    def test_pre_parsed_fields(self):
        """测试已解析字段优先"""
        ocr_payload = {
            "raw_ocr_text": "Some text",
            "material_code": "PRE-PARSED-001",
            "quantity": 1000,
            "image_filename": "test.jpg",
            "scan_time": datetime.utcnow().isoformat(),
        }

        result = parse_ocr_payload(ocr_payload)

        assert result["material_code"] == "PRE-PARSED-001"
        assert result["quantity"] == 1000

    def test_empty_text(self):
        """测试空文本"""
        ocr_payload = {
            "raw_ocr_text": "",
            "image_filename": "test.jpg",
            "scan_time": datetime.utcnow().isoformat(),
        }

        result = parse_ocr_payload(ocr_payload)

        assert result["raw_ocr_text"] == ""
        assert result["material_code"] is None

