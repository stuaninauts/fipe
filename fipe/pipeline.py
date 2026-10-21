"""Build the clean price table from everything under data/raw/.

    uv run python -m fipe.pipeline

Reads the v1 scraper CSVs and the collector cache, cleans them (fipe/clean.py), adds prices in reais of the
latest IPCA month (fipe/inflation.py) and writes data/processed/prices.parquet plus a coverage summary in
data/processed/coverage.csv and clean_report.json. All stay local (docs/adr/0001).
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from fipe.aggregate import coverage
from fipe.clean import clean, read_api_cache, read_v1_csv
from fipe.inflation import DEFAULT_PATH as IPCA_PATH
from fipe.inflation import deflate, load_ipca

RAW = Path("data/raw")
PROCESSED = Path("data/processed")
# v1 scraper CSVs: "janeiro-2004 " (trailing space) up to 2023, "janeiro-2024.csv" after.
V1_GLOBS = ["janeiros-*/janeiro-*"]


def v1_files(raw: Path = RAW) -> list[Path]:
    files = {p for pattern in V1_GLOBS for p in raw.glob(pattern) if p.is_file()}
    return sorted(files)


def build(raw: Path = RAW, ipca_path: Path = IPCA_PATH) -> tuple[pd.DataFrame, dict]:
    frames = [read_v1_csv(p) for p in v1_files(raw)]
    cache = raw / "fipe_api.sqlite"
    if cache.exists():
        frames.append(read_api_cache(cache))
    if not frames:
        raise SystemExit(f"no source found under {raw}")
    prices, report = clean(pd.concat(frames, ignore_index=True))
    prices = deflate(prices, load_ipca(ipca_path))
    return prices, asdict(report)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--raw", type=Path, default=RAW)
    parser.add_argument("--out", type=Path, default=PROCESSED)
    args = parser.parse_args(argv)

    prices, report = build(args.raw)
    args.out.mkdir(parents=True, exist_ok=True)
    prices.to_parquet(args.out / "prices.parquet", index=False)
    cov = coverage(prices)
    cov.to_csv(args.out / "coverage.csv", index=False)
    (args.out / "clean_report.json").write_text(json.dumps(report, indent=1) + "\n")

    print(
        f"prices: {report['rows_out']:,} rows (from {report['rows_in']:,}), real values in reais of "
        f"{prices.attrs['price_base']}",
        file=sys.stderr,
    )
    for key in [
        "invalid_codigo",
        "invalid_price",
        "invalid_year",
        "duplicates_dropped",
        "duplicate_conflicts",
        "fuel_group_collisions",
    ]:
        print(f"  {key}: {report[key]}", file=sys.stderr)
    print(f"  by source: {report['by_source']}", file=sys.stderr)
    print(cov.to_string(index=False), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
