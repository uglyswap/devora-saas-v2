"""
Code generation request and response schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from .project_schemas import ProjectFileResponse, ConversationMessage


class GenerateRequest(BaseModel):
    """Base schema for code generation requests"""
    message: str = Field(..., min_length=1, max_length=10000, description="User prompt for code generation")
    model: str = Field(default="gpt-4o", description="LLM model to use")
    api_key: str = Field(..., min_length=1, description="API key for LLM provider")
    conversation_history: List[ConversationMessage] = Field(default=[], description="Previous conversation context")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Create a landing page with a hero section",
                "model": "gpt-4o",
                "api_key": "sk-...",
                "conversation_history": []
            }
        }


class GenerateResponse(BaseModel):
    """Response schema for simple generation"""
    response: str = Field(..., description="Generated code or response")
    model: str = Field(..., description="Model used for generation")
    context_compressed: bool = Field(default=False, description="Whether context compression was applied")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "<!DOCTYPE html><html>...",
                "model": "gpt-4o",
                "context_compressed": False
            }
        }


class AgenticRequest(BaseModel):
    """Schema for agentic code generation (HTML/CSS/JS)"""
    message: str = Field(..., min_length=1, max_length=10000, description="User request")
    model: str = Field(default="gpt-4o", description="LLM model")
    api_key: str = Field(..., min_length=1, description="API key")
    current_files: List[ProjectFileResponse] = Field(default=[], description="Current project files")
    conversation_history: List[ConversationMessage] = Field(default=[], description="Conversation history")
    project_id: Optional[str] = Field(None, description="Project ID for context")
    user_id: Optional[str] = Field(None, description="User ID for memory integration")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Add a contact form with validation",
                "model": "gpt-4o",
                "api_key": "sk-...",
                "current_files": [
                    {"name": "index.html", "content": "...", "language": "html"}
                ],
                "conversation_history": [],
                "project_id": "prj_123",
                "user_id": "usr_456"
            }
        }


class FullStackRequest(BaseModel):
    """Schema for full-stack project generation (Next.js/TypeScript/Supabase)"""
    message: str = Field(..., min_length=1, max_length=10000, description="Project requirements")
    model: str = Field(default="gpt-4o", description="LLM model")
    api_key: str = Field(..., min_length=1, description="API key")
    current_files: List[ProjectFileResponse] = Field(default=[], description="Existing files")
    conversation_history: List[ConversationMessage] = Field(default=[], description="Conversation history")
    project_type: Optional[str] = Field(None, description="Project type (saas, ecommerce, blog, dashboard, api)")
    project_id: Optional[str] = Field(None, description="Project ID")
    user_id: Optional[str] = Field(None, description="User ID for memory")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Build a SaaS app with authentication and Stripe billing",
                "model": "gpt-4o",
                "api_key": "sk-...",
                "current_files": [],
                "conversation_history": [],
                "project_type": "saas",
                "project_id": "prj_123",
                "user_id": "usr_456"
            }
        }


class ProgressEvent(BaseModel):
    """Progress event during generation"""
    event: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data")
    timestamp: str = Field(..., description="Event timestamp (ISO format)")


class CompressionStats(BaseModel):
    """Context compression statistics"""
    compressed: bool = Field(..., description="Whether compression was applied")
    total: Optional[Dict[str, Any]] = Field(None, description="Total compression statistics")


class AgenticResponse(BaseModel):
    """Response schema for agentic generation"""
    success: bool = Field(..., description="Whether generation succeeded")
    files: List[ProjectFileResponse] = Field(..., description="Generated files")
    message: str = Field(..., description="Summary message")
    iterations: int = Field(default=1, description="Number of agent iterations")
    progress_events: List[ProgressEvent] = Field(default=[], description="Generation progress events")
    context_compressed: bool = Field(default=False, description="Context compression applied")
    compression_stats: Optional[CompressionStats] = Field(None, description="Compression statistics")
    memory_enabled: bool = Field(default=False, description="Whether persistent memory was used")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "files": [
                    {"name": "index.html", "content": "...", "language": "html"},
                    {"name": "styles.css", "content": "...", "language": "css"}
                ],
                "message": "Successfully generated 2 files",
                "iterations": 1,
                "progress_events": [],
                "context_compressed": False,
                "memory_enabled": True
            }
        }


class FullStackResponse(AgenticResponse):
    """Response schema for full-stack generation"""
    generation_mode: str = Field(default="fullstack", description="Generation mode")
    stack: Dict[str, List[str]] = Field(..., description="Tech stack used")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "files": [
                    {"name": "app/page.tsx", "content": "...", "language": "typescript"}
                ],
                "message": "Generated full-stack Next.js app",
                "iterations": 3,
                "progress_events": [],
                "context_compressed": False,
                "memory_enabled": True,
                "generation_mode": "fullstack",
                "stack": {
                    "frontend": ["next.js", "react", "tailwind", "shadcn/ui"],
                    "backend": ["api-routes", "server-actions"],
                    "database": ["supabase", "postgresql"]
                }
            }
        }
