"""
Main application entry point for the FastAPI server.
"""
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi import APIRouter

loaded = load_dotenv() 

from routes.research import research_router
from utils.types import APIResponse
from config import get_config
from utils.logging import logger

app = FastAPI()

api_router = APIRouter()

config = get_config()

BASE_URL = "/api/v1"


@api_router.get("/healthz", response_model=APIResponse)
async def health_check():
    """Health check endpoint to verify the service is running."""
    return APIResponse(code=200, status="success", message=None, data={"status": "healthy"})



@api_router.get("/info", response_model=APIResponse)
async def info():
    """Endpoint to get basic information about the service."""

    all_models = [model for model in config.available_models.keys()]

    logger.debug(f"Available models: {all_models}")

    if config.is_prod:
        filterred_models = list(filter(lambda m: m != "default", all_models))
    else:
        filterred_models = all_models

    info_data = {
        "service": "AI Research Assistant",
        "version": "1.0.0",
        "description": "A service that provides AI-powered research capabilities.",
        "models": {
            "available_models": filterred_models,
        }
    }
    return APIResponse(code=200, status="success", message=None, data=info_data)


app.include_router(api_router, prefix=BASE_URL)
app.include_router(research_router, prefix=BASE_URL, tags=["research"])