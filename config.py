import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    
    API_TITLE: str = "PDF Tools API"
    API_VERSION: str = "0.1.0"
    API_DESCRIPTION: str = "High-performance PDF processing API"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    CORS_ORIGINS: str = "*"
    
    MAX_FILE_SIZE_MB: int = 100
    MAX_FILES_PER_REQUEST: int = 50
    
    TEMP_DIR: str = "./temp"
    CLEANUP_TEMP_FILES: bool = True
    
    DEFAULT_DPI: int = 72
    DEFAULT_IMAGE_QUALITY: int = 40
    DEFAULT_COLOR_MODE: str = "no-change"
    
    ASYNC_PROCESSING: bool = True
    PROCESS_TIMEOUT_SECONDS: int = 300
    
    @property
    def cors_origins_list(self) -> List[str]:
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    @property
    def max_file_size_bytes(self) -> int:
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

settings = Settings()

os.makedirs(settings.TEMP_DIR, exist_ok=True)
