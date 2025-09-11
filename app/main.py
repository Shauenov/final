from fastapi import FastAPI
from contextlib import asynccontextmanager
from starlette.middleware.cors import CORSMiddleware
from app.api.main import api_router
from app.core.db import engine
from sqlalchemy import text
from app.core.config import settings
from prometheus_fastapi_instrumentator import Instrumentator

@asynccontextmanager
async def lifespan(app: FastAPI):
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    yield

docs_url = "/docs"
redoc_url = "/redoc"
openapi_url = "/openapi.json"

app = FastAPI(
    lifespan=lifespan, docs_url=docs_url, redoc_url=redoc_url, openapi_url=openapi_url, swagger_ui_parameters={ "persistAuthorization": True }
)

Instrumentator().instrument(app).expose(app)

origins = (
    ["http://localhost", "http://localhost:3000", "https://juie.app"]
    if settings.ENVIRONMENT != "production"
    else ["https://juie.app", "http://localhost:3000"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
