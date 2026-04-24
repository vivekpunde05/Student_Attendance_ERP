"""
PDF Generator for Attendance Reports using ReportLab.
"""

import html
import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT


def _safe(text):
    """Escape text for ReportLab Paragraph XML parsing."""
    return html.escape(str(text))


def generate_attendance_pdf(data, teacher_name, subject, output_path):
    """
    Generate a professional attendance report PDF.

    Args:
        data: dict from overall_attendance_summary() — keyed by student_id
        teacher_name: str
        subject: str
        output_path: full file path for the PDF
    """
    doc = SimpleDocTemplate(
        output_path,
        pagesize=landscape(A4),
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=2 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=22,
        alignment=TA_CENTER,
        spaceAfter=14,
        textColor=colors.HexColor("#1e293b"),
    )
    subtitle_style = ParagraphStyle(
        "CustomSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        alignment=TA_CENTER,
        spaceAfter=6,
        textColor=colors.HexColor("#475569"),
    )
    header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.whitesmoke,
        fontName="Helvetica-Bold",
    )
    cell_style = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
    )
    cell_left_style = ParagraphStyle(
        "TableCellLeft",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_LEFT,
    )
    red_cell_style = ParagraphStyle(
        "RedCell",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#dc2626"),
        fontName="Helvetica-Bold",
    )
    red_cell_left_style = ParagraphStyle(
        "RedCellLeft",
        parent=styles["Normal"],
        fontSize=9,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#dc2626"),
        fontName="Helvetica-Bold",
    )
    summary_style = ParagraphStyle(
        "SummaryStyle",
        parent=styles["Normal"],
        fontSize=11,
        alignment=TA_LEFT,
        spaceAfter=6,
        textColor=colors.HexColor("#1e293b"),
        fontName="Helvetica-Bold",
    )

    story = []

    # Title
    story.append(Paragraph("<b>ATTENDANCE REPORT</b>", title_style))
    story.append(Spacer(1, 4))

    # Meta info
    report_date = datetime.now().strftime("%d %B %Y")
    story.append(Paragraph(f"<b>Teacher:</b> {_safe(teacher_name)} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Subject:</b> {_safe(subject)}", subtitle_style))
    story.append(Paragraph(f"<b>Date:</b> {_safe(report_date)}", subtitle_style))
    story.append(Spacer(1, 12))

    # Build table data
    table_data = []
    # Header row
    headers = [
        Paragraph("<b>Sr. No</b>", header_style),
        Paragraph("<b>PRN</b>", header_style),
        Paragraph("<b>Student Name</b>", header_style),
        Paragraph("<b>Theory</b><br/>(Present/Total)", header_style),
        Paragraph("<b>Tutorial</b><br/>(Present/Total)", header_style),
        Paragraph("<b>Practical</b><br/>(Present/Total)", header_style),
        Paragraph("<b>Total</b><br/>(Present/Total)", header_style),
        Paragraph("<b>Percentage</b>", header_style),
    ]
    table_data.append(headers)

    # Sort by serial_no
    sorted_students = sorted(data.values(), key=lambda x: x.get("serial_no", 0))

    total_students = len(sorted_students)
    total_percentage_sum = 0.0
    low_attendance_count = 0

    for idx, student in enumerate(sorted_students, start=1):
        theory = student.get("theory", {"attended": 0, "total": 0})
        tutorial = student.get("tutorial", {"attended": 0, "total": 0})
        practical = student.get("practical", {"attended": 0, "total": 0})
        overall = student.get("overall", {"attended": 0, "total": 0, "percentage": 0})

        pct = float(overall.get("percentage", 0))
        total_percentage_sum += pct
        if pct < 50:
            low_attendance_count += 1

        is_low = pct < 50

        sr_cell = Paragraph(_safe(idx), red_cell_style if is_low else cell_style)
        prn_cell = Paragraph(_safe(student.get("prn", "")), red_cell_style if is_low else cell_style)
        name_cell = Paragraph(_safe(student.get("name", "")), red_cell_left_style if is_low else cell_left_style)
        theory_cell = Paragraph(
            _safe(f"{theory.get('attended', 0)}/{theory.get('total', 0)}"),
            red_cell_style if is_low else cell_style,
        )
        tutorial_cell = Paragraph(
            _safe(f"{tutorial.get('attended', 0)}/{tutorial.get('total', 0)}"),
            red_cell_style if is_low else cell_style,
        )
        practical_cell = Paragraph(
            _safe(f"{practical.get('attended', 0)}/{practical.get('total', 0)}"),
            red_cell_style if is_low else cell_style,
        )
        total_cell = Paragraph(
            _safe(f"{overall.get('attended', 0)}/{overall.get('total', 0)}"),
            red_cell_style if is_low else cell_style,
        )
        pct_cell = Paragraph(
            _safe(f"{pct}%"),
            red_cell_style if is_low else cell_style,
        )

        table_data.append([
            sr_cell, prn_cell, name_cell, theory_cell,
            tutorial_cell, practical_cell, total_cell, pct_cell,
        ])

    # Create table
    col_widths = [1.2 * cm, 2.8 * cm, 4.5 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.2 * cm, 2.0 * cm]
    table = Table(table_data, colWidths=col_widths, repeatRows=1)

    # Table style
    style_commands = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("ALIGN", (2, 1), (2, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
    ]
    table.setStyle(TableStyle(style_commands))

    story.append(table)
    story.append(Spacer(1, 20))

    # Summary section
    avg_pct = round(total_percentage_sum / total_students, 2) if total_students > 0 else 0
    story.append(Paragraph("<b>Overall Summary</b>", summary_style))
    story.append(Spacer(1, 6))

    summary_data = [
        [Paragraph("<b>Total Students</b>", cell_style), Paragraph(_safe(total_students), cell_style)],
        [Paragraph("<b>Average Attendance</b>", cell_style), Paragraph(_safe(f"{avg_pct}%"), cell_style)],
        [Paragraph("<b>Students with Low Attendance (<50%)</b>", red_cell_style), Paragraph(_safe(low_attendance_count), red_cell_style)],
    ]
    summary_table = Table(summary_data, colWidths=[6 * cm, 3 * cm])
    summary_table.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("BOX", (0, 0), (-1, -1), 1, colors.black),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#fee2e2")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_table)

    # Footer note
    story.append(Spacer(1, 20))
    footer_style = ParagraphStyle(
        "Footer",
        parent=styles["Normal"],
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#94a3b8"),
    )
    story.append(Paragraph("This is a computer-generated attendance report.", footer_style))

    doc.build(story)
    return output_path

