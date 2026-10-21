"""Write the public export: aggregate tables only (docs/adr/0001), read by the site at build time.

    uv run python -m fipe.pipeline          # first: data/processed/prices.parquet
    uv run python -m fipe.export            # rewrite web/public/data/
    uv run python -m fipe.export --check    # fail if the committed export is out of date

Every table goes out as JSON (records) and CSV, listed in manifest.json with its columns, row count and the
month the real values are expressed in. Never edit these files by hand.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

from fipe import aggregate
from fipe.inflation import DEFAULT_PATH as IPCA_PATH
from fipe.inflation import load_ipca

PRICES = Path("data/processed/prices.parquet")
CLEAN_REPORT = Path("data/processed/clean_report.json")
OUT = Path("web/public/data")
ATTRIBUTION = "Fonte: Tabela FIPE (Fundação Instituto de Pesquisas Econômicas); IPCA: IBGE."
DESCRIPTIONS = {
    "yearly_change": "Same used car from one January to the next: median change (nominal, real) and IPCA.",
    "new_vs_used": "Used car of the current model year over the same car brand new, per January.",
    "retention_by_age": "Share of the brand-new price kept at each age, same January (all years and recent).",
    "coverage": "Prices, brand-new prices, FIPE codes and brands per reference month.",
    "explore_retention": "retention_by_age by brand, fuel group and brand-new price band (explore page).",
    "explore_yearly": "Real change of the same used car per January by brand, fuel group and price band.",
    "fuel_labels": "Prices per fuel label and January (FIPE split the Gasolina label in 2024).",
    "clean_report": "What cleaning dropped: invalid rows, duplicates and fuel group collisions.",
}


def clean_report_table(report: dict) -> pd.DataFrame:
    """The pipeline's cleaning report as one row, with the source counts as their own columns."""
    flat = {k: v for k, v in report.items() if k != "by_source"}
    flat |= {f"rows_from_{source}": n for source, n in sorted(report["by_source"].items())}
    return pd.DataFrame([flat])


def build_tables(prices: pd.DataFrame, ipca: pd.DataFrame, report: dict) -> dict[str, pd.DataFrame]:
    return {
        "yearly_change": aggregate.yearly_change(prices, ipca),
        "new_vs_used": aggregate.new_vs_used(prices),
        "retention_by_age": aggregate.retention_by_age(prices),
        "coverage": aggregate.coverage(prices),
        "explore_retention": aggregate.explore_retention(prices),
        "explore_yearly": aggregate.explore_yearly(prices),
        "fuel_labels": aggregate.fuel_labels(prices),
        "clean_report": clean_report_table(report),
    }


def render(tables: dict[str, pd.DataFrame], price_base: str) -> dict[str, str]:
    """File name -> exact file content, so writing and checking compare the same bytes."""
    files: dict[str, str] = {}
    manifest = {"attribution": ATTRIBUTION, "price_base": price_base, "tables": {}}
    for name, df in tables.items():
        files[f"{name}.json"] = json.dumps(df.to_dict("records"), ensure_ascii=False, indent=1) + "\n"
        files[f"{name}.csv"] = df.to_csv(index=False, lineterminator="\n")
        manifest["tables"][name] = {
            "description": DESCRIPTIONS[name],
            "rows": len(df),
            "columns": list(df.columns),
        }
    files["manifest.json"] = json.dumps(manifest, ensure_ascii=False, indent=1) + "\n"
    return files


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument(
        "--check", action="store_true", help="compare with the files on disk instead of writing"
    )
    parser.add_argument("--prices", type=Path, default=PRICES)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args(argv)

    if not args.prices.exists():
        print(f"{args.prices} not found: run `uv run python -m fipe.pipeline` first", file=sys.stderr)
        return 2
    ipca = load_ipca(IPCA_PATH)
    last = ipca.sort_values(["year", "month"]).iloc[-1]
    price_base = f"{int(last['year'])}-{int(last['month']):02d}"
    report = json.loads(args.prices.with_name(CLEAN_REPORT.name).read_text())
    files = render(build_tables(pd.read_parquet(args.prices), ipca, report), price_base)

    if args.check:
        stale = [
            n
            for n, text in files.items()
            if not (args.out / n).exists() or (args.out / n).read_text() != text
        ]
        if stale:
            print(
                f"export out of date: {', '.join(stale)}. Run `uv run python -m fipe.export`.",
                file=sys.stderr,
            )
            return 1
        print("export up to date", file=sys.stderr)
        return 0

    args.out.mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        (args.out / name).write_text(text)
    print(f"wrote {len(files)} files to {args.out} (real values in reais of {price_base})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
