from pydantic import BaseModel, Field
from typing import List


class GeneratedComment(BaseModel):
    """Schema for a generated comment"""
    author: str = Field(..., description="Full name of the commenter")
    username: str = Field(..., description="Username (without @)")
    text: str = Field(..., description="Comment text content")
    likes: int = Field(..., ge=0, description="Number of likes (>= 0)")
    timestamp: str = Field(..., description="Time ago (e.g., '2h', '5 min', '1d')")
    
    class Config:
        json_schema_extra = {
            "example": {
                "author": "Maria Silva",
                "username": "maria_silva",
                "text": "Que vídeo incrível! Amei demais ❤️",
                "likes": 150,
                "timestamp": "2h"
            }
        }


class CommentGenerationRequest(BaseModel):
    """Request to generate comments"""
    video_title: str = Field(..., description="Title of the video")
    video_description: str = Field(default="", description="Description of the video")
    hashtags: List[str] = Field(default_factory=list, description="List of hashtags")
    num_comments: int = Field(default=15, ge=1, le=50, description="Number of comments to generate")


class CommentGenerationResponse(BaseModel):
    """Response with generated comments"""
    comments: List[GeneratedComment]
    total: int = Field(..., description="Total number of comments generated")
    txt_file_path: str = Field(..., description="Path to the generated txt file")


