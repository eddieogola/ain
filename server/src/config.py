"""
Configuration module for the application.
"""
import os
from functools import lru_cache

from tavily import TavilyClient
from dotenv import load_dotenv
load_dotenv()

from memory.short_term import short_memory

is_prod = True if os.getenv("ENVIRONMENT") == "prod" else False

from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings

# Environment variables
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
MODEL_BASE_URL = os.getenv("MODEL_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
MODEL_API_KEY = os.getenv("MODEL_API_KEY")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_BASE_URL = os.getenv("GEMINI_BASE_URL")


# Validate required environment variables
required_vars = {
    "TAVILY_API_KEY": TAVILY_API_KEY,
    "MODEL_BASE_URL": MODEL_BASE_URL,
    "MODEL_NAME": MODEL_NAME,
    "MODEL_API_KEY": MODEL_API_KEY,
    "EMBEDDING_MODEL_NAME": EMBEDDING_MODEL_NAME,
    "GEMINI_API_KEY": GEMINI_API_KEY,
    "GEMINI_BASE_URL": GEMINI_BASE_URL,
}

for var_name, var_value in required_vars.items():
    if not var_value:
        raise ValueError(f"{var_name} environment variable is not set.")


# Available models configuration
# default will only be available in dev mode
available_models = {
    "default": {
        "model": MODEL_NAME,
        "api_key": MODEL_API_KEY,
        "base_url": MODEL_BASE_URL,
    },
    "Gemini 2.5 Flash":{
        "model": "google_genai:gemini-2.5-flash",
        "api_key": GEMINI_API_KEY,
        "base_url": GEMINI_BASE_URL,
    },
    "Gemini 2.5 Pro":{
        "model": "google_genai:gemini-2.5-pro",
        "api_key": GEMINI_API_KEY,
        "base_url": GEMINI_BASE_URL,
    }
}


# defaults
_model_params = {
    "model": available_models["Gemini 2.5 Flash"]["model"] if is_prod else MODEL_NAME,
    "api_key": available_models["Gemini 2.5 Flash"]["api_key"] if is_prod else MODEL_API_KEY,
    "base_url": available_models["Gemini 2.5 Flash"]["base_url"] if is_prod else MODEL_BASE_URL,
}


_embed_model_params = {
    "model": EMBEDDING_MODEL_NAME,
    "openai_api_base": MODEL_BASE_URL,
    "api_key": MODEL_API_KEY,
}

# create an absolute path to the uploads directory
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "rag/data/uploads")
VECTOR_STORE_DIR = os.path.join(os.path.dirname(__file__), "rag/data/storage")

class Config:
    """
    Configuration class for managing application settings.
    """
    
    def __init__(self):
        self.web_search_client = TavilyClient(api_key=TAVILY_API_KEY)
        self.llm =  init_chat_model(**_model_params)
        self.writer_llm = init_chat_model(**_model_params)
        self.embed_model = OpenAIEmbeddings(**_embed_model_params)
        self.short_term_memory = short_memory
        self.upload_dir = UPLOAD_DIR
        self.vector_store_dir = VECTOR_STORE_DIR
        self.max_chunk_size = 1000
        self.available_models = available_models
        self.model_params = _model_params
        self.is_prod = is_prod


@lru_cache(maxsize=1)
def get_config() -> Config:
    """
    Returns a Config object with default settings.
    Returns:
        Config: A new instance of the Config class with default configuration values.
    """

    return Config()


def update_config(model_params):
    """
    Updates the cached Config object with new model parameters.
    Args:
        model_params (dict): New model parameters to update the configuration.
    """
    get_config.cache_clear()

    _model_params.update(model_params)