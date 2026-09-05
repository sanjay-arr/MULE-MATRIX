from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings
from backend.app.api.router import api_router
from fastapi.responses import RedirectResponse

import os

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="FastAPI backend exposing Mule Matrix intelligence through REST APIs.",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    root_path="",
)

# CORS Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "")

origins = [
    "https://mule-matrix.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

if FRONTEND_URL and FRONTEND_URL not in origins:
    origins.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/docs")


@app.get("/health", include_in_schema=False)
def health():
    return {
        "status": "healthy",
        "service": "mule-matrix",
        "dataset": "initialized",
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)