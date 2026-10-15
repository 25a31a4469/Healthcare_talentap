import os
import json
from pathlib import Path
from typing import List, Union, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# Safe multi-location environment discovery
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = Path(__file__).resolve().parent.parent

for env_path in [Path.cwd() / ".env", ROOT_DIR / ".env", BACKEND_DIR / ".env"]:
    if env_path.exists():
        load_dotenv(env_path, override=False)

def resolve_database_url() -> str:
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        # If relative SQLite path, resolve against repo root so DB is never misplaced
        if env_url.startswith("sqlite:///./"):
            relative_name = env_url.replace("sqlite:///./", "")
            resolved_path = ROOT_DIR / relative_name
            return f"sqlite:///{resolved_path.as_posix()}"
        return env_url
    # Default to healthcare.db in repo root
    default_db = ROOT_DIR / "healthcare.db"
    return f"sqlite:///{default_db.as_posix()}"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        extra="ignore"
    )

    APP_NAME: str = "H4 — The Medication Safety Second Pair of Eyes"
    TAGLINE: str = "Catch the right risks. Reduce unnecessary alerts. Explain every warning."
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_HOST: str = "127.0.0.1"
    APP_PORT: int = 8000
    
    # Database
    DATABASE_URL: str = resolve_database_url()
    
    # CORS Allowed Origins (Supports comma-separated strings or JSON arrays)
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://healthcare-talentap.vercel.app",
        "https://healthcare-talentap-git-main-25a31a4469.vercel.app"
    ]
    ALLOWED_ORIGINS: Optional[Union[List[str], str]] = None
    
    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    def get_cors_origins(self) -> List[str]:
        origins = list(self.CORS_ORIGINS) if isinstance(self.CORS_ORIGINS, list) else [self.CORS_ORIGINS]
        if self.ALLOWED_ORIGINS:
            if isinstance(self.ALLOWED_ORIGINS, str):
                origins.extend([o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()])
            elif isinstance(self.ALLOWED_ORIGINS, list):
                origins.extend(self.ALLOWED_ORIGINS)
        # Deduplicate while preserving order
        seen = set()
        deduped = []
        for o in origins:
            if o not in seen:
                seen.add(o)
                # In production with credentials, strip wildcard '*'
                if self.ENVIRONMENT.lower() == "production" and o == "*":
                    continue
                deduped.append(o)
        return deduped or ["http://localhost:5173"]

    # Evaluation & Reference
    REFERENCE_DATA_VERSION: str = "v1.4-Hackathon-Core"
    DATASET_SOURCE_LABEL: str = "Validated Clinical Reference Rules & Synthetic Demo Records"
    DEMO_MODE: bool = True
    
    # Clinical Safety Notices
    CLINICAL_DISCLAIMER: str = (
        "DECISION-SUPPORT NOTICE: This software is an experimental prototype designed to assist "
        "qualified clinicians during medication review. It is NOT medically certified, NOT cleared for "
        "autonomous clinical use, and must NEVER independently prescribe, discontinue, or alter medications."
    )

settings = Settings()
