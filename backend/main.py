from fastapi import FastAPI

from backend.core.config import settings

app = FastAPI(title="Securities Research Tool")


@app.get("/")
async def root():
    return {
        "message": "Welcome to Securities Research Tool API",
        "environment": settings.ENVIRONMENT,
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
