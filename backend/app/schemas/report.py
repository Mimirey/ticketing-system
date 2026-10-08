from datetime import date
from pydantic import BaseModel

class StatusCount(BaseModel):
    OPEN: int = 0
    ASSIGNED: int = 0
    IN_PROGRESS: int = 0
    QA: int = 0
    DONE: int = 0
class StaffReport(BaseModel):
    staff_id: int
    staff_name: str
    total: int
    by_status: StatusCount
class TicketReportResponse(BaseModel):
    period: dict
    total: int
    by_status: StatusCount
    by_staff: list[StaffReport]