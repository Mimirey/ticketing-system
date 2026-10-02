from io import BytesIO
from openpyxl import Workbook
from app.models.ticket import Ticket
from app.core.ticket_timeline import get_ticket_timeline

def calculate_duration(start, end):
    if not start or not end:
        return None

    duration = end - start
    return round(duration.total_seconds() / 3600, 2)
def export_ticket_excel(tickets, db):
    wb = Workbook()
    ws = wb.active
    ws.title = "Tickets"

    ws.append([
        "Ticket Number",
        "Company",
        "Application"
        "Title",
        "Type",
        "Description",
        "Priority",
        "Status",
        "Reporter",
        "PIC",
        "Created At",
        "Assigned At",
        "In Progress At",
        "QA At",
        "Done At",
        "Total Resolution Time (Hours)",
    ])
    for ticket in tickets:
        timeline = get_ticket_timeline(db, ticket.id)

        total_resolution_time = calculate_duration(
            timeline["created_at"],
            timeline["done_at"]
        )

        ws.append([
            ticket.ticket_number,
            ticket.company.name if ticket.company else "-",
            ticket.application.name if ticket.application else "-",
            ticket.type.value,
            ticket.title,
            ticket.description,
            ticket.priority.value,
            ticket.status.value,
            ticket.reporter.name if ticket.reporter else "-",
            ticket.pic.name if ticket.pic else "-",
            str(timeline["created_at"]) if timeline["created_at"] else "-",
            str(timeline["assigned_at"]) if timeline["assigned_at"] else "-",
            str(timeline["in_progress_at"]) if timeline["in_progress_at"] else "-",
            str(timeline["qa_at"]) if timeline["qa_at"] else "-",
            str(timeline["done_at"]) if timeline["done_at"] else "-",
            total_resolution_time if total_resolution_time is not None else "-",
        ])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output