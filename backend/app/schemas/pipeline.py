from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, validator


class PipelineCreate(BaseModel):
    name: str


class PipelineSummary(BaseModel):
    id: int
    code: str
    name: str
    created_at: datetime
    total_scans: int


class PipelineDetail(PipelineSummary):
    excel_path: str


class ScanResult(BaseModel):
    material_code: Optional[str]
    quantity: Optional[int]
    batch: Optional[str]
    date: Optional[str]
    brand: Optional[str]
    electrical_characteristics: Optional[str]
    raw_ocr_text: str
    image_filename: str
    scan_time: datetime

    @validator("scan_time", pre=True)
    def ensure_datetime(cls, value):
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        return value


class RecognitionResponse(ScanResult):
    pipeline_id: int
    pipeline_code: str
