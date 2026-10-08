from datetime import date, datetime,time, timezone
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.models.user import User

STATUS_LIST =[ "OPEN","ASSIGNED", "IN_PROGRESS", "QA", "DONE"]
def get_ticket_report(
        db: Session,
        start_date: date,
        end_date: date,
        staff_ids: list[int] | None=None,
):
    start_datetime = datetime.combine(
        start_date,
        time.min,
        tzinfo=timezone.utc
    )
    end_datetime = datetime.combine(
        end_date,
        time.max,
        tzinfo=timezone.utc
    )
    query =(
        db.query(
            Ticket.pic_id,
            User.name.label("staff_name"),
            Ticket.status,
            func.count(Ticket.id).label("total"),
        )
        .outerjoin(User,User.id == Ticket.pic_id)
        .filter(
            Ticket.created_at >= start_datetime,
            Ticket.created_at <= end_datetime,
            Ticket.is_deleted == false,
        )
    )
    if staff_ids:
        query = query.filter(Ticket.pic_id.in_(staff_ids))

    rows =(
        query
        .group_by(
            Ticket.pic_id,
            User.name,
            Ticket.status,
        )
        .all()
    )
    total = 0
    by_status ={
        status: 0
        for status in STATUS_LIST
    }
    staff_data= {}
    for row in rows:
        status = row.status.value if hasattr(row.status, "value") else row.status
        count = row.total
        total += count

        if status in by_status:
            by_status[status] += count
        if row.pic_id is None:
            continue
        if row.pic_id not in staff_data:
            staff_data[row.pic_id] = {
                "staff_id": row.pic_id,
                "staff_name": row.staff_name or "Unknown",
                "total": 0,
                "by_status": {
                    status_name: 0
                    for status_name in STATUS_LIST
                },
            }
        staff_data[row.pic_id]["total"] += count
        if status in staff_data[row.pic_id]["by_status"]:
            staff_data[row.pic_id]["by_status"][status] += count
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        "total": total,
        "by_status": by_status,
        "by_staff": list(staff_data.values()),
    }