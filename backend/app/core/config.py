from pathlib import Path
from typing import List, Union
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = f"sqlite:///{BACKEND_DIR / 'faculty_scheduler.db'}"

    # JWT & Auth
    JWT_SECRET_KEY: str = "dev_super_secret_key_for_jwt_signing_which_is_at_least_32_bytes_long!"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # Institutional Defaults
    INSTITUTION_NAME: str = "Academic Institute"
    TIMEZONE: str = "Asia/Kolkata"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def resolve_database_url(cls, v: str) -> str:
        if v and v.startswith("sqlite:///."):
            rel_path = v.replace("sqlite:///.", "").lstrip("/\\")
            abs_path = (BACKEND_DIR / rel_path).resolve()
            return f"sqlite:///{abs_path}"
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.strip().startswith("[") and v.strip().endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    @model_validator(mode="after")
    def validate_production_secrets(self) -> "Settings":
        if self.ENVIRONMENT.lower() == "production":
            if "dev_" in self.JWT_SECRET_KEY or len(self.JWT_SECRET_KEY) < 32:
                raise ValueError(
                    "Production deployment requires a secure, non-default JWT_SECRET_KEY of at least 32 characters."
                )
            if self.DATABASE_URL.startswith("sqlite"):
                raise ValueError("Production deployment requires PostgreSQL, SQLite is not permitted.")
        return self

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
