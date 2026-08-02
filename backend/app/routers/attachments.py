import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.core.ticket_access import ensure_ticket_access
from app.core.file_utils import (
    validate_file, generate_stored_filename, get_ticket_upload_dir
)
from app.models.user import User
from app.models.ticket import Ticket
from app.models.attachment import Attachment
from app.schemas.attachment import AttachmentResponse

router = APIRouter(prefix="/tickets", tags=["Attachments"])


def get_ticket_or_404(ticket_id: int, db: Session) -> Ticket:
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id, Ticket.is_deleted == False
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket tidak ditemukan")
    return ticket


@router.post("/{ticket_id}/attachments", response_model=AttachmentResponse, status_code=status.HTTP_201_CREATED)
async def upload_attachment(
    ticket_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = get_ticket_or_404(ticket_id, db)
    ensure_ticket_access(current_user, ticket)

    contents = await file.read()
    file_size = len(contents)

    error = validate_file(file.content_type, file_size)
    if error:
        raise HTTPException(status_code=400, detail=error)

    stored_name = generate_stored_filename(file.filename)
    upload_dir = get_ticket_upload_dir(ticket_id)
    full_path = os.path.join(upload_dir, stored_name)

    with open(full_path, "wb") as f:
        f.write(contents)

    attachment = Attachment(
        ticket_id=ticket.id,
        uploaded_by_id=current_user.id,
        original_filename=file.filename,
        stored_filename=stored_name,
        file_path=full_path,
        file_size=file_size,
        content_type=file.content_type,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


@router.get("/{ticket_id}/attachments", response_model=List[AttachmentResponse])
def list_attachments(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = get_ticket_or_404(ticket_id, db)
    ensure_ticket_access(current_user, ticket)

    return (
        db.query(Attachment)
        .filter(Attachment.ticket_id == ticket_id, Attachment.is_deleted == False)
        .order_by(Attachment.created_at.desc())
        .all()
    )


@router.get("/{ticket_id}/attachments/{attachment_id}/download")
def download_attachment(
    ticket_id: int,
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = get_ticket_or_404(ticket_id, db)
    ensure_ticket_access(current_user, ticket)

    attachment = db.query(Attachment).filter(
        Attachment.id == attachment_id,
        Attachment.ticket_id == ticket_id,
        Attachment.is_deleted == False,
    ).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment tidak ditemukan")

    if not os.path.exists(attachment.file_path):
        raise HTTPException(status_code=404, detail="File fisik tidak ditemukan di server")

    return FileResponse(
        path=attachment.file_path,
        filename=attachment.original_filename,
        media_type=attachment.content_type,
    )


@router.delete("/{ticket_id}/attachments/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attachment(
    ticket_id: int,
    attachment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    attachment = db.query(Attachment).filter(
        Attachment.id == attachment_id,
        Attachment.ticket_id == ticket_id,
        Attachment.is_deleted == False,
    ).first()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment tidak ditemukan")

    is_owner = attachment.uploaded_by_id == current_user.id
    is_pm = current_user.role.name == "PM_IT"
    if not (is_owner or is_pm):
        raise HTTPException(status_code=403, detail="Kamu tidak punya izin menghapus attachment ini")

    attachment.is_deleted = True
    db.commit()