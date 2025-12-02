#!/usr/bin/env python3

from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, relationship
from sqlmodel import Field, SQLModel

# 首先测试单独的字段定义
print("Testing field definitions...")

# 测试每个字段类型
test_fields = [
    ("id", Optional[int]),
    ("code", str),
    ("name", str),
    ("excel_path", str),
    ("created_at", datetime)
]

for name, field_type in test_fields:
    try:
        field = Field()
        print(f"✓ {name}: {field_type} - OK")
    except Exception as e:
        print(f"✗ {name}: {field_type} - ERROR: {e}")

print("\nTesting full class definition...")

# 现在测试完整的类定义
try:
    class TestPipeline(SQLModel, table=True):
        __tablename__ = "test_pipelines"

        id: Optional[int] = Field(default=None, primary_key=True)
        code: str = Field(index=True, unique=True)
        name: str
        excel_path: str
        created_at: datetime = Field(default_factory=datetime.utcnow, sa_type=DateTime(timezone=True))

    print("✓ TestPipeline class defined successfully")
    
except Exception as e:
    print(f"✗ TestPipeline class failed: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting Mapped relationship...")

try:
    class TestRecognitionResult(SQLModel, table=True):
        __tablename__ = "test_recognition_results"

        id: Optional[int] = Field(default=None, primary_key=True)
        pipeline_id: int = Field(foreign_key="test_pipelines.id")
        
    print("✓ TestRecognitionResult class defined successfully")
    
except Exception as e:
    print(f"✗ TestRecognitionResult class failed: {e}")
    import traceback
    traceback.print_exc()