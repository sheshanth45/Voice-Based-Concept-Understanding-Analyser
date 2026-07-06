"""
PDF report generation using ReportLab.

Produces a single-page (or multi-page, if content is long) evaluation report
containing the topic, transcript, scores, fluency stats, AI feedback, and an
embedded waveform image.
"""
from datetime import datetime
from pathlib import Path
from typing import Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
)

import config


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="VBCUATitle", fontSize=20, leading=24,
                               textColor=colors.HexColor("#1E3A8A"), spaceAfter=6))
    styles.add(ParagraphStyle(name="VBCUASubtitle", fontSize=11, leading=14,
                               textColor=colors.HexColor("#4B5563"), spaceAfter=14))
    styles.add(ParagraphStyle(name="SectionHeader", fontSize=13, leading=16,
                               textColor=colors.HexColor("#1E3A8A"), spaceBefore=14, spaceAfter=6))
    styles.add(ParagraphStyle(name="BodyTextVBCUA", fontSize=10.5, leading=15))
    return styles


def _score_table(semantic_score, fluency_score, overall_score, grade):
    data = [
        ["Metric", "Score"],
        ["Semantic Understanding", f"{semantic_score} / 100"],
        ["Speaking Fluency", f"{fluency_score} / 100"],
        ["Overall Score", f"{overall_score} / 100"],
        ["Grade", grade],
    ]
    table = Table(data, colWidths=[8 * cm, 6 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#EFF6FF")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -2), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def generate_report(
    topic: str,
    transcript: str,
    semantic_score: float,
    fluency_score: float,
    overall_score: float,
    grade: str,
    feedback: str,
    fluency_stats: dict,
    waveform_image_path: Optional[str] = None,
    output_path: Optional[str] = None,
) -> str:
    """
    Build the PDF evaluation report and return the path it was saved to.

    fluency_stats is expected to have keys: duration_seconds, words_per_minute,
    filler_count, pauses (with count/long_pause_count/total_pause_duration).
    """
    styles = _styles()

    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c if c.isalnum() else "_" for c in topic)[:40]
        output_path = str(config.REPORTS_DIR / f"VBCUA_Report_{safe_topic}_{timestamp}.pdf")

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
    )

    story = []
    story.append(Paragraph("VBCUA Evaluation Report", styles["VBCUATitle"]))
    story.append(Paragraph(
        f"Voice-Based Concept Understanding Analyser &middot; Generated on "
        f"{datetime.now().strftime('%d %b %Y, %H:%M')}",
        styles["VBCUASubtitle"],
    ))

    story.append(Paragraph(f"<b>Topic:</b> {topic}", styles["BodyTextVBCUA"]))
    story.append(Spacer(1, 10))

    story.append(Paragraph("Scores", styles["SectionHeader"]))
    story.append(_score_table(semantic_score, fluency_score, overall_score, grade))

    story.append(Paragraph("Fluency Details", styles["SectionHeader"]))
    pauses = fluency_stats.get("pauses", {})
    fluency_details = (
        f"Duration: {fluency_stats.get('duration_seconds', 'N/A')}s &nbsp;|&nbsp; "
        f"Speaking rate: {fluency_stats.get('words_per_minute', 'N/A')} wpm &nbsp;|&nbsp; "
        f"Filler words: {fluency_stats.get('filler_count', 'N/A')} &nbsp;|&nbsp; "
        f"Pauses: {pauses.get('count', 'N/A')} "
        f"(long pauses: {pauses.get('long_pause_count', 'N/A')})"
    )
    story.append(Paragraph(fluency_details, styles["BodyTextVBCUA"]))

    if waveform_image_path and Path(waveform_image_path).exists():
        story.append(Spacer(1, 10))
        story.append(Paragraph("Waveform", styles["SectionHeader"]))
        story.append(Image(waveform_image_path, width=16 * cm, height=4.4 * cm))

    story.append(Paragraph("Transcript", styles["SectionHeader"]))
    story.append(Paragraph(transcript.replace("\n", "<br/>") or "(empty)", styles["BodyTextVBCUA"]))

    story.append(Paragraph("AI Feedback", styles["SectionHeader"]))
    story.append(Paragraph(feedback.replace("\n", "<br/>") or "(no feedback available)", styles["BodyTextVBCUA"]))

    doc.build(story)
    return output_path
