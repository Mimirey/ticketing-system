from datetime import datetime

def generate_ticket_number(ticket_id: int) -> str:
    year = datetime.now().year
    return f"TCK-{year}-{ticket_id:03d}"