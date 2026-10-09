"""
report.py — PDF Report Generation Utility using ReportLab for VEDA
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_pdf_report(
    input_text: str,
    sentiment: str,
    confidence: float,
    scores: dict,
    model_name: str,
    input_type: str = "text",
    emotion: str = "Neutral",
    insight: str = "",
    user_name: str = "User"
) -> bytes:
    """
    Generate professional VEDA PDF Intelligence Report.
    Returns raw PDF bytes for Streamlit st.download_button.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'VedaTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#4F46E5')
    )
    
    sub_style = ParagraphStyle(
        'VedaSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#64748B')
    )

    head_style = ParagraphStyle(
        'VedaHead',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=12,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'VedaBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=15,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # Header section
    story.append(Paragraph("VEDA — Voice, Emotion & Data Analytics", title_style))
    story.append(Paragraph("Enterprise AI Sentiment & Emotion Intelligence Report", sub_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#4F46E5'), spaceAfter=15))

    # Metadata Table
    meta_data = [
        [
            Paragraph(f"<b>Generated For:</b> {user_name}", body_style),
            Paragraph(f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style)
        ],
        [
            Paragraph(f"<b>Input Type:</b> {input_type.upper()}", body_style),
            Paragraph(f"<b>Transformer Model:</b> {model_name}", body_style)
        ]
    ]
    t_meta = Table(meta_data, colWidths=[260, 260])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 15))

    # Input Content Section
    input_label = "Audio Speech Transcript" if input_type.lower() == "voice" else "Input Text Corpus"
    story.append(Paragraph(f"📄 {input_label}", head_style))
    story.append(Paragraph(f'"{input_text}"', body_style))
    story.append(Spacer(1, 15))

    # Sentiment & Emotion Summary Table
    story.append(Paragraph("🎯 Classification Results & Emotion Intelligence", head_style))
    
    sent_color = colors.HexColor('#10B981') if sentiment == 'POSITIVE' else colors.HexColor('#EF4444') if sentiment == 'NEGATIVE' else colors.HexColor('#64748B')
    
    res_data = [
        [
            Paragraph("<b>Predicted Sentiment</b>", body_style),
            Paragraph(f"<font color='{sent_color.hexval()}'><b>{sentiment}</b></font>", body_style),
            Paragraph(f"<b>Confidence:</b> {confidence:.2f}%", body_style)
        ],
        [
            Paragraph("<b>Granular Emotion</b>", body_style),
            Paragraph(f"<b>{emotion}</b>", body_style),
            Paragraph("<b>Engine:</b> VEDA Neural Pipeline", body_style)
        ]
    ]
    t_res = Table(res_data, colWidths=[170, 170, 180])
    t_res.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#EEF2FF')),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#C7D2FE')),
    ]))
    story.append(t_res)
    story.append(Spacer(1, 15))

    # Probability Score Breakdown
    story.append(Paragraph("📊 Class Probabilities Breakdown", head_style))
    prob_data = [
        ["Class", "Probability (%)"],
        ["Positive", f"{scores.get('POSITIVE', 0)*100:.2f}%"],
        ["Neutral", f"{scores.get('NEUTRAL', 0)*100:.2f}%"],
        ["Negative", f"{scores.get('NEGATIVE', 0)*100:.2f}%"]
    ]
    t_prob = Table(prob_data, colWidths=[260, 260])
    t_prob.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4F46E5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
    ]))
    story.append(t_prob)
    story.append(Spacer(1, 15))

    # AI Insight Section
    if insight:
        story.append(Paragraph("💡 VEDA AI Insight", head_style))
        story.append(Paragraph(f"<i>{insight}</i>", body_style))
        story.append(Spacer(1, 15))

    # Footer
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceBefore=20, spaceAfter=10))
    story.append(Paragraph("Report generated automatically by VEDA Intelligence Engine • Confidential", sub_style))

    doc.build(story)
    pdf_data = buffer.getvalue()
    buffer.close()
    return pdf_data
