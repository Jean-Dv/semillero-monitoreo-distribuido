#!/usr/bin/env python3
"""Export the frozen comparison cohort from the local ClickHouse instance."""

from __future__ import annotations

import argparse
import hashlib
import os
import tempfile
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPORTS = (
    (ROOT / "sql" / "export_features_v1.sql", ROOT / "data" / "features_v1.csv"),
    (
        ROOT / "sql" / "export_evaluation_reference_v1.sql",
        ROOT / "data" / "evaluation_reference_v1.csv",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        default=os.environ.get("AIOPSLAB_CLICKHOUSE_URL", "http://127.0.0.1:8123/"),
    )
    parser.add_argument(
        "--user", default=os.environ.get("CLICKHOUSE_USER", "aiopslab")
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("CLICKHOUSE_PASSWORD", "aiopslab-local"),
    )
    return parser.parse_args()


def endpoint(base_url: str, user: str, password: str) -> str:
    query = urllib.parse.urlencode(
        {"database": "aiopslab", "user": user, "password": password}
    )
    return f"{base_url.rstrip('/')}/?{query}"


def export_one(url: str, sql_path: Path, output_path: Path) -> str:
    sql = sql_path.read_bytes()
    request = urllib.request.Request(url, data=sql, method="POST")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(request, timeout=120) as response:
        with tempfile.NamedTemporaryFile(
            dir=output_path.parent, prefix=f".{output_path.name}.", delete=False
        ) as temporary:
            temporary_path = Path(temporary.name)
            digest = hashlib.sha256()
            while chunk := response.read(1024 * 1024):
                temporary.write(chunk)
                digest.update(chunk)
    temporary_path.replace(output_path)
    return digest.hexdigest()


def main() -> None:
    args = parse_args()
    url = endpoint(args.url, args.user, args.password)
    checksums = []
    for sql_path, output_path in EXPORTS:
        digest = export_one(url, sql_path, output_path)
        checksums.append(f"{digest}  {output_path.name}")
        print(f"Exported {output_path.name}: sha256={digest}")
    checksum_path = ROOT / "data" / "SHA256SUMS"
    checksum_path.write_text("\n".join(checksums) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
