import json
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle, PageBreak)


def load_bombas():
    data_path = Path(__file__).resolve().parent.parent / "data" / "bombas_especificaciones.json"
    with open(data_path, encoding="utf-8") as fp:
        return json.load(fp)


def build_cover(story, styles):
    story.append(Spacer(1, 1 * inch))
    story.append(Paragraph("SiBIC - Simulador de Bombas de Infusión Continua", styles["CoverTitle"]))
    story.append(Spacer(1, 0.25 * inch))
    story.append(Paragraph("Guía Técnica Educativa de Operación y Procedimientos", styles["CoverSubtitle"]))
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph(f"Versión 1.0 · {date.today().strftime('%d de %B de %Y')}", styles["NormalCenter"]))
    story.append(Spacer(1, 0.75 * inch))
    story.append(Paragraph("SiBIC combina educación clínica y simulación práctica para acelerar la capacitación en UCI.", styles["NormalCenter"]))
    story.append(Spacer(1, 1.25 * inch))
    story.append(Paragraph("© 2025 SiBIC | Simulador de Bombas de Infusión Continua", styles["SmallCenter"]))
    story.append(PageBreak())


def add_bomb_section(story, styles, bomba):
    story.append(Paragraph(bomba["name"], styles["Heading2"]))
    story.append(Paragraph(f"Fabricante: {bomba['manufacturer']}", styles["Normal"],))
    story.append(Spacer(1, 0.1 * inch))

    specs_data = [
        ["Dimensiones", bomba["specs"]["dimensions"]],
        ["Peso", bomba["specs"]["weight"]],
        ["Batería", bomba["specs"]["battery_type"]],
        ["Pantalla", bomba["specs"]["display"]],
    ]
    specs_table = Table(specs_data, colWidths=[2.5 * inch, 3.5 * inch])
    specs_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003f87")),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.gray),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (0, -1), "LEFT"),
    ]))
    story.append(Paragraph("Especificaciones técnicas", styles["Heading3"]))
    story.append(specs_table)
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Vista frontal", styles["NormalBold"]))
    front_buttons = " · ".join(btn["name"] for btn in bomba["buttons"])
    story.append(Paragraph(bomba["views"]["frontal"]["description"], styles["Normal"]))
    story.append(Paragraph(f"Botones clave: {front_buttons}", styles["CustomItalic"]))
    story.append(Spacer(1, 0.1 * inch))

    story.append(Paragraph("Vista trasera", styles["NormalBold"]))
    story.append(Paragraph(bomba["views"]["trasera"]["description"], styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    button_rows = [["Nombre", "Ubicación", "Función"]] + [
        [btn["name"], btn["location"], btn["function"]]
        for btn in bomba["buttons"]
    ]
    button_table = Table(button_rows, colWidths=[2.5 * inch, 2 * inch, 3 * inch])
    button_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0066cc")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.gray),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    story.append(Paragraph("Tabla de botones", styles["Heading3"]))
    story.append(button_table)
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Procedimientos", styles["Heading3"]))
    for op in bomba["operations"]:
        story.append(Paragraph(op["name"], styles["NormalBold"]))
        steps = "\n".join(f"{idx}. {step}" for idx, step in enumerate(op["steps"], start=1))
        story.append(Paragraph(steps, styles["Normal"]))
        story.append(Paragraph(f"Guía de video: {op['video_url']}", styles["CustomItalicSmall"]))
        story.append(Spacer(1, 0.1 * inch))

    story.append(PageBreak())


def build_comparison_table(story, bombas, styles):
    story.append(Paragraph("Tabla comparativa", styles["Heading1"]))
    headers = ["Característica"] + [bomba["name"] for bomba in bombas]
    rows = [headers]

    def present_availability(bomba, op_key):
        item = next((op for op in bomba["operations"] if op_key in op["name"].lower()), None)
        if not item:
            return "-"
        available = item.get("available")
        if available is False:
            return "-"
        return "✓"

    features = [
        ("Pantalla", lambda b: b["specs"]["display"]),
        ("Goteo nuevo", lambda b: "✓"),
        ("Paralelo", lambda b: present_availability(b, "paralelo")),
        ("Bolo", lambda b: present_availability(b, "bolo")),
        ("Drug Library", lambda b: "-"),
        ("Peso", lambda b: b["specs"]["weight"]),
        ("Batería", lambda b: b["specs"]["battery_type"]),
        ("Apilable", lambda b: "-"),
    ]

    for feature, extractor in features:
        row = [feature] + [extractor(bomba) for bomba in bombas]
        rows.append(row)

    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0b4f6c")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.gray),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ]))
    story.append(table)
    story.append(PageBreak())


def build_appendix(story, styles, bombas):
    story.append(Paragraph("Apéndice", styles["Heading1"]))
    story.append(Paragraph("Glosario básico", styles["Heading3"]))
    glossary = [
        "Bomba de infusión", "Flujo", "Modo bolo", "Alarmas críticas",
        "Drug library", "Cargador", "Perfil de terapia", "Puertos dedicados",
        "Batery low", "Configuración de paralelo", "Lockout", "Validación de paciente",
        "Volumen total", "Rate", "Auto-completion"
    ]
    for term in glossary:
        story.append(Paragraph(f"• {term}", styles["Normal"]))
    story.append(Spacer(1, 0.2 * inch))

    story.append(Paragraph("Referencias de videos educativos", styles["Heading3"]))
    unique_videos = []
    for bomba in bombas:
        for op in bomba["operations"]:
            url = op.get("video_url")
            if url and url not in unique_videos:
                unique_videos.append(url)
    for idx, video in enumerate(unique_videos, start=1):
        story.append(Paragraph(f"{idx}. {video}", styles["Normal"]))


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="CoverTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=24,
        textColor=colors.HexColor("#0b3d91"),
    ))
    styles.add(ParagraphStyle(
        name="CoverSubtitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=16,
        textColor=colors.HexColor("#1c75bc"),
    ))
    styles.add(ParagraphStyle(
        name="NormalCenter",
        parent=styles["Normal"],
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="NormalBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold"
    ))
    styles.add(ParagraphStyle(
        name="CustomItalic",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique"
    ))
    styles.add(ParagraphStyle(
        name="CustomItalicSmall",
        parent=styles["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=9,
    ))
    styles.add(ParagraphStyle(
        name="SmallCenter",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.gray,
    ))
    return styles


def build_pdf():
    bombas = load_bombas()
    doc_path = Path(__file__).resolve().parent.parent / "docs" / "SiBIC_BOMBAS_REFERENCIA.pdf"
    doc = SimpleDocTemplate(
        str(doc_path),
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )
    styles = build_styles()
    story = []

    build_cover(story, styles)
    for bomba in bombas:
        add_bomb_section(story, styles, bomba)
    build_comparison_table(story, bombas, styles)
    build_appendix(story, styles, bombas)

    doc.build(story)
    print(f"✅ PDF generado en: {doc_path}")


if __name__ == "__main__":
    build_pdf()
