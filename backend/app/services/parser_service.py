from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict

FIELD_ALIASES = {
    "material_code": ["material", "material code", "code", "料号", "物料编码", "part no", "part number"],
    "quantity": ["qty", "quantity", "数量", "qty:", "quantity:"],
    "batch": ["lot", "lot number", "batch", "批次", "lot no", "lotno"],
    "date": ["date", "production date", "生产日期", "日期", "prod date", "生产日期"],
    "brand": ["brand", "厂商", "品牌", "manufacturer", "mfr"],
    "electrical_characteristics": ["spec", "电气特性", "电感", "规格", "l=", "l =", "inductance", "容差", "tolerance"],
}

DATE_PATTERNS = [
    "%Y/%m/%d",
    "%Y-%m-%d",
    "%d-%b-%Y",
    "%d/%m/%Y",
    "%m/%d/%Y",
    "%Y.%m.%d",
    "%d.%m.%Y",
]


def normalize_date(value: str | None) -> str | None:
    """标准化日期格式为 YYYY-MM-DD"""
    if not value:
        return None
    
    # 清理字符串
    value = value.strip()
    
    # 尝试各种日期格式
    for pattern in DATE_PATTERNS:
        try:
            return datetime.strptime(value, pattern).strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # 尝试从文本中提取日期模式
    # YYYY-MM-DD 或 YYYY/MM/DD
    date_match = re.search(r"(\d{4})[-/](\d{1,2})[-/](\d{1,2})", value)
    if date_match:
        year, month, day = date_match.groups()
        try:
            return datetime(int(year), int(month), int(day)).strftime("%Y-%m-%d")
        except ValueError:
            pass
    
    # DD/MM/YYYY 或 DD-MM-YYYY
    date_match = re.search(r"(\d{1,2})[-/](\d{1,2})[-/](\d{4})", value)
    if date_match:
        day, month, year = date_match.groups()
        try:
            return datetime(int(year), int(month), int(day)).strftime("%Y-%m-%d")
        except ValueError:
            pass
    
    return value


def extract_numeric(value: str | None) -> int | None:
    """从文本中提取数字（去除千位分隔符）"""
    if not value:
        return None
    # 移除逗号，提取第一个完整数字
    cleaned = value.replace(",", "").replace(" ", "")
    match = re.search(r"\d+", cleaned)
    if match:
        try:
            return int(match.group())
        except ValueError:
            return None
    return None


def extract_material_code(text: str) -> str | None:
    """提取物料编码（通常包含字母和数字，如 SL-IND-1008-100）"""
    # 匹配常见的物料编码模式：字母-字母-数字-数字
    patterns = [
        r"[A-Z]{2,}-[A-Z]+-\d+-\d+",  # SL-IND-1008-100
        r"[A-Z]+\d+[A-Z]*",  # ABC123
        r"[A-Z]{2,}\d+[-]?\d*",  # SL1008-100
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group().upper()
    return None


def extract_batch(text: str) -> str | None:
    """提取批次号（通常以 B、LOT、批次等开头）"""
    patterns = [
        r"(?:batch|lot|批次)[\s:]*([A-Z0-9]+)",
        r"B\d+[A-Z]*",
        r"LOT[\s:]*([A-Z0-9]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1) if match.groups() else match.group()
    return None


def extract_brand(text: str) -> str | None:
    """提取品牌名称（常见品牌如 Sunlord）"""
    # 常见品牌列表（可根据实际情况扩展）
    brands = ["Sunlord", "Murata", "TDK", "Vishay", "Coilcraft"]
    text_upper = text.upper()
    for brand in brands:
        if brand.upper() in text_upper:
            return brand
    return None


def extract_electrical_characteristics(text: str) -> str | None:
    """提取电气特性（如 L=10uH±10%）"""
    patterns = [
        r"L\s*=\s*(\d+[mu]?H[±\s]*\d+%?)",  # L=10uH±10%
        r"(\d+[mu]?H[±\s]*\d+%?)",  # 10uH±10%
        r"(\d+[mu]?H)",  # 10uH
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1) if match.groups() else match.group()
    return None


def extract_quantity(text: str) -> int | None:
    """从文本中提取数量（查找 Qty、Quantity、数量等关键词后的数字）"""
    patterns = [
        r"(?:qty|quantity|数量)[\s:]*(\d{1,3}(?:,\d{3})*)",
        r"(?:qty|quantity|数量)[\s:]*(\d+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            num_str = match.group(1).replace(",", "")
            try:
                return int(num_str)
            except ValueError:
                continue
    # 如果没有找到关键词，尝试提取较大的数字（可能是数量）
    numbers = re.findall(r"\d{3,}", text.replace(",", ""))
    if numbers:
        try:
            # 返回最大的数字（通常是数量）
            return max(int(n) for n in numbers)
        except (ValueError, TypeError):
            pass
    return None


def parse_ocr_payload(ocr_payload: Dict[str, Any]) -> Dict[str, Any]:
    """从 OCR 结果中解析并提取结构化字段"""
    raw_text = ocr_payload.get("raw_ocr_text", "")
    
    # 如果 OCR 已经返回了结构化字段，优先使用
    normalized = {
        "material_code": ocr_payload.get("material_code"),
        "quantity": ocr_payload.get("quantity"),
        "batch": ocr_payload.get("batch"),
        "date": normalize_date(ocr_payload.get("date")),
        "brand": ocr_payload.get("brand"),
        "electrical_characteristics": ocr_payload.get("electrical_characteristics"),
        "raw_ocr_text": raw_text,
        "image_filename": ocr_payload.get("image_filename"),
        "scan_time": ocr_payload.get("scan_time", datetime.utcnow()),
    }

    # 如果字段缺失，从原始文本中提取
    if not normalized["material_code"] and raw_text:
        normalized["material_code"] = extract_material_code(raw_text)
    
    if not normalized["quantity"] and raw_text:
        normalized["quantity"] = extract_quantity(raw_text)
        if not normalized["quantity"]:
            normalized["quantity"] = extract_numeric(raw_text)
    
    if not normalized["batch"] and raw_text:
        normalized["batch"] = extract_batch(raw_text)
    
    if not normalized["date"] and raw_text:
        normalized["date"] = normalize_date(raw_text)
    
    if not normalized["brand"] and raw_text:
        normalized["brand"] = extract_brand(raw_text)
    
    if not normalized["electrical_characteristics"] and raw_text:
        normalized["electrical_characteristics"] = extract_electrical_characteristics(raw_text)

    return normalized
