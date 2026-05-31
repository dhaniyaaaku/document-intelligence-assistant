"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import routes_analysis, routes_chat, routes_documents
from backend.database.db import init_db
from backend.utils.config import get_settings
from backend.utils.logging import configure_logging, get_logger


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    init_db()
    get_logger(__name__).info(
        "Document Intelligence Assistant ready on %s:%d",
        settings.api_host,
        settings.api_port,
    )
    yield


app = FastAPI(
    title="Document Intelligence Assistant",
    description="RAG + agentic AI over user-uploaded documents.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}


app.include_router(routes_documents.router)
app.include_router(routes_chat.router)
app.include_router(routes_analysis.router)


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )
