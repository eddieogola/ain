"""
Research endpoint module for handling research-related requests.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage
import base64
import os

from rag.indexer import Indexer
from utils.types import APIResponse
from utils.logging import logger

from agents.main import agent
from agents.rag import agent as rag_agent
from config import get_config

config = get_config()

research_router = APIRouter()

class ResearchMessage(BaseModel):
    message: str

class ChatMessage(BaseModel):
    message: str

class DocumentUpload(BaseModel):
    filename: str
    file_data: str  # Base64 encoded file

thread = {"configurable": {"thread_id": "1", "recursion_limit": 50}}
chat_thread = {"configurable": {"thread_id": "chat_docs", "recursion_limit": 50}}

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
        logger.debug(f"Received research request: {research_message}")

        convo_messages.append(HumanMessage(content=research_message.message))

        model_response = await agent.ainvoke({"messages": convo_messages}, config=thread)
        
        logger.debug(f"Model response: {model_response}")

        messages = model_response.get("messages")
        report = model_response.get("final_report", None)

        if report:

            convo_messages.append(AIMessage(content=report))
            response = {
                "code": 200,
                "status": "success",
                "message": None,
                "data": {
                    "message": report,
                }
            }
            return APIResponse(**response)

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

@research_router.post("/doc-index", response_model=APIResponse)
async def document_indexing_endpoint(document: DocumentUpload):
    """
    Endpoint to receive and process uploaded PDF documents.
    """
    if not document.filename or not document.file_data:
        response = {
            "code": 400,
            "status": "error",
            "message": "Filename and file data are required",
            "data": None
        }
        return APIResponse(**response)
    
    try:
        logger.debug(f"Received document upload: {document.filename}")
        indexer = Indexer(config)
        
        # Create a directory to store uploaded files if it doesn't exist
        os.makedirs(config.upload_dir, exist_ok=True)

        # Decode the base64 file data
        file_bytes = base64.b64decode(document.file_data)
        
        # Save the file
        file_path = os.path.join(config.upload_dir, document.filename)
        with open(file_path, "wb") as f:
            f.write(file_bytes)
        
        logger.debug(f"Document saved to {file_path}")
        

        indexer.index_documents(file_path=file_path)
        
        response = {
            "code": 200,
            "status": "success",
            "message": None,
            "data": {
                "message": f"Document '{document.filename}' uploaded and indexed successfully",
                "file_path": file_path
            }
        }
        
        return APIResponse(**response)
    
    except Exception as e:
        logger.exception(f"Exception occurred in document indexing endpoint: {str(e)}")
        
        response = {
            "code": 500,
            "status": "error",
            "message": f"An error occurred while processing the document: {str(e)}",
            "data": None
        }
        
        return APIResponse(**response)
    

@research_router.post("/chat_docs", response_model=APIResponse)
async def chat_documents_endpoint(query: ChatMessage):
    """
    Endpoint to handle queries against indexed documents.
    """
    if not query:
        response = {
            "code": 400,
            "status": "error",
            "message": "Query parameter is required",
            "data": None
        }
        return APIResponse(**response)
    
    try:
        logger.debug(f"Received document chat query: {query}")

        model_response = await rag_agent.ainvoke({"messages": [{"role": "user", "content": query.message}]}, config=chat_thread)

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
        logger.exception(f"Exception occurred in document chat endpoint: {str(e)}")

        response = {
            "code": 500,
            "status": "error",
            "message": "An error occurred while processing the document chat",
            "data": None
        }

        return APIResponse(**response)