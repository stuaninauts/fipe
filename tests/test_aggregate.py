import pandas as pd
import pytest

from fipe import aggregate

IPCA = pd.DataFrame({"year": [2023, 2024], "month": [1, 1], "ipca_index": [100.0, 110.0]})


def price(year, codigo, model_year, value, fuel="Gasolina", is_new=False, deflator=None):
    """One clean row; real price = nominal * (IPCA 2024 / IPCA of the year) unless given."""
    index = {2023: 100.0, 2024: 110.0}
    real = value * 110.0 / index.get(year, 110.0) if deflator is None else value * deflator
    group = {"Álcool": "alcohol", "Diesel": "diesel"}.get(fuel, "gasoline")
    return {
        "ref_year": year,
        "ref_month": 1,
        "brand": "Fiat",
        "model": "Argo",
        "codigo_fipe": codigo,
        "is_new": is_new,
        "model_year": pd.NA if is_new else model_year,
        "fuel": fuel,
        "fuel_group": group,
        "price_brl": float(value),
        "price_real_brl": float(real),
    }


def table(*rows):
    df = pd.DataFrame(list(rows))
    df["model_year"] = df["model_year"].astype("Int64")
    return df


def test_yearly_change_pairs_the_same_car_across_the_fuel_relabel():
    prices = table(
        price(2023, "001500-1", 2020, 100_000),
        price(2024, "001500-1", 2020, 99_000, fuel="Flex"),  # same car, label changed in 2024
        price(2023, "001600-1", 2018, 50_000),  # disappears: no pair
        price(2023, "001500-1", 2020, 120_000, is_new=True),  # brand new: excluded from the used pairs
        price(2023, "001700-1", 0, 80_000, is_new=True),
        price(2024, "001700-1", 0, 84_000, is_new=True),
    )
    row = aggregate.yearly_change(prices, IPCA).iloc[0]
    assert (row["from_year"], row["to_year"], row["n"]) == (2023, 2024, 1)
    assert row["median_nominal"] == pytest.approx(-0.01)
    assert row["median_real"] == pytest.approx(99_000 / 110_000 - 1, abs=1e-4)
    assert row["ipca"] == pytest.approx(0.10)
    assert (row["new_n"], row["new_median_nominal"]) == (1, pytest.approx(0.05))


def test_new_vs_used_compares_the_current_model_year_with_brand_new():
    prices = table(
        price(2024, "001500-1", 2024, 90_000),
        price(2024, "001500-1", 0, 100_000, is_new=True),
        price(2024, "001500-1", 2023, 80_000),  # older model year: not in this comparison
        price(2024, "001900-1", 2024, 45_000),  # no brand-new price: no pair
    )
    row = aggregate.new_vs_used(prices).iloc[0]
    assert (row["ref_year"], row["n"], row["median_ratio"]) == (2024, 1, 0.9)


def test_retention_by_age_divides_by_the_same_month_brand_new_price():
    prices = table(
        price(2024, "001500-1", 0, 100_000, is_new=True),
        price(2024, "001500-1", 2024, 90_000),
        price(2024, "001500-1", 2021, 60_000),
        price(2024, "001500-1", 2000, 10_000),  # age 24: beyond max_age
    )
    out = aggregate.retention_by_age(prices, max_age=15).set_index(["scope", "age"])
    assert out.loc[("all", 0), "median_ratio"] == 0.9
    assert out.loc[("all", 3), "median_ratio"] == 0.6
    assert ("all", 24) not in out.index
    assert out.loc[("recent", 3), "n"] == 1


def test_coverage_counts_per_reference_month():
    prices = table(
        price(2024, "001500-1", 0, 100_000, is_new=True),
        price(2024, "001500-1", 2020, 60_000),
        price(2024, "001600-1", 2020, 40_000),
    )
    row = aggregate.coverage(prices).iloc[0]
    assert (row["prices"], row["new_car_prices"], row["codigos_fipe"], row["brands"]) == (3, 1, 2, 1)
