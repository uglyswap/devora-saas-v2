"""
Project and conversation-related Pydantic schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime


class ConversationMessage(BaseModel):
    """Single message in a conversation"""
    role: str = Field(..., pattern="^(user|assistant|system)$", description="Message role")
    content: str = Field(..., min_length=1, description="Message content")


class ProjectFileCreate(BaseModel):
    """Schema for creating a project file"""
    name: str = Field(..., min_length=1, max_length=255, description="File name with extension")
    content: str = Field(..., description="File content as string")
    language: str = Field(..., description="Programming language or file type")

    @field_validator('name')
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Validate filename doesn't contain dangerous characters"""
        if '..' in v or '/' in v or '\\' in v:
            raise ValueError('Filename cannot contain path traversal characters')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "name": "index.tsx",
                "content": "export default function Home() { return <div>Hello</div> }",
                "language": "typescript"
            }
        }


class ProjectFileResponse(ProjectFileCreate):
    """Response schema for project files"""
    pass


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=200, description="Project name")
    description: Optional[str] = Field(None, max_length=1000, description="Project description")
    project_type: Optional[str] = Field(None, description="Type of project (saas, ecommerce, blog, etc.)")


class ProjectCreate(ProjectBase):
    """Schema for creating a new project"""
    files: List[ProjectFileCreate] = Field(default=[], description="Initial project files")
    conversation_history: List[ConversationMessage] = Field(default=[], description="Conversation history")


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    files: Optional[List[ProjectFileCreate]] = None
    conversation_history: Optional[List[ConversationMessage]] = None
    github_repo_url: Optional[str] = None
    vercel_url: Optional[str] = None


class ProjectResponse(ProjectBase):
    """Response schema for projects"""
    id: str = Field(..., description="Project unique identifier")
    files: List[ProjectFileResponse] = Field(default=[], description="Project files")
    conversation_history: List[ConversationMessage] = Field(default=[], description="Conversation history")
    conversation_id: Optional[str] = Field(None, description="Associated conversation ID")
    github_repo_url: Optional[str] = Field(None, description="GitHub repository URL")
    vercel_url: Optional[str] = Field(None, description="Vercel deployment URL")
    created_at: datetime = Field(..., description="Project creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "prj_1234567890",
                "name": "My SaaS App",
                "description": "A full-stack SaaS application",
                "project_type": "saas",
                "files": [
                    {
                        "name": "app/page.tsx",
                        "content": "export default function Home() {...}",
                        "language": "typescript"
                    }
                ],
                "conversation_history": [
                    {"role": "user", "content": "Build me a SaaS app"},
                    {"role": "assistant", "content": "I'll create a Next.js app..."}
                ],
                "github_repo_url": "https://github.com/user/repo",
                "vercel_url": "https://app.vercel.app",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z"
            }
        }
