"""Turn the raw FIPE sources into one tidy price table.

Sources (all local, under data/raw/, never committed: docs/adr/0001):
- the v1 scraper CSVs, one file per month
  (`ano_ref;mes_ref;marca;modelo;ano_fab;valor;combustivel;codigo_fipe`);
- the collector's SQLite cache (fipe/cache.py), one JSON body per price.

A car is (codigo_fipe, model_year, fuel); a price is that car in a reference month
(CLAUDE.md, "Identidade de um preço"). Brand-new cars come from the endpoint as model year 32000 and become
`is_new = True` with no model year.
"""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

MONTHS = {
    "janeiro": 1,
    "fevereiro": 2,
    "março": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}
NEW_CAR_YEAR = "32000"
# In January 2024 FIPE split its "Gasolina" label into Flex, Híbrido, Elétrico and Gás Natural for the same
# cars. Following a car across years therefore uses this stable group; `fuel` keeps the label as published.
FUEL_GROUP = {"Álcool": "alcohol", "Diesel": "diesel"}  # every other label belongs to "gasoline"
CODIGO_FIPE = re.compile(r"\d{6}-\d")
PRICE = re.compile(r"R\$ (\d{1,3}(?:\.\d{3})*),(\d{2})")

# Raw columns shared by every source, before cleaning (all text except the reference month).
RAW_COLUMNS = [
    "ref_year",
    "ref_month",
    "brand",
    "model",
    "model_year_raw",
    "price_raw",
    "fuel",
    "codigo_fipe",
    "source",
]
# A price is unique on this key after cleaning.
KEY = ["ref_year", "ref_month", "codigo_fipe", "is_new", "model_year", "fuel"]
# A car across reference months: same code, model year and fuel group (see FUEL_GROUP).
CAR = ["codigo_fipe", "is_new", "model_year", "fuel_group"]
# Where both sources have the same price, the collector's copy wins (it is the newer, verified one).
SOURCE_RANK = {"api": 0, "csv_v1": 1}


@dataclass
class CleanReport:
    rows_in: int = 0
    rows_out: int = 0
    invalid_codigo: int = 0
    invalid_price: int = 0
    invalid_year: int = 0
    duplicates_dropped: int = 0
    duplicate_conflicts: int = 0  # duplicates whose prices differed (kept by source rank, then first seen)
    fuel_group_collisions: int = 0  # rows sharing a month and CAR key; must stay 0 for CAR to identify a car
    by_source: dict[str, int] = field(default_factory=dict)


def read_v1_csv(path: Path) -> pd.DataFrame:
    """One v1 scraper CSV. File names may end in a space; every field is read as text."""
    df = pd.read_csv(path, sep=";", dtype=str, keep_default_na=False, encoding="utf-8")
    out = pd.DataFrame(
        {
            "ref_year": pd.to_numeric(df["ano_ref"].str.strip()),
            "ref_month": df["mes_ref"].str.strip().str.lower().map(MONTHS),
            "brand": df["marca"],
            "model": df["modelo"],
            "model_year_raw": df["ano_fab"],
            "price_raw": df["valor"],
            "fuel": df["combustivel"],
            "codigo_fipe": df["codigo_fipe"],
            "source": "csv_v1",
        }
    )
    if out["ref_month"].isna().any():
        raise ValueError(f"{path}: unknown month name in mes_ref")
    return out[RAW_COLUMNS]


def read_api_cache(path: Path) -> pd.DataFrame:
    """Every price stored by the collector. MesReferencia comes as "janeiro de 2024 "."""
    rows = []
    with sqlite3.connect(path) as db:
        cursor = db.execute("select body from responses where endpoint = 'ConsultarValorComTodosParametros'")
        for (body,) in cursor:
            b = json.loads(body)
            month_name, _, year = b["MesReferencia"].strip().lower().partition(" de ")
            rows.append(
                {
                    "ref_year": int(year),
                    "ref_month": MONTHS[month_name],
                    "brand": b["Marca"],
                    "model": b["Modelo"],
                    "model_year_raw": str(b["AnoModelo"]),
                    "price_raw": b["Valor"],
                    "fuel": b["Combustivel"],
                    "codigo_fipe": b["CodigoFipe"],
                    "source": "api",
                }
            )
    return pd.DataFrame(rows, columns=RAW_COLUMNS)


def parse_price(raw: pd.Series) -> pd.Series:
    """ "R$ 1.234,56" -> 1234.56 (reais). Anything else becomes NaN."""
    parts = raw.str.strip().str.fullmatch(PRICE.pattern)
    digits = raw.str.strip().str.extract(PRICE.pattern)
    value = pd.to_numeric(digits[0].str.replace(".", "", regex=False) + "." + digits[1], errors="coerce")
    return value.where(parts)


def clean(raw: pd.DataFrame) -> tuple[pd.DataFrame, CleanReport]:
    """Validate, type and deduplicate the raw rows. Returns the price table and what was dropped."""
    report = CleanReport(rows_in=len(raw))
    df = raw.copy()
    for col in ["brand", "model", "fuel", "codigo_fipe", "model_year_raw", "price_raw"]:
        df[col] = df[col].astype(str).str.strip()

    ok_codigo = df["codigo_fipe"].str.fullmatch(CODIGO_FIPE.pattern)
    report.invalid_codigo = int((~ok_codigo).sum())

    df["price_brl"] = parse_price(df["price_raw"])
    ok_price = df["price_brl"].notna() & (df["price_brl"] > 0)
    report.invalid_price = int((ok_codigo & ~ok_price).sum())

    df["is_new"] = df["model_year_raw"] == NEW_CAR_YEAR
    year = pd.to_numeric(df["model_year_raw"].where(~df["is_new"]), errors="coerce")
    ok_year = df["is_new"] | year.between(1900, 2100)
    report.invalid_year = int((ok_codigo & ok_price & ~ok_year).sum())
    df["model_year"] = year.astype("Int64")

    df = df[ok_codigo & ok_price & ok_year].copy()

    df["_rank"] = df["source"].map(SOURCE_RANK)
    df = df.sort_values("_rank", kind="stable")
    dup = df.duplicated(KEY, keep=False)
    if dup.any():
        report.duplicate_conflicts = int(
            (df[dup].groupby(KEY, dropna=False)["price_brl"].nunique() > 1).sum()
        )
    before = len(df)
    df = df.drop_duplicates(KEY, keep="first")
    report.duplicates_dropped = before - len(df)

    df["fuel_group"] = df["fuel"].map(FUEL_GROUP).fillna("gasoline")
    report.fuel_group_collisions = int(df.duplicated(["ref_year", "ref_month", *CAR], keep=False).sum())

    df = df.sort_values(["ref_year", "ref_month", "brand", "model", "model_year", "fuel"], na_position="last")
    df = df[
        [
            "ref_year",
            "ref_month",
            "brand",
            "model",
            "codigo_fipe",
            "is_new",
            "model_year",
            "fuel",
            "fuel_group",
            "price_brl",
            "source",
        ]
    ].reset_index(drop=True)
    df["ref_year"] = df["ref_year"].astype("int16")
    df["ref_month"] = df["ref_month"].astype("int8")
    report.rows_out = len(df)
    report.by_source = {str(k): int(v) for k, v in df["source"].value_counts().sort_index().items()}
    return df, report
