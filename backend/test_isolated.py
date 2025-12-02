#!/usr/bin/env python3

import sys
sys.path.insert(0, '.')

from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field, SQLModel

print("Testing isolated pipeline model...")

try:
    class Pipeline(SQLModel, table=True):
        __tablename__ = "pipelines"

        id: Optional[int] = Field(default=None, primary_key=True)
        code: str = Field(index=True, unique=True)
        name: str
        excel_path: str
        created_at: datetime = Field(default_factory=datetime.utcnow, sa_type=DateTime(timezone=True))

    print("✓ Pipeline class defined successfully")
    
except Exception as e:
    print(f"✗ Pipeline class failed: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting RecognitionResult model...")

try:
    class RecognitionResult(SQLModel, table=True):
        __tablename__ = "recognition_results"

        id: Optional[int] = Field(default=None, primary_key=True)
        pipeline_id: int = Field(foreign_key="pipelines.id")
        material_code: Optional[str] = None
        quantity: Optional[int] = Field(default=None, sa_type=Integer)
        batch: Optional[str] = None
        date: Optional[str] = None
        brand: Optional[str] = None
        electrical_characteristics: Optional[str] = None
        raw_ocr_text: Optional[str] = None
        image_filename: Optional[str] = None
        recognized_at: datetime = Field(default_factory=datetime.utcnow, sa_type=DateTime(timezone=True))

    print("✓ RecognitionResult class defined successfully")
    
except Exception as e:
    print(f"✗ RecognitionResult class failed: {e}")
    import traceback
    traceback.print_exc()