from app.db.database import SessionLocal
from app.services.ticket_reminder import check_ticket_reminders

db = SessionLocal()

try:
    check_ticket_reminders(db)
    print("Reminder check selesai")
finally:
    db.close()