from io import BytesIO
from openpyxl import Workbook
from app.models.ticket import Ticket
def export_ticket_excel(tickets):
    wb = Workbook()
    ws = wb.active
    ws.title = "Tickets"

    ws.append([
        "Ticket Number",
        "Title",
        "Type",
        "Priority",
        "Status",
        "Reporter",
        "PIC",
        "Created At",
    ])
    for ticket in tickets:
        ws.append([
            ticket.ticket_number,
            ticket.title,
            ticket.type.value,
            ticket.priority.value,
            ticket.status.value,
            ticket.reporter.name if ticket.reporter else "-",
            ticket.pic.name if ticket.pic else "-",
            str(ticket.created_at),
        ])
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output