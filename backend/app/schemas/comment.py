from pydantic import BaseModel, Field
from datetime import datetime

class CommentAuthor(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes= True

class CommentCreate(BaseModel):
    content: str= Field(..., min_length=1, max_length=2000)

class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000)

class CommentResponse(BaseModel):
    id: int
    content: str
    author: CommentAuthor
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True