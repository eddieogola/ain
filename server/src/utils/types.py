"""
Common types and schemas used across the application.
"""
from typing import Dict, List, Union, Literal

from pydantic import BaseModel, Field

class APIResponse(BaseModel):
    """Generic schema for API responses."""
    code: int
    status: Literal["success", "error"]
    message: str | None = None
    data: Union[Dict, List, None] = None


# SUMMARIZE_WEBPAGE structured output model
class Summary(BaseModel):
    """Schema for webpage content summarization."""
    summary: str = Field(description="Concise summary of the webpage content")
    key_excerpts: str = Field(description="Important quotes and excerpts from the content")
