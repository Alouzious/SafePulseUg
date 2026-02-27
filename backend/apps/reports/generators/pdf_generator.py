import io
from datetime               import datetime
from reportlab.lib          import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles   import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units    import cm
from reportlab.platypus     import (
    SimpleDocTemplate, Paragraph, Spacer,
    Table, TableStyle, HRFlowable, PageBreak
)
from reportlab.lib.enums    import TA_CENTER, TA_LEFT, TA_RIGHT


# ─────────────────────────────────────────────────────────────
# COLORS — SafePulse UG Brand
# ─────────────────────────────────────────────────────────────
DARK_BLUE   = colors.HexColor('#1a3a5c')
MEDIUM_BLUE = colors.HexColor('#2563eb')
LIGHT_BLUE  = colors.HexColor('#dbeafe')
RED         = colors.HexColor('#dc2626')
GREY        = colors.HexColor('#6b7280')
LIGHT_GREY  = colors.HexColor('#f3f4f6')
WHITE       = colors.white
BLACK       = colors.black


# ─────────────────────────────────────────────────────────────
# STYLES
# ─────────────────────────────────────────────────────────────
def get_styles():
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name        ='ReportTitle',
        fontSize    = 22,
        textColor   = DARK_BLUE,
        alignment   = TA_CENTER,
        spaceAfter  = 6,
        fontName    = 'Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        name        ='ReportSubtitle',
        fontSize    = 11,
        textColor   = GREY,
        alignment   = TA_CENTER,
        spaceAfter  = 4,
    ))
    styles.add(ParagraphStyle(
        name        ='SectionHeader',
        fontSize    = 13,
        textColor   = WHITE,
        alignment   = TA_LEFT,
        fontName    = 'Helvetica-Bold',
        spaceAfter  = 6,
        spaceBefore = 12,
    ))
    styles.add(ParagraphStyle(
        name        ='FieldLabel',
        fontSize    = 9,
        textColor   = GREY,
        fontName    = 'Helvetica-Bold',
    ))
    styles.add(ParagraphStyle(
        name        ='FieldValue',
        fontSize    = 10,
        textColor   = BLACK,
    ))
    styles.add(ParagraphStyle(
        name        ='BodyText2',
        fontSize    = 9,
        textColor   = BLACK,
        spaceAfter  = 4,
    ))
    styles.add(ParagraphStyle(
        name        ='AIText',
        fontSize    = 10,
        textColor   = BLACK,
        spaceAfter  = 6,
        leading     = 16,
    ))

    return styles


# ─────────────────────────────────────────────────────────────
# HELPER — Section Header Block
# ─────────────────────────────────────────────────────────────
def section_header(text, styles):
    data  = [[Paragraph(f"  {text}", styles['SectionHeader'])]]
    table = Table(data, colWidths=[19 * cm])
    table.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (-1, -1), DARK_BLUE),
        ('ROWPADDING',  (0, 0), (-1, -1), 6),
    ]))
    return table


