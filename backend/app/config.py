import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "H4 — The Medication Safety Second Pair of Eyes"
    TAGLINE: str = "Catch the right risks. Reduce unnecessary alerts. Explain every warning."
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./healthcare.db")
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*"
    ]
    
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

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
