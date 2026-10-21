"""IPCA (IBGE) to express FIPE prices in reais of a single month.

The monthly IPCA index (SIDRA table 1737, variable 2266, base Dec 1993 = 100) is versioned in
reference/ipca.csv, so tests and the pipeline never need the network. Refresh it with:

    uv run python -m fipe.inflation --update
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from pathlib import Path

import pandas as pd

SIDRA_URL = "https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/all"
DEFAULT_PATH = Path("reference/ipca.csv")
FIRST_YEAR = 2000  # older months are not needed (the FIPE data starts in 2004)


def parse_sidra(payload: list[dict]) -> pd.DataFrame:
    """SIDRA JSON (first row is the header) -> year, month, index. Months without a value are dropped."""
    rows = []
    for row in payload[1:]:
        code, value = row["D3C"], row["V"]
        try:
            index = float(value)
        except ValueError:
            continue  # "..." or "-" for months not published yet
        rows.append({"year": int(code[:4]), "month": int(code[4:]), "ipca_index": index})
    df = pd.DataFrame(rows, columns=["year", "month", "ipca_index"])
    return df[df["year"] >= FIRST_YEAR].sort_values(["year", "month"]).reset_index(drop=True)


def fetch_ipca(timeout: float = 60.0) -> pd.DataFrame:
    with urllib.request.urlopen(SIDRA_URL, timeout=timeout) as resp:
        return parse_sidra(json.load(resp))


def load_ipca(path: Path = DEFAULT_PATH) -> pd.DataFrame:
    return pd.read_csv(path, dtype={"year": "int16", "month": "int8", "ipca_index": "float64"})


def deflate(prices: pd.DataFrame, ipca: pd.DataFrame, base: tuple[int, int] | None = None) -> pd.DataFrame:
    """Add `price_real_brl`: the price in reais of the `base` month (default: the latest IPCA month).

    A reference month without an IPCA value is an error, never a silent NaN.
    """
    ipca = ipca.sort_values(["year", "month"])
    base_year, base_month = base or (int(ipca["year"].iloc[-1]), int(ipca["month"].iloc[-1]))
    base_row = ipca[(ipca["year"] == base_year) & (ipca["month"] == base_month)]
    if base_row.empty:
        raise ValueError(f"no IPCA for the base month {base_year}-{base_month:02d}")
    base_index = float(base_row["ipca_index"].iloc[0])

    keyed = ipca.rename(columns={"year": "ref_year", "month": "ref_month"})
    out = prices.merge(keyed, on=["ref_year", "ref_month"], how="left", validate="many_to_one")
    missing = out.loc[out["ipca_index"].isna(), ["ref_year", "ref_month"]].drop_duplicates()
    if not missing.empty:
        months = ", ".join(f"{y}-{m:02d}" for y, m in missing.itertuples(index=False))
        raise ValueError(f"no IPCA for reference month(s): {months}")
    out["price_real_brl"] = (out["price_brl"] * base_index / out["ipca_index"]).round(2)
    out.attrs["price_base"] = f"{base_year}-{base_month:02d}"
    return out.drop(columns="ipca_index")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Refresh reference/ipca.csv from IBGE SIDRA.")
    parser.add_argument("--update", action="store_true", help="download the series and rewrite the file")
    parser.add_argument("--path", type=Path, default=DEFAULT_PATH)
    args = parser.parse_args(argv)
    if not args.update:
        parser.print_help()
        return 0
    df = fetch_ipca()
    args.path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.path, index=False)
    first, last = df.iloc[0], df.iloc[-1]
    span = f"{int(first['year'])}-{int(first['month']):02d} to {int(last['year'])}-{int(last['month']):02d}"
    print(f"{args.path}: {len(df)} months, {span}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
