from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ActivityActor(BaseModel):
    id: int
    name: str
    class Config:
        from_attributes= True
class ActivityLogResponse(BaseModel):
    id:int
    action: str
    description: str
    user: Optional[ActivityActor]
    created_at: datetime
    class Config:
        from_attributes= True