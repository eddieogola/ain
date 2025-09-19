"""
Configuration module for the application.
"""
import os
from functools import lru_cache

from tavily import TavilyClient

from memory.short_term import short_memory

is_prod = True if os.getenv("ENVIRONMENT") == "prod" else False

from langchain_google_genai import ChatGoogleGenerativeAI

from utils.logging import logger

# https://www.tavily.com/
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

MODEL_BASE_URL =  os.getenv("MODEL_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
MODEL_API_KEY = os.getenv("MODEL_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY environment variable is not set.")

# if not MODEL_BASE_URL:
#     raise ValueError("MODEL_BASE_URL environment variable is not set.")

if not MODEL_NAME:
    raise ValueError("MODEL_NAME environment variable is not set.")

if not MODEL_API_KEY:
    raise ValueError("MODEL_API_KEY environment variable is not set.")

model_params = {
    "model": MODEL_NAME,
    "api_key": MODEL_API_KEY,
    # "base_url": MODEL_BASE_URL,
}


class Config:
    """
    Configuration class for managing application settings.
    """
    
    def __init__(self):
        self.web_search_client = TavilyClient(api_key=TAVILY_API_KEY)
        self.llm = ChatGoogleGenerativeAI(**model_params)
        self.writer_llm = ChatGoogleGenerativeAI(**model_params)
        self.short_term_memory = short_memory
        self.max_chunk_size = 1000 #To control the size of text chunks for processing and to fit in the context window of the LLM.


@lru_cache(maxsize=1)
def get_config() -> Config:
    """
    Returns a Config object with default settings.
    Returns:
        Config: A new instance of the Config class with default configuration values.
    """

    return Config()