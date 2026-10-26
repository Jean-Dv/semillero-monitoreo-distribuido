"""Genera las figuras explicativas de la propuesta de investigación."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FIGURE_DIR = ROOT / "assets" / "figures"

NAVY = "#1F4E78"
MID_BLUE = "#5B9BD5"
PALE_BLUE = "#EAF2F8"
VERY_PALE_BLUE = "#F5F9FC"
GRAY = "#5A6570"
LIGHT_GRAY = "#D9E1E8"
DARK = "#17202A"
WHITE = "#FFFFFF"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    names = ["arialbd.ttf" if bold else "arial.ttf", "calibrib.ttf" if bold else "calibri.ttf"]
    roots = [Path("C:/Windows/Fonts"), Path("/usr/share/fonts/truetype/dejavu")]
    for root in roots:
        for name in names:
            candidate = root / name
            if candidate.exists():
                return ImageFont.truetype(str(candidate), size=size)
    fallback = roots[-1] / ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf")
    return ImageFont.truetype(str(fallback), size=size)


def wrap(draw: ImageDraw.ImageDraw, text: str, selected_font, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if draw.textbbox((0, 0), candidate, font=selected_font)[2] <= max_width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def centered_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    selected_font,
    fill: str = DARK,
    spacing: int = 10,
) -> None:
    x1, y1, x2, y2 = box
    lines = wrap(draw, text, selected_font, x2 - x1 - 36)
    line_height = selected_font.size + spacing
    total_height = len(lines) * line_height - spacing
    y = y1 + ((y2 - y1) - total_height) / 2
    for line in lines:
        width = draw.textbbox((0, 0), line, font=selected_font)[2]
        draw.text((x1 + ((x2 - x1) - width) / 2, y), line, font=selected_font, fill=fill)
        y += line_height


def rounded_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: str,
    outline: str = NAVY,
    width: int = 5,
    radius: int = 28,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str = NAVY,
    width: int = 8,
    head: int = 24,
) -> None:
    draw.line([start, end], fill=color, width=width)
    x1, y1 = start
    x2, y2 = end
    if abs(x2 - x1) >= abs(y2 - y1):
        direction = 1 if x2 > x1 else -1
        points = [(x2, y2), (x2 - direction * head, y2 - head // 2), (x2 - direction * head, y2 + head // 2)]
    else:
        direction = 1 if y2 > y1 else -1
        points = [(x2, y2), (x2 - head // 2, y2 - direction * head), (x2 + head // 2, y2 - direction * head)]
    draw.polygon(points, fill=color)


def problem_figure(path: Path) -> None:
    image = Image.new("RGB", (2400, 1050), WHITE)
    draw = ImageDraw.Draw(image)
    title_font = font(58, bold=True)
    group_font = font(34, bold=True)
    label_font = font(34, bold=True)
    body_font = font(31)
    note_font = font(27)

    centered_text(draw, (80, 28, 2320, 120), "Del problema operativo a la evidencia para decidir", title_font, NAVY)

    draw.text((80, 170), "Señales separadas", font=group_font, fill=NAVY)
    signal_boxes = [
        ((80, 245, 450, 385), "Métricas"),
        ((80, 455, 450, 595), "Registros"),
        ((80, 665, 450, 805), "Trazas"),
    ]
    for box, text in signal_boxes:
        rounded_box(draw, box, PALE_BLUE, outline=MID_BLUE)
        centered_text(draw, box, text, label_font, NAVY)

    problem_box = (640, 300, 1060, 750)
    rounded_box(draw, problem_box, VERY_PALE_BLUE)
    centered_text(
        draw,
        (670, 325, 1030, 720),
        "Fragmentación del análisis\n\nVolumen y heterogeneidad\nDesfase temporal\nDatos faltantes\nCorrelación manual",
        body_font,
    )

    artifact_box = (1245, 270, 1755, 780)
    rounded_box(draw, artifact_box, PALE_BLUE)
    centered_text(
        draw,
        (1280, 300, 1720, 750),
        "Artefacto experimental\n\nRepresentación conjunta\nReconocimiento de patrones\nEvidencia interpretable y trazable",
        body_font,
    )

    decision_box = (1940, 330, 2320, 720)
    rounded_box(draw, decision_box, VERY_PALE_BLUE)
    centered_text(
        draw,
        (1970, 355, 2290, 695),
        "Apoyo a decisiones\n\nInformación contextual\nSin sustituir el juicio\nSin afirmar causalidad",
        body_font,
    )

    for _, y1, _, y2 in [box for box, _ in signal_boxes]:
        draw.line([(450, (y1 + y2) // 2), (545, (y1 + y2) // 2)], fill=MID_BLUE, width=6)
        draw.line([(545, (y1 + y2) // 2), (545, 525)], fill=MID_BLUE, width=6)
    arrow(draw, (545, 525), (640, 525), color=MID_BLUE)
    arrow(draw, (1060, 525), (1245, 525))
    arrow(draw, (1755, 525), (1940, 525))

    centered_text(
        draw,
        (350, 880, 2050, 1000),
        "Reunir fuentes en una interfaz no crea por sí solo una representación multimodal; la relación semántica y temporal debe diseñarse y evaluarse.",
        note_font,
        GRAY,
    )
    image.save(path, dpi=(300, 300), optimize=True)


def dsrm_figure(path: Path) -> None:
    image = Image.new("RGB", (2400, 1500), WHITE)
    draw = ImageDraw.Draw(image)
    title_font = font(58, bold=True)
    phase_font = font(34, bold=True)
    body_font = font(29)
    feedback_font = font(28, bold=True)

    centered_text(draw, (80, 25, 2320, 115), "Aplicación iterativa de DSRM al proyecto", title_font, NAVY)

    boxes = {
        1: (90, 210, 710, 600),
        2: (890, 210, 1510, 600),
        3: (1690, 210, 2310, 600),
        4: (1690, 820, 2310, 1210),
        5: (890, 820, 1510, 1210),
        6: (90, 820, 710, 1210),
    }
    content = {
        1: ("1 Problema", "Evidencia, necesidad y requisitos\nProducto: pregunta y alcance"),
        2: ("2 Objetivos", "Variables, métricas y criterios\nProducto: objetivos verificables"),
        3: ("3 Diseño y desarrollo", "Flujo, método, procesamiento y extensión\nProducto: prototipo versionado"),
        4: ("4 Demostración", "Escenarios locales controlados\nProducto: ejecuciones trazables"),
        5: ("5 Evaluación", "Comparación con datos de referencia\nProducto: resultados y decisión de iterar"),
        6: ("6 Comunicación", "Método, artefacto, resultados y límites\nProducto: entregables reproducibles"),
    }

    for index, box in boxes.items():
        x1, y1, x2, y2 = box
        rounded_box(draw, box, VERY_PALE_BLUE)
        draw.rounded_rectangle((x1, y1, x2, y1 + 92), radius=28, fill=NAVY, outline=NAVY, width=3)
        draw.rectangle((x1, y1 + 50, x2, y1 + 92), fill=NAVY)
        centered_text(draw, (x1 + 18, y1 + 12, x2 - 18, y1 + 84), content[index][0], phase_font, WHITE)
        centered_text(draw, (x1 + 28, y1 + 112, x2 - 28, y2 - 24), content[index][1], body_font)

    arrow(draw, (710, 405), (890, 405))
    arrow(draw, (1510, 405), (1690, 405))
    arrow(draw, (2000, 600), (2000, 820))
    arrow(draw, (1690, 1015), (1510, 1015))
    arrow(draw, (890, 1015), (710, 1015))

    # Retroalimentación: si la evaluación no satisface los criterios, se revisan objetivos o diseño.
    draw.line([(1200, 820), (1200, 705), (2000, 705), (2000, 655)], fill=MID_BLUE, width=7)
    arrow(draw, (1200, 705), (1200, 600), color=MID_BLUE, width=7)
    arrow(draw, (1800, 705), (1800, 600), color=MID_BLUE, width=7)
    centered_text(draw, (1270, 615, 1930, 685), "Iteración si los criterios no se cumplen", feedback_font, MID_BLUE)

    centered_text(
        draw,
        (250, 1320, 2150, 1435),
        "La secuencia es nominal: la trazabilidad de requisitos, datos, versiones y resultados se conserva durante todas las iteraciones.",
        body_font,
        GRAY,
    )
    image.save(path, dpi=(300, 300), optimize=True)


def build_figures() -> list[Path]:
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    outputs = [
        FIGURE_DIR / "problema_flujo_conceptual.png",
        FIGURE_DIR / "dsrm_aplicacion_proyecto.png",
    ]
    problem_figure(outputs[0])
    dsrm_figure(outputs[1])
    return outputs


if __name__ == "__main__":
    for output in build_figures():
        print(output)
