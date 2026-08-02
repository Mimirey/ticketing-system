import os
import uuid

MAX_FILE_SIZE= 5 * 1024 *1024
ALLOWED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  
}
UPLOAD_ROOT = "uploads/tickets"


def validate_file(content_type: str, file_size: int):
    if content_type not in ALLOWED_CONTENT_TYPES:
        return f"Tipe file '{content_type}' tidak diizinkan"
    if file_size > MAX_FILE_SIZE:
        return f"Ukuran file melebihi batas maksimum {MAX_FILE_SIZE // (1024*1024)}MB"
    return None


def generate_stored_filename(original_filename: str) -> str:
    ext = os.path.splitext(original_filename)[1]
    return f"{uuid.uuid4().hex}{ext}"


def get_ticket_upload_dir(ticket_id: int) -> str:
    path = os.path.join(UPLOAD_ROOT, str(ticket_id))
    os.makedirs(path, exist_ok=True)
    return path