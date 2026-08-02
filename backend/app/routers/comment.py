from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.core.ticket_access import ensure_ticket_access
from app.models.user import User
from app.models.ticket import Ticket
from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse

router = APIRouter(prefix="/tickets", tags=["Comments"])


def get_ticket_or_404(ticket_id: int, db: Session) -> Ticket:
    ticket = db.query(Ticket).filter(
        Ticket.id == ticket_id, Ticket.is_deleted == False
    ).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket tidak ditemukan")
    return ticket


@router.post("/{ticket_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    ticket_id: int,
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = get_ticket_or_404(ticket_id, db)
    ensure_ticket_access(current_user, ticket)

    comment = Comment(
        ticket_id=ticket.id,
        author_id=current_user.id,
        content=data.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/{ticket_id}/comments", response_model=List[CommentResponse])
def list_comments(
    ticket_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ticket = get_ticket_or_404(ticket_id, db)
    ensure_ticket_access(current_user, ticket)

    return (
        db.query(Comment)
        .filter(Comment.ticket_id == ticket_id, Comment.is_deleted == False)
        .order_by(Comment.created_at.asc())
        .all()
    )


@router.patch("/{ticket_id}/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    ticket_id: int,
    comment_id: int,
    data: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.ticket_id == ticket_id,
        Comment.is_deleted == False,
    ).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Komentar tidak ditemukan")

    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Kamu hanya bisa mengedit komentar milikmu sendiri")

    comment.content = data.content
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{ticket_id}/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    ticket_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.ticket_id == ticket_id,
        Comment.is_deleted == False,
    ).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Komentar tidak ditemukan")

    if comment.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Kamu hanya bisa menghapus komentar milikmu sendiri")

    comment.is_deleted = True
    db.commit()