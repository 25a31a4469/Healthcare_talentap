from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.config import settings
from backend.app.database import engine, Base, SessionLocal
from backend.app.reference_data import seed_reference_data
from backend.app.seed_demo import seed_demo_patients_and_analyses
from backend.app.api.router import api_router

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_reference_data(db)
        seed_demo_patients_and_analyses(db)
    finally:
        db.close()

# Auto-initialize database schema and seeds on load
init_db()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title=settings.APP_NAME,
    description=f"{settings.TAGLINE}\n\nClinical Decision Support Prototype. Not for autonomous clinical use.",
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include main API router
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {
        "app": settings.APP_NAME,
        "tagline": settings.TAGLINE,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "api_prefix": "/api",
        "disclaimer": settings.CLINICAL_DISCLAIMER
    }

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error", "detail": str(exc)}
    )
