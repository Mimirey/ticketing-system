from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class HistoryActor(BaseModel):
    id: int
    name: str
    class Config:
        from_attribute= True

class TicketHistoryResponse(BaseModel):
    id: int
    field_changed: str
    old_value: Optional[str]
    new_value: str
    changed_by: HistoryActor
    changed_at: datetime

    class Config:
        from_attributes= True

