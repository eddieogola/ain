"""
Main application entry point for the FastAPI server.
"""
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi import APIRouter

from utils.logging import logger

loaded = load_dotenv() 

from routes.research import research_router
from utils.types import APIResponse

app = FastAPI()

api_router = APIRouter()

BASE_URL = "/api/v1"


@api_router.get("/healthz", response_model=APIResponse)
async def health_check():
    """Health check endpoint to verify the service is running."""
    return APIResponse(code=200, status="success", message=None, data={"status": "healthy"})

app.include_router(api_router, prefix=BASE_URL)
app.include_router(research_router, prefix=BASE_URL, tags=["research"])
