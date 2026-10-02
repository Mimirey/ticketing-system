import time
from app.db.database import SessionLocal
from app.services.ticket_reminder import check_ticket_reminders

CHECK_INTERVAL = 300  
def run():
    print("Ticket reminder worker started")
    while True:
        db = SessionLocal()
        try:
            print("Checking ticket reminders...")
            check_ticket_reminders(db)
        except Exception as e:
            print(f"Ticket reminder error: {e}")
        finally:
            db.close()
        time.sleep(CHECK_INTERVAL)
if __name__ == "__main__":
    run()