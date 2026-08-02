from pydantic import BaseModel
from datetime import datetime

class AttachmentUploader(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes= True

class AttachmentResponse(BaseModel):
    id: int
    original_filename: str
    file_size: int
    content_type: str
    uploaded_by: AttachmentUploader
    created_at: datetime

    class Config:
        from_attributes = True