# ─────────────────────────────────────────────────────────────
# GENERATE CRIME LIST PDF
# ─────────────────────────────────────────────────────────────
def generate_crime_list_pdf(reports, filters=None):
    """
    Generate a PDF report for a list of crime reports.
    Returns a BytesIO buffer.
    """
    buffer  = io.BytesIO()
    doc     = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )
    styles  = get_styles()
    story   = []

    # ── Header ────────────────────────────────────────────────
    story.append(Paragraph("🛡 SafePulse UG", styles['ReportTitle']))
    story.append(Paragraph("Uganda Police Force — Crime Analysis System", styles['ReportSubtitle']))
    story.append(Paragraph("CRIME REPORTS", styles['ReportSubtitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=DARK_BLUE))
    story.append(Spacer(1, 0.3*cm))

    # ── Report metadata ──────────────────────────────────────
    meta_data = [
        ['Generated On:', datetime.now().strftime('%Y-%m-%d %H:%M')],
        ['Total Records:', str(len(reports))],
        ['Filters Applied:', str(filters) if filters else 'None'],
    ]
    meta_table = Table(meta_data, colWidths=[4*cm, 15*cm])
    meta_table.setStyle(TableStyle([
        ('FONTNAME',    (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 9),
        ('TEXTCOLOR',   (0, 0), (0, -1), GREY),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Section header ───────────────────────────────────────
    story.append(section_header("CRIME REPORTS LIST", styles))
    story.append(Spacer(1, 0.3*cm))

    if not reports:
        story.append(Paragraph("No crime reports found.", styles['BodyText2']))
    else:
        # ── Table headers ─────────────────────────────────────
        table_data = [[
            Paragraph('Case No.',   styles['FieldLabel']),
            Paragraph('Title',      styles['FieldLabel']),
            Paragraph('Category',   styles['FieldLabel']),
            Paragraph('Severity',   styles['FieldLabel']),
            Paragraph('Status',     styles['FieldLabel']),
            Paragraph('District',   styles['FieldLabel']),
            Paragraph('Date',       styles['FieldLabel']),
        ]]

        # ── Table rows ────────────────────────────────────────
        for i, r in enumerate(reports):
            bg_color = LIGHT_GREY if i % 2 == 0 else WHITE

            # Color-code severity
            severity_color = {
                'low':      colors.green,
                'medium':   colors.orange,
                'high':     RED,
                'critical': colors.purple,
            }.get(r.severity, BLACK)

            table_data.append([
                Paragraph(r.case_number,                        styles['BodyText2']),
                Paragraph(r.title[:40],                         styles['BodyText2']),
                Paragraph(r.category.replace('_', ' ').title(), styles['BodyText2']),
                Paragraph(
                    f'<font color="{severity_color.hexval()}">'
                    f'{r.severity.upper()}</font>',
                    styles['BodyText2']
                ),
                Paragraph(r.status.replace('_', ' ').title(),   styles['BodyText2']),
                Paragraph(r.district,                           styles['BodyText2']),
                Paragraph(
                    r.date_occurred.strftime('%Y-%m-%d'),
                    styles['BodyText2']
                ),
            ])

        col_widths = [3.2*cm, 5*cm, 2.5*cm, 2*cm, 2.8*cm, 2.5*cm, 2*cm]
        table = Table(table_data, colWidths=col_widths, repeatRows=1)
        table.setStyle(TableStyle([
            ('BACKGROUND',      (0, 0), (-1, 0),  DARK_BLUE),
            ('TEXTCOLOR',       (0, 0), (-1, 0),  WHITE),
            ('FONTNAME',        (0, 0), (-1, 0),  'Helvetica-Bold'),
            ('FONTSIZE',        (0, 0), (-1, -1), 8),
            ('ROWBACKGROUNDS',  (0, 1), (-1, -1), [LIGHT_GREY, WHITE]),
            ('GRID',            (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWPADDING',      (0, 0), (-1, -1), 5),
            ('VALIGN',          (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(table)

    # ── Footer ───────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=GREY))
    story.append(Paragraph(
        "CONFIDENTIAL — Uganda Police Force | SafePulse UG Crime Analysis System",
        styles['ReportSubtitle']
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ─────────────────────────────────────────────────────────────
# GENERATE SINGLE CRIME REPORT PDF
# ─────────────────────────────────────────────────────────────
def generate_single_crime_pdf(report):
    """
    Generate a detailed PDF for a single crime report.
    Returns a BytesIO buffer.
    """
    buffer  = io.BytesIO()
    doc     = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )
    styles  = get_styles()
    story   = []

    # ── Header ───────────────────────────────────────────────
    story.append(Paragraph("🛡 SafePulse UG", styles['ReportTitle']))
    story.append(Paragraph("Uganda Police Force — Crime Analysis System", styles['ReportSubtitle']))
    story.append(Paragraph(f"CRIME REPORT — {report.case_number}", styles['ReportSubtitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=DARK_BLUE))
    story.append(Spacer(1, 0.5*cm))

    # ── Case summary box ─────────────────────────────────────
    severity_color = {
        'low':      colors.green,
        'medium':   colors.orange,
        'high':     RED,
        'critical': colors.purple,
    }.get(report.severity, BLACK)

    summary_data = [
        ['Case Number',  report.case_number,
         'Severity',
         Paragraph(
             f'<font color="{severity_color.hexval()}">'
             f'{report.severity.upper()}</font>',
             styles['FieldValue']
         )],
        ['Category',     report.category.replace('_', ' ').title(),
         'Status',       report.status.replace('_', ' ').title()],
        ['District',     report.district,
         'Date Occurred', report.date_occurred.strftime('%Y-%m-%d %H:%M')],
        ['Location',     report.location,
         'Victim Count', str(report.victim_count)],
    ]

    summary_table = Table(summary_data, colWidths=[3.5*cm, 6*cm, 3.5*cm, 6*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (0, -1), LIGHT_BLUE),
        ('BACKGROUND',  (2, 0), (2, -1), LIGHT_BLUE),
        ('FONTNAME',    (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME',    (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 9),
        ('GRID',        (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('ROWPADDING',  (0, 0), (-1, -1), 6),
        ('VALIGN',      (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Description ──────────────────────────────────────────
    story.append(section_header("CRIME DESCRIPTION", styles))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(report.description, styles['BodyText2']))
    story.append(Spacer(1, 0.3*cm))

    if report.weapons_used:
        story.append(Paragraph(f"<b>Weapons Used:</b> {report.weapons_used}", styles['BodyText2']))

    if report.modus_operandi:
        story.append(Paragraph(f"<b>Modus Operandi:</b> {report.modus_operandi}", styles['BodyText2']))

    if report.victim_details:
        story.append(Paragraph(f"<b>Victim Details:</b> {report.victim_details}", styles['BodyText2']))

    if report.evidence_notes:
        story.append(Spacer(1, 0.3*cm))
        story.append(section_header("EVIDENCE NOTES", styles))
        story.append(Spacer(1, 0.2*cm))
        story.append(Paragraph(report.evidence_notes, styles['BodyText2']))

    # ── Suspects ─────────────────────────────────────────────
    suspects = report.suspects.all()
    if suspects.exists():
        story.append(Spacer(1, 0.3*cm))
        story.append(section_header(f"SUSPECTS ({suspects.count()})", styles))
        story.append(Spacer(1, 0.2*cm))

        suspect_data = [[
            Paragraph('Name',           styles['FieldLabel']),
            Paragraph('Age',            styles['FieldLabel']),
            Paragraph('Gender',         styles['FieldLabel']),
            Paragraph('Known to Victim',styles['FieldLabel']),
            Paragraph('Arrested',       styles['FieldLabel']),
            Paragraph('Description',    styles['FieldLabel']),
        ]]

        for s in suspects:
            suspect_data.append([
                Paragraph(s.name or 'Unknown',              styles['BodyText2']),
                Paragraph(str(s.age_estimate or 'N/A'),     styles['BodyText2']),
                Paragraph(s.gender.title(),                 styles['BodyText2']),
                Paragraph('Yes' if s.known_to_victim else 'No', styles['BodyText2']),
                Paragraph('Yes' if s.is_arrested else 'No', styles['BodyText2']),
                Paragraph(s.description[:80] or 'N/A',     styles['BodyText2']),
            ])

        s_table = Table(
            suspect_data,
            colWidths=[3*cm, 1.5*cm, 2*cm, 3*cm, 2*cm, 7.5*cm]
        )
        s_table.setStyle(TableStyle([
            ('BACKGROUND',  (0, 0), (-1, 0), DARK_BLUE),
            ('TEXTCOLOR',   (0, 0), (-1, 0), WHITE),
            ('FONTNAME',    (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE',    (0, 0), (-1, -1), 8),
            ('GRID',        (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT_GREY, WHITE]),
            ('ROWPADDING',  (0, 0), (-1, -1), 5),
        ]))
        story.append(s_table)

    # ── Witnesses ────────────────────────────────────────────
    witnesses = report.witnesses.all()
    if witnesses.exists():
        story.append(Spacer(1, 0.3*cm))
        story.append(section_header(f"WITNESSES ({witnesses.count()})", styles))
        story.append(Spacer(1, 0.2*cm))

        for w in witnesses:
            name = 'Anonymous' if w.is_anonymous else w.name
            story.append(Paragraph(f"<b>{name}</b>", styles['BodyText2']))
            if w.contact:
                story.append(Paragraph(f"Contact: {w.contact}", styles['BodyText2']))
            if w.statement:
                story.append(Paragraph(f"Statement: {w.statement}", styles['BodyText2']))
            story.append(Spacer(1, 0.2*cm))

    # ── AI Analysis (if available) ───────────────────────────
    analysis_results = report.analysis_results.filter(
        status='completed'
    ).order_by('-created_at').first()

    if analysis_results:
        story.append(PageBreak())
        story.append(section_header("AI ANALYSIS RESULTS", styles))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(
            analysis_results.ai_summary,
            styles['AIText']
        ))

    # ── Footer ───────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=GREY))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
        "CONFIDENTIAL — Uganda Police Force | SafePulse UG",
        styles['ReportSubtitle']
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ─────────────────────────────────────────────────────────────
# GENERATE ANALYSIS REPORT PDF
# ─────────────────────────────────────────────────────────────
def generate_analysis_pdf(analysis):
    """
    Generate a PDF for an AI analysis result.
    Returns a BytesIO buffer.
    """
    buffer  = io.BytesIO()
    doc     = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )
    styles  = get_styles()
    story   = []

    # ── Header ───────────────────────────────────────────────
    story.append(Paragraph("🛡 SafePulse UG", styles['ReportTitle']))
    story.append(Paragraph("Uganda Police Force — AI Crime Analysis", styles['ReportSubtitle']))
    story.append(HRFlowable(width="100%", thickness=2, color=DARK_BLUE))
    story.append(Spacer(1, 0.5*cm))

    # ── Metadata ─────────────────────────────────────────────
    case = analysis.crime_report.case_number if analysis.crime_report else 'General Analysis'
    meta_data = [
        ['Analysis ID:',    str(analysis.id)],
        ['Case:',           case],
        ['Requested By:',   analysis.requested_by.full_name if analysis.requested_by else 'Unknown'],
        ['Generated On:',   analysis.completed_at.strftime('%Y-%m-%d %H:%M') if analysis.completed_at else 'N/A'],
    ]
    meta_table = Table(meta_data, colWidths=[4*cm, 15*cm])
    meta_table.setStyle(TableStyle([
        ('FONTNAME',    (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 9),
        ('TEXTCOLOR',   (0, 0), (0, -1), GREY),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.5*cm))

    # ── AI Analysis content ──────────────────────────────────
    story.append(section_header("AI ANALYSIS REPORT", styles))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(analysis.ai_summary, styles['AIText']))

    # ── Footer ───────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=GREY))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} | "
        "CONFIDENTIAL — Uganda Police Force | SafePulse UG",
        styles['ReportSubtitle']
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer