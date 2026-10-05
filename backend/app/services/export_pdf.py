from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


def export_ticket_pdf(tickets):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=4,
    )

    # Style untuk Subtitle / Tanggal Cetak
    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        textColor=colors.HexColor("#64748B"),
        spaceAfter=15,
    )

    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#334155"),
    )

    cell_header_style = ParagraphStyle(
        "TableHeaderCell",
        parent=cell_style,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    story.append(Paragraph("Laporan Data Ticket", title_style))
    story.append(
        Paragraph("Daftar tiket yang terdaftar dalam sistem", subtitle_style)
    )

    data = [
        [
            Paragraph("No Ticket", cell_header_style),
            Paragraph("Title", cell_header_style),
            Paragraph("Priority", cell_header_style),
            Paragraph("Status", cell_header_style),
            Paragraph("Reporter", cell_header_style),
            Paragraph("PIC", cell_header_style),
        ]
    ]

    for t in tickets:
        data.append(
            [
                Paragraph(str(t.ticket_number), cell_style),
                Paragraph(t.title or "-", cell_style),
                Paragraph(
                    t.priority.value if hasattr(t.priority, "value") else str(t.priority),
                    cell_style,
                ),
                Paragraph(
                    t.status.value if hasattr(t.status, "value") else str(t.status),
                    cell_style,
                ),
                Paragraph(
                    t.reporter.name if getattr(t, "reporter", None) else "-",
                    cell_style,
                ),
                Paragraph(
                    t.pic.name if getattr(t, "pic", None) else "-", cell_style
                ),
            ]
        )

    col_widths = [90, 153, 60, 60, 80, 80]

    table = Table(data, colWidths=col_widths, repeatRows=1)

    ts = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),  
        ("ALIGN", (0, 0), (-1, 0), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
    ]

    for i in range(1, len(data)):
        if i % 2 == 0:
            ts.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F8FAFC")))
        else:
            ts.append(("BACKGROUND", (0, i), (-1, i), colors.white))

    table.setStyle(TableStyle(ts))
    story.append(table)

    def add_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#94A3B8"))
        canvas.drawString(
            36, 20, f"Halaman {doc.page} | Sistem Manajemen Ticket"
        )
        canvas.restoreState()

    doc.build(story, onFirstPage=add_footer, onLaterPages=add_footer)

    buffer.seek(0)
    return buffer