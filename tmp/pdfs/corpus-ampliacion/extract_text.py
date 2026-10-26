from pathlib import Path

from pypdf import PdfReader


PAIRS = {
    "papers/scrocca-etal-2020-kaiju-event-driven-observability.pdf": "kaiju.txt",
    "papers/li-etal-2024-explainable-anomaly-detection-survey.pdf": "xad-survey.txt",
    "papers/sipple-youssef-2022-explainable-ai-anomaly-detection.pdf": "sipple.txt",
    "papers/jha-etal-2025-itbench-ai-agents.pdf": "itbench.txt",
    "papers/niedermaier-etal-2019-observability-monitoring-interview-study.pdf": "observability-interviews.txt",
}

root = Path(__file__).resolve().parents[3]
output_dir = Path(__file__).resolve().parent

for relative_source, output_name in PAIRS.items():
    reader = PdfReader(root / relative_source)
    pages = []
    for page_number, page in enumerate(reader.pages, start=1):
        pages.append(f"\n===== PDF PAGE {page_number} =====\n")
        pages.append(page.extract_text() or "")
    (output_dir / output_name).write_text("".join(pages), encoding="utf-8")
