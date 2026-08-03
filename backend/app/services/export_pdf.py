from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors


def export_ticket_pdf(tickets):
    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    data = [
        [
            "No",
            "Title",
            "Priority",
            "Status",
            "Reporter",
            "PIC",
        ]
    ]

    for t in tickets:
        data.append([
            t.ticket_number,
            t.title,
            t.priority.value,
            t.status.value,
            t.reporter.name if t.reporter else "-",
            t.pic.name if t.pic else "-",
        ])

    table = Table(data)

    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("BACKGROUND", (0,1), (-1,-1), colors.beige),
        ("BOTTOMPADDING", (0,0), (-1,0), 10),
    ]))

    doc.build([table])

    buffer.seek(0)
    return buffer