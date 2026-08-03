from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from app.services.export_excel import export_ticket_excel
from app.services.export_pdf import export_ticket_pdf
from app.services.sla import calculate_sla
from app.db.database import get_db
from app.core.dependencies import get_current_user, require_role
from app.core.ticket_utils import generate_ticket_number
from app.core.activity_log_utils import log_activity
from app.models.user import User
from app.models.ticket import Ticket
from app.models.enums import TicketStatus, TicketPriority, TicketType
from app.models.ticket_history import TicketHistory
from app.schemas.ticket_history import TicketHistoryResponse
from app.core.history_utils import log_history
from app.core.notification_utils import create_notification
from app.schemas.ticket import (
    TicketCreate, TicketResponse, TicketAssign, TicketStatusUpdate, TicketPriorityUpdate, TicketDueDateUpdate
)

router = APIRouter(prefix="/tickets", tags=["Tickets"])


ALLOWED_TRANSITIONS = {
    TicketStatus.OPEN: [TicketStatus.ASSIGNED],
    TicketStatus.ASSIGNED: [TicketStatus.IN_PROGRESS],
    TicketStatus.IN_PROGRESS: [TicketStatus.QA],
    TicketStatus.QA: [TicketStatus.DONE, TicketStatus.IN_PROGRESS],  
    TicketStatus.DONE: [],  
}


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
def create_ticket(
    data: TicketCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = Ticket(
        type=data.type,
        title=data.title,
        description=data.description,
        priority=data.priority,
        module=data.module,
        due_date=data.due_date,
        status=TicketStatus.OPEN,
        reporter_id=current_user.id,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)

    ticket.ticket_number = generate_ticket_number(ticket.id)
    db.commit()
    db.refresh(ticket)
    pm_users = (
        db.query(User)
        .filter(User.is_deleted == False)
        .filter(User.role.has(name="PM_IT"))
        .all()
    )
    for pm in pm_users:
        create_notification(
            db=db,
            user_id=pm.id,
            ticket_id=ticket.id,
            title="Ticket Baru",
            message=f"Ticket {ticket.ticket_number} telah dibuat.",
        )
    log_activity(db, current_user.id, "CREATE_TICKET", f"{current_user.name} membuat ticket {ticket.ticket_number}")
    db.commit()

    sla=calculate_sla(ticket)
    ticket.sla_status = sla["sla_status"]
    ticket.remaining_hours = sla["remaining_hours"]
    return ticket


@router.get("", response_model=List[TicketResponse])
def list_tickets(
    search: str | None = Query(None),
    status: TicketStatus | None = Query(None),
    priority: TicketPriority | None = Query(None),
    type: TicketType | None = Query(None),    
    pic_id: int | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),

    sort_by: str = Query("created_at"),
    order: str = Query("desc"),

    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Ticket).filter(Ticket.is_deleted == False)
    if search:
        query = query.filter(
            (Ticket.title.ilike(f"%{search}%")) |
            (Ticket.ticket_number.ilike(f"%{search}%")) |
            (Ticket.module.ilike(f"%{search}%")) |
            (User.name.ilike(f"%{search}"))
        )
    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if type:
        query = query.filter(Ticket.type == type)
    if pic_id:
        query= query.filter(Ticket.pic_id == pic_id)

    if current_user.role.name == "USER":
        query = query.filter(Ticket.reporter_id == current_user.id)
    elif current_user.role.name == "STAFF_IT":
        query = query.filter(Ticket.pic_id == current_user.id)

    SORTABLE_FIELDS ={"created_at", "updated_at", "priority", "status"}
    sort_field = sort_by if sort_by in SORTABLE_FIELDS else "created_at"
    sort_column = getattr(Ticket, sort_field)

    if order.lower() == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())

    offset = (page - 1) * page_size
    tickets = (
        query
        .offset(offset)
        .limit(page_size)
        .all()
    )
    for ticket in tickets:
        sla = calculate_sla(ticket)
        ticket.sla_status = sla["sla_status"]
        ticket.remaining_hours = sla["remaining_hours"]
    return tickets
@router.get("/export")
def export_excel(
    current_user: User = Depends(require_role("PM_IT")),
    db: Session = Depends(get_db),
):
    tickets = (
        db.query(Ticket)
        .filter(Ticket.is_deleted == False)
        .all()
    )

    excel = export_ticket_excel(tickets)

    return StreamingResponse(
        excel,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "attachment; filename=tickets.xlsx"
        },
    )
@router.get("/export/pdf")
def export_pdf(
    current_user: User = Depends(require_role("PM_IT")),
    db: Session = Depends(get_db),
):
    tickets = (
        db.query(Ticket)
        .filter(Ticket.is_deleted == False)
        .all()
    )

    pdf = export_ticket_pdf(tickets)

    return StreamingResponse(
        pdf,
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=tickets.pdf"
        },
    )

@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id, Ticket.is_deleted == False
    ).first()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket tidak ditemukan")

    if current_user.role.name == "USER" and ticket.reporter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Kamu tidak punya akses ke ticket ini")
    sla = calculate_sla(ticket)
    ticket.sla_status = sla["sla_status"]
    ticket.remaining_hours = sla["remaining_hours"]
    return ticket


