from pathlib import Path

from pypdf import PdfReader


PAIRS = {
    "papers/zhang-etal-2022-deeptralog-trace-log-anomaly-detection.pdf": "deeptralog.txt",
    "papers/huang-etal-2023-mstgad-multimodal-anomaly-detection.pdf": "mstgad.txt",
    "papers/hou-etal-2021-pdiagnose-heterogeneous-data.pdf": "pdiagnose.txt",
    "papers/steidl-etal-2024-industry-runtime-anomalies.pdf": "industry-anomalies.txt",
    "papers/pham-etal-2025-rcaeval-benchmark.pdf": "rcaeval.txt",
    "papers/bakhtin-etal-2025-lo2-dataset.pdf": "lo2.txt",
    "papers/shkuro-etal-2022-schema-first-telemetry.pdf": "schema-first.txt",
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
