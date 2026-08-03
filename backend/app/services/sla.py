from datetime import datetime, timezone
def calculate_sla(ticket):
    if ticket.due_date is None:
        return {
            "sla_status": "NO_DUE_DATE",
            "remaining_hours": None,
        }

    now = datetime.now(timezone.utc)

    remaining = (
        ticket.due_date - now
    ).total_seconds() / 3600

    return {
        "sla_status": "OVERDUE" if remaining < 0 else "ON_TIME",
        "remaining_hours": round(remaining, 2),
    }