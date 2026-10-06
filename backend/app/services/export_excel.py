from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

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
    ws.views.sheetView[0].showGridLines = True

    headers = [
        "Ticket Number",
        "Company",
        "Application",
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
    ]
    ws.append(headers)

    header_fill = PatternFill(
        start_color="1E3A8A", end_color="1E3A8A", fill_type="solid"
    )
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    data_font = Font(name="Calibri", size=10, color="000000")
    zebra_fill = PatternFill(
        start_color="F8FAFC", end_color="F8FAFC", fill_type="solid"
    )

    thin_border = Border(
        left=Side(style="thin", color="E2E8F0"),
        right=Side(style="thin", color="E2E8F0"),
        top=Side(style="thin", color="E2E8F0"),
        bottom=Side(style="thin", color="E2E8F0"),
    )

    for col_num in range(1, len(headers) + 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(
            horizontal="center", vertical="center", wrap_text=True
        )

    ws.row_dimensions[1].height = 28

    for row_idx, ticket in enumerate(tickets, start=2):
        timeline = get_ticket_timeline(db, ticket.id)

        total_resolution_time = calculate_duration(
            timeline["created_at"], timeline["done_at"]
        )

        ticket_type = (
            ticket.type.value
            if hasattr(ticket.type, "value")
            else str(ticket.type)
        )
        ticket_priority = (
            ticket.priority.value
            if hasattr(ticket.priority, "value")
            else str(ticket.priority)
        )
        ticket_status = (
            ticket.status.value
            if hasattr(ticket.status, "value")
            else str(ticket.status)
        )

        row_data = [
            ticket.ticket_number,
            ticket.company.name if ticket.company else "-",
            ticket.application.name if ticket.application else "-",
            ticket.title or "-",
            ticket_type,
            ticket.description or "-",
            ticket_priority,
            ticket_status,
            ticket.reporter.name if ticket.reporter else "-",
            ticket.pic.name if ticket.pic else "-",
            str(timeline["created_at"]) if timeline["created_at"] else "-",
            str(timeline["assigned_at"]) if timeline["assigned_at"] else "-",
            (
                str(timeline["in_progress_at"])
                if timeline["in_progress_at"]
                else "-"
            ),
            str(timeline["qa_at"]) if timeline["qa_at"] else "-",
            str(timeline["done_at"]) if timeline["done_at"] else "-",
            (
                total_resolution_time
                if total_resolution_time is not None
                else "-"
            ),
        ]
        ws.append(row_data)

        ws.row_dimensions[row_idx].height = 20
        is_even = row_idx % 2 == 0

        for col_idx, value in enumerate(row_data, start=1):
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.font = data_font
            cell.border = thin_border

            if is_even:
                cell.fill = zebra_fill

            if col_idx in [1, 5, 7, 8, 11, 12, 13, 14, 15, 16]:
                cell.alignment = Alignment(
                    horizontal="center", vertical="center"
                )
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)

        for cell in col:
            val_str = str(cell.value or "")
            if len(val_str) > max_len:
                max_len = len(val_str)

        ws.column_dimensions[col_letter].width = min(max(max_len + 4, 12), 40)

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output