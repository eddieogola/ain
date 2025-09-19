"""
Research endpoint module for handling research-related requests.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage

from utils.types import APIResponse
from utils.logging import logger

from agents.main import agent


research_router = APIRouter()

class ResearchMessage(BaseModel):
    message: str

thread = {"configurable": {"thread_id": "1", "recursion_limit": 50}}

convo_messages = []

@research_router.post("/research", response_model=APIResponse)
async def research_endpoint(research_message: ResearchMessage):
    if not research_message.message:
        response = {
            "code": 400,
            "status": "error",
            "message": "Message content is required",
            "data": None
        }
        return APIResponse(**response)
    try:
        logger.debug(f"Received research request: {research_message.message}")

        convo_messages.append(HumanMessage(content=research_message.message))

        model_response = await agent.ainvoke({"messages": convo_messages}, config=thread)
        
        logger.debug(f"Model response: {model_response}")

        messages = model_response.get("messages")

        if messages:
            logger.debug(f"Model response messages: {convo_messages}")
            last_message = messages[-1]
            if last_message.type == "ai":
                convo_messages.append(AIMessage(content=last_message.content))
                response = {
                        "code": 200,
                        "status": "success",
                        "message": None,
                        "data": {
                            "message": last_message.content
                        }
                    }
        else:
            response = {
                "code": 500,
                "status": "error",
                "message": "No response from the model",
                "data": None
            }
                

        return APIResponse(**response)
    except Exception as e:
        logger.exception(f"Exception occurred in research endpoint: {str(e)}")

        response = {
            "code": 500,
            "status": "error",
            "message": "An error occurred while processing the research",
            "data": None
        }

        return APIResponse(**response)