@router.patch("/{ticket_id}/assign", response_model=TicketResponse)
def assign_ticket(
    ticket_id: int,
    data: TicketAssign,
    current_user: User = Depends(require_role("PM_IT")),
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id, Ticket.is_deleted == False
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket tidak ditemukan")
    if ticket.status == TicketStatus.DONE:
        raise HTTPException(status_code=400, detail="Ticket sudah Done dan terkunci")

    staff = db.query(User).filter(
        User.id == data.pic_id, User.is_deleted == False
    ).first()
    if not staff or staff.role.name != "STAFF_IT":
        raise HTTPException(status_code=400, detail="PIC harus user dengan role STAFF_IT")

    old_pic_name = ticket.pic.name if ticket.pic else "Belum ada"
    ticket.pic_id = staff.id
    log_history(db, ticket.id, current_user.id, "pic", old_pic_name, staff.name)
    create_notification(
        db=db,
        user_id=staff.id,
        ticket_id=ticket.id,
        title="Ticket Ditugaskan",
        message=f"Kamu ditugaskan untuk ticket {ticket.ticket_number}: {ticket.title}",
    )

    if ticket.status == TicketStatus.OPEN:
        old_status = ticket.status.value
        ticket.status = TicketStatus.ASSIGNED
        log_history(db, ticket.id, current_user.id, "status", old_status, ticket.status.value)
    log_activity(db, current_user.id, "ASSIGN", f"{current_user.name} menugaskan {staff.name} ke ticket {ticket.ticket_number}")
    db.commit()
    db.refresh(ticket)
    return ticket


@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_status(
    ticket_id: int,
    data: TicketStatusUpdate,
    current_user: User = Depends(require_role("PM_IT", "STAFF_IT")),
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id, Ticket.is_deleted == False
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket tidak ditemukan")
    if ticket.status == TicketStatus.DONE:
        raise HTTPException(status_code=400, detail="Ticket sudah Done dan terkunci")

    if current_user.role.name == "STAFF_IT" and ticket.pic_id != current_user.id:
        raise HTTPException(status_code=403, detail="Kamu bukan PIC ticket ini")

    allowed_next = ALLOWED_TRANSITIONS.get(ticket.status, [])
    if data.status not in allowed_next:
        raise HTTPException(
            status_code=400,
            detail=f"Tidak bisa ubah status dari {ticket.status.value} ke {data.status.value}",
        )

    old_status = ticket.status.value
    ticket.status = data.status
    log_history(db, ticket.id, current_user.id, "status", old_status, data.status.value)
    if ticket.reporter_id != current_user.id:
            create_notification(
                db=db,
                user_id=ticket.reporter_id,
                ticket_id=ticket.id,
                title="Status Ticket Berubah",
                message=f"Ticket {ticket.ticket_number} kamu sekarang berstatus {data.status.value}",
            )
    log_activity(db, current_user.id, "UPDATE_STATUS", f"{current_user.name} mengubah status ticket {ticket.ticket_number} ke {data.status.value}")
    db.commit()
    db.refresh(ticket)
    return ticket
@router.patch("/{ticket_id}/priority", response_model=TicketResponse)
def update_priority(
    ticket_id: int,
    data: TicketPriorityUpdate,
    current_user: User = Depends(require_role("PM_IT")),
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id, Ticket.is_deleted == False
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket tidak ditemukan")
    if ticket.status == TicketStatus.DONE:
        raise HTTPException(status_code=400, detail="Ticket sudah Done dan terkunci")

    old_priority = ticket.priority.value
    ticket.priority = data.priority
    log_history(db, ticket.id, current_user.id, "priority", old_priority, data.priority.value)

    db.commit()
    db.refresh(ticket)
    return ticket

@router.get("/{ticket_id}/history", response_model=List[TicketHistoryResponse])
def get_ticket_history(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id, Ticket.is_deleted == False
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket tidak ditemukan")

    if current_user.role.name == "USER" and ticket.reporter_id != current_user.id:
        raise HTTPException(status_code=403, detail="Kamu tidak punya akses ke ticket ini")

    return (
        db.query(TicketHistory)
        .filter(TicketHistory.ticket_id == ticket_id)
        .order_by(TicketHistory.changed_at.desc())
        .all()
    )

@router.delete("/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
): 
    ticket = (
        db.query(Ticket)
        .filter(
            Ticket.id == ticket_id,
            Ticket.is_deleted == False,
        )
        .first()
    )
    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket tidak ditemukan",
        )
    if (
        current_user.role.name != "PM_IT"
        and ticket.reporter_id != current_user.id
    ):
        raise HTTPException(
            status_code=403,
            detail="Tidak punya akses",
    )
    if ticket.status == TicketStatus.DONE:
        raise HTTPException(
            status_code=400,
            detail="Ticket sudah selesai",
        )
    ticket.is_deleted = True
    log_activity(db, current_user.id, "DELETE_TICKET", f"{current_user.name} menghapus ticket {ticket.ticket_number}")
    db.commit()
    return {
        "message": "Ticket berhasil dihapus"
    }
@router.patch("/{ticket_id}/due-date", response_model=TicketResponse)
def update_due_date(
    ticket_id: int,
    data: TicketDueDateUpdate,
    current_user: User = Depends(require_role("PM_IT")),
    db: Session = Depends(get_db),
):
    ticket = (
        db.query(Ticket)
        .filter(
            Ticket.id == ticket_id,
            Ticket.is_deleted == False,
        )
        .first()
    )

    if not ticket:
        raise HTTPException(404, "Ticket tidak ditemukan")

    ticket.due_date = data.due_date

    db.commit()
    db.refresh(ticket)

    return ticket