from functools import lru_cache
from pathlib import Path
from typing import List, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = Field(default="MatriQ OCR Service", validation_alias="APP_NAME")
    api_prefix: str = Field(default="/api/v1", validation_alias="API_PREFIX")
    sqlite_path: Path = Field(default=Path("backend/data/matriq.db"), validation_alias="SQLITE_PATH")
    pipelines_root: Path = Field(default=Path("backend/data/pipelines"), validation_alias="PIPELINES_ROOT")
    excel_filename_template: str = Field(
        default="{pipeline_code}_MatriQ.xlsx", validation_alias="EXCEL_FILENAME_TEMPLATE"
    )

    # PaddleOCR-VL API 配置
    paddleocr_api_url: str = Field(
        default="https://gfc197xb35lb0274.aistudio-app.com/layout-parsing",
        validation_alias="PADDLEOCR_API_URL",
    )
    paddleocr_token: str = Field(
        default="your-token-here", validation_alias="PADDLEOCR_TOKEN"
    )
    
    # 兼容旧配置（可选）
    ocr_endpoint: str | None = None
    ocr_api_key: str | None = None
    classifier_endpoint: str | None = None

    allowed_extensions: Union[List[str], str] = Field(
        default=[".jpg", ".jpeg", ".png"], validation_alias="ALLOWED_EXTENSIONS"
    )
    max_upload_mb: int = Field(default=15, validation_alias="MAX_UPLOAD_MB")
    
    # 日志配置
    log_level: str = Field(default="DEBUG", validation_alias="LOG_LEVEL")
    log_file: str = Field(default="app.log", validation_alias="LOG_FILE")
    enable_file_logging: bool = Field(default=True, validation_alias="ENABLE_FILE_LOGGING")

    @field_validator("allowed_extensions", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v: Union[List[str], str]) -> List[str]:
        if isinstance(v, str):
            return [x.strip() for x in v.split(",") if x.strip()]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # 环境变量不区分大小写


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.pipelines_root.mkdir(parents=True, exist_ok=True)
    settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return settings