
from fastapi import APIRouter

from utils.types import APIResponse
from utils.logging import logger
from pydantic import BaseModel

from config import get_config, update_config

config = get_config()


info_router = APIRouter()

class ModelUpdateRequest(BaseModel):
    model_name: str

@info_router.get("/info", response_model=APIResponse)
async def info():
    """Endpoint to get basic information about the service."""

    all_models = [model for model in config.available_models.keys()]

    if config.is_prod:
        filtered_models = list(filter(lambda m: m != "default", all_models))
    else:
        filtered_models = all_models

    # get model key of the active model by checking config.available_models values against the config.model_params.get("model") the active_model is the corresponding key
    active_model = next((k for k, v in config.available_models.items() if v.get("model") == config.model_params.get("model")), None)

    info_data = {
        "service": "Africa Insights Navigator",
        "version": "0.1.0",
        "description": "A service that provides AI-powered due diligence research capabilities.",
        "models": {
            "available_models": filtered_models,
            "active_model": active_model
        }
        }
    return APIResponse(code=200, status="success", message=None, data=info_data)

@info_router.post("/update_model", response_model=APIResponse)
async def update_model(request: ModelUpdateRequest):
    """Function to update the model dynamically."""
    try:
        if request.model_name in config.available_models:
            update_config(model_params=config.available_models[request.model_name])
            logger.info(f"Model updated to {request.model_name}")
            
            response = {
                "code": 200,
                "status": "success",
                "message": f"Model updated to {request.model_name}"
            }
        else:
            logger.warning(f"Attempted to update to unsupported model: {request.model_name}")
            response = {
                "code": 400,
                "status": "error",
                "message": f"Unsupported model: {request.model_name}"
            }
    except Exception as e:
        logger.exception(f"Exception occurred while updating model: {str(e)}")
        response = {
            "code": 500,
            "status": "error",
            "message": "An error occurred while updating the model"
        }

    return APIResponse(**response)