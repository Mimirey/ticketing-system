from pydantic import BaseModel
from typing import List

class DashboardStatisticResponse(BaseModel):
    total_ticket: int
    open_ticket: int
    assigned_ticket: int
    in_progress_ticket: int
    qa_ticket: int
    done_ticket: int
    overdue_ticket: int
    high_priority_ticket: int
    medium_priority_ticket: int
    low_priority_ticket: int
    critical_priority_ticket: int

class StatusChartItem(BaseModel):
    status: str
    count: int
class PriorityChartItem(BaseModel):
    priority: str
    count: int
class StatusChartResponse(BaseModel):
    status: str
    count: int
class PriorityChartResponse(BaseModel):
    priority: str
    count: int