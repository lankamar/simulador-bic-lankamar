import json
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle, PageBreak)


def load_bombas():
    data_path = Path(__file__).resolve().parent.parent / "data" / "bombas_especificaciones.json"
    with open(data_path, encoding="utf-8") as fp:
        payload = json.load(fp)
    return payload.get("bombas", [])


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
    contenido_es = bomba.get("contenido", {}).get("es", {})
    titulo = contenido_es.get("titulo_pdf") or contenido_es.get("nombre_comercial") or bomba.get("modelo", "Sin nombre")
    story.append(Paragraph(titulo, styles["Heading2"]))
    fabricante = bomba.get("fabricante_id", "")
    modelo = bomba.get("modelo", "").strip()
    tipo = bomba.get("tipo", "-")
    story.append(Paragraph(f"Fabricante: {fabricante} · Modelo: {modelo} · Tipo: {tipo}", styles["Normal"]))
    story.append(Spacer(1, 0.1 * inch))

    parametros = bomba.get("parametros_tecnicos", {})
    rango = parametros.get("rango_infusion_ml_h")
    rango_text = f"{rango[0]} - {rango[1]} ml/h" if isinstance(rango, list) and len(rango) == 2 else "-"
    precision = parametros.get("precision_porcentaje", "-")
    volumen_max = parametros.get("volumen_max_ml", "-")
    presion_max = parametros.get("presion_max_psi", "-")
    tipo_display = parametros.get("tipo_display", "-")
    alimentacion = ", ".join(parametros.get("alimentacion", [])) or "-"

    tech_rows = [
        ["Rango de infusión", rango_text],
        ["Precisión", f"{precision} %" if isinstance(precision, (int, float)) else precision],
        ["Volumen máximo", f"{volumen_max} ml" if isinstance(volumen_max, (int, float)) else volumen_max],
        ["Presión máxima", f"{presion_max} psi" if isinstance(presion_max, (int, float)) else presion_max],
        ["Pantalla", tipo_display],
        ["Alimentación", alimentacion],
    ]
    tech_table = Table(tech_rows, colWidths=[2.5 * inch, 4 * inch])
    tech_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
        ("GRID", (0, 0), (-1, -1), 0.3, colors.gray),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(Paragraph("Parámetros técnicos", styles["Heading3"]))
    story.append(tech_table)
    story.append(Spacer(1, 0.2 * inch))

    descripcion = contenido_es.get("descripcion_clinica")
    if descripcion:
        story.append(Paragraph("Descripción clínica", styles["NormalBold"]))
        story.append(Paragraph(descripcion, styles["Normal"]))
        story.append(Spacer(1, 0.1 * inch))

    observaciones = contenido_es.get("observaciones", [])
    if observaciones:
        story.append(Paragraph("Observaciones", styles["NormalBold"]))
        for obs in observaciones:
            story.append(Paragraph(f"• {obs}", styles["Normal"]))
        story.append(Spacer(1, 0.1 * inch))

    diagrama = bomba.get("diagramas", {}).get("ascii")
    if diagrama:
        if isinstance(diagrama, list):
            diagrama_text = "\n".join(diagrama)
        else:
            diagrama_text = diagrama
        story.append(Paragraph("Diagrama ASCII", styles["NormalBold"]))
        story.append(Paragraph(diagrama_text, styles["Monospace"]))
        story.append(Spacer(1, 0.2 * inch))

    story.append(PageBreak())


def build_comparison_table(story, bombas, styles):
    story.append(Paragraph("Tabla comparativa", styles["Heading1"]))
    headers = ["Nombre", "Tipo", "Rango", "Precisión"]
    rows = [headers]

    def format_range_value(rango):
        if isinstance(rango, list) and len(rango) == 2:
            return f"{rango[0]} - {rango[1]}"
        return "-"

    for bomba in bombas:
        contenido_es = bomba.get("contenido", {}).get("es", {})
        nombre = contenido_es.get("nombre_comercial") or contenido_es.get("titulo_pdf") or bomba.get("modelo", "-")
        tipo = bomba.get("tipo", "-")
        parametros = bomba.get("parametros_tecnicos", {})
        rango_text = format_range_value(parametros.get("rango_infusion_ml_h"))
        precision = parametros.get("precision_porcentaje")
        precision_text = f"{precision} %" if isinstance(precision, (int, float)) else "-"
        rows.append([nombre, tipo, rango_text, precision_text])

    table = Table(rows, repeatRows=1, colWidths=[2.6 * inch, 1.4 * inch, 2.2 * inch, 1.4 * inch])
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

    story.append(Paragraph("Referencias técnicas", styles["Heading3"]))
    unique_urls = []
    for bomba in bombas:
        referencias = bomba.get("referencias", {})
        for key in ("manuales", "fichas"):
            for ref in referencias.get(key, []):
                url = ref.get("url")
                if url and url not in unique_urls:
                    unique_urls.append(url)
    if unique_urls:
        for idx, url in enumerate(unique_urls, start=1):
            story.append(Paragraph(f"{idx}. {url}", styles["Normal"]))
    else:
        story.append(Paragraph("No se registraron referencias adicionales.", styles["Normal"]))


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
    styles.add(ParagraphStyle(
        name="Monospace",
        parent=styles["Normal"],
        fontName="Courier",
        leading=12,
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
