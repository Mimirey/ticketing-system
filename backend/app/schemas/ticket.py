from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.enums import TicketType, TicketStatus,TicketPriority

class TicketCreate(BaseModel):
    type: TicketType
    title: str = Field (..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    priority: TicketPriority= TicketPriority.LOW
    module: Optional[str]= None

class TicketResponse(BaseModel):
    id: int
    ticket_number:str
    type: TicketType
    title: str
    description: str
    priority: TicketPriority
    status: TicketStatus
    module: Optional[str]
    reporter_id: int
    pic_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes= True
class TicketAssign(BaseModel):
    pic_id: int


class TicketStatusUpdate(BaseModel):
    status: TicketStatus


class TicketPriorityUpdate(BaseModel):
    priority: TicketPriority