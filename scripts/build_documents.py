"""Exporta la propuesta de investigación a DOCX y, opcionalmente, PDF."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION_START
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

from build_figures import build_figures


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "docs" / "propuesta_investigacion.md"
DEFAULT_DOCX = ROOT / "output" / "docx" / "propuesta_investigacion.docx"
DEFAULT_PDF_DIR = ROOT / "output" / "pdf"


def set_run_font(run, size: float = 11, bold=None, italic=None, color="000000"):
    run.font.name = "Times New Roman"
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), "Times New Roman")
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), "Times New Roman")
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor.from_string(color)
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic


def configure_styles(doc: Document):
    styles = doc.styles

    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    normal.font.size = Pt(11)
    normal.font.color.rgb = RGBColor(0, 0, 0)
    normal.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.15

    title = styles["Title"]
    title.base_style = normal
    title.font.name = "Times New Roman"
    title._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    title._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    title.font.size = Pt(18)
    title.font.bold = True
    title.font.color.rgb = RGBColor(0, 0, 0)
    title.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_before = Pt(72)
    title.paragraph_format.space_after = Pt(18)
    title_properties = title._element.get_or_add_pPr()
    for border in title_properties.findall(qn("w:pBdr")):
        title_properties.remove(border)

    subtitle = styles.add_style("Academic Subtitle", WD_STYLE_TYPE.PARAGRAPH)
    subtitle.base_style = normal
    subtitle.font.name = "Times New Roman"
    subtitle._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    subtitle._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    subtitle.font.size = Pt(11)
    subtitle.font.italic = False
    subtitle.font.color.rgb = RGBColor(64, 64, 64)
    subtitle.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.paragraph_format.space_after = Pt(4)

    heading_tokens = {
        "Academic H1": (13, True, False, 14, 6, 0),
        "Academic H2": (12, True, False, 12, 5, 1),
        "Academic H3": (11, True, True, 10, 4, 2),
        "Academic H4": (11, False, True, 8, 3, 3),
    }
    for name, (size, bold, italic, before, after, outline_level) in heading_tokens.items():
        style = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        style.base_style = normal
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
        style.font.size = Pt(size)
        style.font.bold = bold
        style.font.italic = italic
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.paragraph_format.space_before = Pt(before)
        style.paragraph_format.space_after = Pt(after)
        style.paragraph_format.keep_with_next = True
        outline = OxmlElement("w:outlineLvl")
        outline.set(qn("w:val"), str(outline_level))
        style._element.get_or_add_pPr().append(outline)

    if "IEEE Reference" not in styles:
        ref_style = styles.add_style("IEEE Reference", WD_STYLE_TYPE.PARAGRAPH)
    else:
        ref_style = styles["IEEE Reference"]
    ref_style.base_style = normal
    ref_style.font.name = "Times New Roman"
    ref_style._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    ref_style._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    ref_style.font.size = Pt(10)
    ref_style.paragraph_format.left_indent = Inches(0.28)
    ref_style.paragraph_format.first_line_indent = Inches(-0.28)
    ref_style.paragraph_format.space_after = Pt(3)
    ref_style.paragraph_format.line_spacing = 1.0

    for list_name in ("List Bullet", "List Number"):
        style = styles[list_name]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
        style.font.size = Pt(11)
        style.paragraph_format.left_indent = Inches(0.5)
        style.paragraph_format.first_line_indent = Inches(-0.25)
        style.paragraph_format.space_after = Pt(4)
        style.paragraph_format.line_spacing = 1.15

    figure_caption = styles.add_style("Figure Caption", WD_STYLE_TYPE.PARAGRAPH)
    figure_caption.base_style = normal
    figure_caption.font.name = "Times New Roman"
    figure_caption._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    figure_caption._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    figure_caption.font.size = Pt(9)
    figure_caption.font.italic = True
    figure_caption.font.color.rgb = RGBColor(64, 64, 64)
    figure_caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    figure_caption.paragraph_format.space_before = Pt(2)
    figure_caption.paragraph_format.space_after = Pt(8)
    figure_caption.paragraph_format.line_spacing = 1.0


def add_page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run()
    set_run_font(run, size=9, color="666666")
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instruction = OxmlElement("w:instrText")
    instruction.set(qn("xml:space"), "preserve")
    instruction.text = " PAGE "
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    value = OxmlElement("w:t")
    value.text = "1"
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instruction, separate, value, end])


def configure_page(doc: Document):
    section = doc.sections[0]
    section.start_type = WD_SECTION_START.NEW_PAGE
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.right_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.header_distance = Inches(0.492)
    section.footer_distance = Inches(0.492)

    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    header.paragraph_format.space_after = Pt(0)
    run = header.add_run("Propuesta de investigación | Ciclo 6")
    set_run_font(run, size=8.5, color="666666")

    footer = section.footer.paragraphs[0]
    add_page_number(footer)


INLINE_PATTERN = re.compile(r"(\*\*.+?\*\*|\*.+?\*)")


def add_inline(paragraph, text: str):
    for part in INLINE_PATTERN.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            run = paragraph.add_run(part[2:-2])
            set_run_font(run, bold=True)
        elif part.startswith("*") and part.endswith("*"):
            run = paragraph.add_run(part[1:-1])
            set_run_font(run, italic=True)
        else:
            run = paragraph.add_run(part)
            set_run_font(run)


def flush_paragraph(doc: Document, buffer: list[str], cover_mode: bool):
    if not buffer:
        return
    text = " ".join(line.strip() for line in buffer).strip()
    buffer.clear()
    if not text:
        return

    style = "IEEE Reference" if re.match(r"^\[\d+\]", text) else "Normal"
    p = doc.add_paragraph(style=style)
    add_inline(p, text)


def split_table_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def is_table_separator(line: str) -> bool:
    cells = split_table_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def set_cell_shading(cell, fill: str):
    properties = cell._tc.get_or_add_tcPr()
    shading = properties.find(qn("w:shd"))
    if shading is None:
        shading = OxmlElement("w:shd")
        properties.append(shading)
    shading.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=100, start=100, bottom=100, end=100):
    properties = cell._tc.get_or_add_tcPr()
    margins = properties.first_child_found_in("w:tcMar")
    if margins is None:
        margins = OxmlElement("w:tcMar")
        properties.append(margins)
    for tag, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        element = margins.find(qn(f"w:{tag}"))
        if element is None:
            element = OxmlElement(f"w:{tag}")
            margins.append(element)
        element.set(qn("w:w"), str(value))
        element.set(qn("w:type"), "dxa")


def set_table_borders(table, color="D9D9D9", size="4"):
    properties = table._tbl.tblPr
    borders = properties.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        properties.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        element = borders.find(qn(f"w:{edge}"))
        if element is None:
            element = OxmlElement(f"w:{edge}")
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def add_markdown_table(doc: Document, headers: list[str], rows: list[list[str]]):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.style = "Table Grid"
    set_table_borders(table)

    widths = (
        [Inches(1.05), Inches(3.35), Inches(2.10)]
        if len(headers) == 3
        else [Inches(6.5 / len(headers)) for _ in headers]
    )

    header_row = table.rows[0]
    header_properties = header_row._tr.get_or_add_trPr()
    repeat = OxmlElement("w:tblHeader")
    repeat.set(qn("w:val"), "true")
    header_properties.append(repeat)

    for index, text in enumerate(headers):
        cell = header_row.cells[index]
        cell.width = widths[index]
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        set_cell_shading(cell, "1F4E78")
        set_cell_margins(cell)
        paragraph = cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.space_after = Pt(0)
        run = paragraph.add_run(text)
        set_run_font(run, size=9.5, bold=True, color="FFFFFF")

    for row_index, values in enumerate(rows):
        row = table.add_row()
        row_properties = row._tr.get_or_add_trPr()
        no_split = OxmlElement("w:cantSplit")
        row_properties.append(no_split)
        normalized = values + [""] * (len(headers) - len(values))
        for index, text in enumerate(normalized[: len(headers)]):
            cell = row.cells[index]
            cell.width = widths[index]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            set_cell_margins(cell)
            set_cell_shading(cell, "EAF2F8" if row_index % 2 else "FFFFFF")
            paragraph = cell.paragraphs[0]
            paragraph.alignment = (
                WD_ALIGN_PARAGRAPH.CENTER if index == 0 else WD_ALIGN_PARAGRAPH.LEFT
            )
            paragraph.paragraph_format.space_after = Pt(0)
            paragraph.paragraph_format.line_spacing = 1.0
            run = paragraph.add_run(text)
            set_run_font(run, size=9.2)

    after = doc.add_paragraph()
    after.paragraph_format.space_after = Pt(0)


def add_figure(doc: Document, image_path: Path, alt_text: str):
    if not image_path.exists():
        raise FileNotFoundError(f"No se encontró la figura: {image_path}")
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before = Pt(4)
    paragraph.paragraph_format.space_after = Pt(0)
    paragraph.paragraph_format.keep_with_next = True
    run = paragraph.add_run()
    shape = run.add_picture(str(image_path), width=Inches(6.35))
    shape._inline.docPr.set("descr", alt_text)
    shape._inline.docPr.set("title", alt_text)


def markdown_to_docx(source: Path, destination: Path):
    lines = source.read_text(encoding="utf-8").splitlines()
    doc = Document()
    configure_styles(doc)
    configure_page(doc)
    doc.core_properties.title = "Propuesta de investigación"
    doc.core_properties.subject = "Detección de patrones en la monitorización de sistemas distribuidos"
    doc.core_properties.author = "Semillero de investigación"

    buffer: list[str] = []
    cover_mode = True
    title_seen = False

    index = 0
    while index < len(lines):
        raw = lines[index]
        line = raw.rstrip()
        if not line.strip():
            flush_paragraph(doc, buffer, cover_mode)
            index += 1
            continue
        if line.strip() == "---":
            flush_paragraph(doc, buffer, cover_mode)
            index += 1
            continue

        if (
            "|" in line
            and index + 1 < len(lines)
            and is_table_separator(lines[index + 1])
        ):
            flush_paragraph(doc, buffer, cover_mode)
            headers = split_table_row(line)
            index += 2
            rows: list[list[str]] = []
            while index < len(lines) and "|" in lines[index] and lines[index].strip():
                rows.append(split_table_row(lines[index]))
                index += 1
            add_markdown_table(doc, headers, rows)
            continue

        image_match = re.match(r"^!\[(.*?)\]\((.*?)\)$", line.strip())
        if image_match:
            flush_paragraph(doc, buffer, cover_mode)
            image_path = (source.parent / image_match.group(2)).resolve()
            add_figure(doc, image_path, image_match.group(1).strip())
            index += 1
            continue

        caption_match = re.match(r"^\*(Figura\s+\d+\..+?)\*$", line.strip())
        if caption_match:
            flush_paragraph(doc, buffer, cover_mode)
            paragraph = doc.add_paragraph(style="Figure Caption")
            run = paragraph.add_run(caption_match.group(1))
            set_run_font(run, size=9, italic=True, color="404040")
            index += 1
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", line)
        if heading:
            flush_paragraph(doc, buffer, cover_mode)
            level = len(heading.group(1))
            text = heading.group(2).strip()
            if level == 1 and not title_seen:
                p = doc.add_paragraph(style="Title")
                add_inline(p, text)
                title_seen = True
                index += 1
                continue
            cover_mode = False
            if text in {"7 Plan de trabajo", "Referencias"}:
                doc.add_page_break()
            p = doc.add_paragraph(style=f"Academic H{min(level - 1, 4)}")
            add_inline(p, text)
            index += 1
            continue

        if cover_mode and line.lstrip().startswith("**"):
            flush_paragraph(doc, buffer, cover_mode)
            clean = line.strip().removesuffix("  ").replace("**", "").strip()
            p = doc.add_paragraph(style="Academic Subtitle")
            add_inline(p, clean)
            index += 1
            continue

        bullet = re.match(r"^[-*]\s+(.+)$", line)
        numbered = re.match(r"^\d+\.\s+(.+)$", line)
        if bullet or numbered:
            flush_paragraph(doc, buffer, cover_mode)
            p = doc.add_paragraph(style="List Bullet" if bullet else "List Number")
            add_inline(p, (bullet or numbered).group(1))
            index += 1
            continue

        buffer.append(line)
        index += 1

    flush_paragraph(doc, buffer, cover_mode)
    destination.parent.mkdir(parents=True, exist_ok=True)
    doc.save(destination)


def export_pdf(docx_path: Path, pdf_dir: Path):
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise SystemExit(
            "No se encontró LibreOffice (soffice) en PATH. "
            "El DOCX sí fue generado; instale LibreOffice para exportar a PDF."
        )
    pdf_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(pdf_dir), str(docx_path)],
        check=True,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--docx", type=Path, default=DEFAULT_DOCX)
    parser.add_argument("--pdf", action="store_true", help="Exporta también a PDF mediante LibreOffice.")
    parser.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF_DIR)
    args = parser.parse_args()

    build_figures()
    markdown_to_docx(args.source.resolve(), args.docx.resolve())
    print(f"DOCX: {args.docx.resolve()}")
    if args.pdf:
        export_pdf(args.docx.resolve(), args.pdf_dir.resolve())
        print(f"PDF: {(args.pdf_dir / (args.docx.stem + '.pdf')).resolve()}")


if __name__ == "__main__":
    main()
