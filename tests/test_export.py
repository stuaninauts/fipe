"""Golden tests over the committed export (web/public/data/).

CI has no raw FIPE data (docs/adr/0001), so it cannot rebuild the export. These tests pin the published
numbers instead: regenerating the export with a different result fails here until the test is updated on
purpose, in the same PR. Locally, with data/processed/prices.parquet present, the export is also rebuilt
and compared.
"""

import json
from pathlib import Path

import pandas as pd
import pytest

from fipe import export

OUT = Path("web/public/data")


def load(name):
    # json.loads keeps the exact decimals of the export (pd.read_json reads 0.5902 as 0.5902000000000001)
    return pd.DataFrame(json.loads((OUT / f"{name}.json").read_text()))


def test_manifest_lists_every_table_with_its_files():
    manifest = json.loads((OUT / "manifest.json").read_text())
    assert set(manifest["tables"]) == set(export.DESCRIPTIONS)
    assert manifest["price_base"] == "2026-09"
    assert "Tabela FIPE" in manifest["attribution"]
    for name, meta in manifest["tables"].items():
        df = load(name)
        assert len(df) == meta["rows"]
        assert list(df.columns) == meta["columns"]
        assert (OUT / f"{name}.csv").exists()


def test_the_2021_2022_shock():
    row = load("yearly_change").set_index("to_year").loc[2022]
    assert (row["n"], row["median_nominal"], row["median_real"]) == (24800, 0.2035, 0.0903)
    others = load("yearly_change").query("to_year != 2022")
    assert (others["median_real"] < 0).all()  # the only year a used car gained in real terms


def test_brand_new_gap_is_about_ten_percent_until_2021():
    ratio = load("new_vs_used").set_index("ref_year")["median_ratio"]
    assert ratio.loc[2004:2021].between(0.87, 0.92).all()
    assert ratio.loc[2022] == 0.9501


def test_retention_at_five_years():
    r = load("retention_by_age").set_index(["scope", "age"])
    assert r.loc[("all", 5), "median_ratio"] == 0.5902
    assert r.loc[("all", 5), "n"] == 5851


def test_no_table_exposes_a_price_per_model():
    """Aggregates only (ADR 0001): no column that would identify a car or carry its price."""
    forbidden = {"codigo_fipe", "model", "price_brl", "price_real_brl"}
    for name in export.DESCRIPTIONS:
        assert forbidden.isdisjoint(load(name).columns), name


@pytest.mark.skipif(not export.PRICES.exists(), reason="needs the local raw data (docs/adr/0001)")
def test_committed_export_matches_the_local_data():
    assert export.main(["--check"]) == 0


def test_explore_cubes_agree_with_the_headline_tables():
    cube = load("explore_retention").query("group_type == 'all'").drop(columns=["group_type", "group"])
    base = load("retention_by_age")
    assert cube.reset_index(drop=True).equals(base.reset_index(drop=True))
    yearly = load("explore_yearly").query("group_type == 'all'").set_index("to_year")
    headline = load("yearly_change").set_index("to_year")
    assert (yearly["n"] == headline["n"]).all()
    assert (yearly["median_real"] == headline["median_real"]).all()


def test_quality_tables():
    report = load("clean_report").iloc[0]
    assert (report["rows_out"], report["fuel_group_collisions"], report["duplicate_conflicts"]) == (
        431303,
        0,
        0,
    )
    labels = load("fuel_labels").set_index(["ref_year", "fuel"])["prices"]
    assert "Flex" not in labels.loc[2023].index
    assert labels.loc[(2024, "Flex")] == 6401
