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


def test_explore_cubes_break_the_same_numbers_down_by_group(monkeypatch):
    monkeypatch.setattr(aggregate, "EXPLORE_MIN_BRAND_N", 1)
    prices = table(
        price(2024, "001500-1", 0, 100_000, is_new=True),
        price(2024, "001500-1", 2021, 60_000),
        price(2024, "001600-1", 0, 300_000, fuel="Diesel", is_new=True),
        price(2024, "001600-1", 2021, 210_000, fuel="Diesel"),
    )
    cube = (
        aggregate.explore_retention(prices)
        .query("scope == 'all' and age == 3")
        .set_index(["group_type", "group"])
    )
    assert cube.loc[("all", "all"), "n"] == 2
    assert cube.loc[("fuel_group", "diesel"), "median_ratio"] == 0.7
    assert cube.loc[("fuel_group", "gasoline"), "median_ratio"] == 0.6
    # the cheaper brand-new car lands in a lower price band than the expensive one
    bands = cube.xs("price_band")["median_ratio"]
    assert bands.index.min() < bands.index.max()
    assert bands.loc[bands.index.min()] == 0.6


def test_price_bands_work_with_fewer_cars_than_bands():
    bands = aggregate._quintiles(pd.Series([10.0, 20.0]), pd.Series([2024, 2024]))
    assert bands.tolist() == ["q3", "q5"]


def test_cohort_follows_the_car_bought_new_and_deflates_both_prices():
    prices = table(
        price(2023, "001500-1", 0, 100_000, is_new=True),  # bought new in Jan 2023 (real 110,000)
        price(2024, "001500-1", 2023, 99_000),  # one year later, model year 2023 (real 99,000)
        price(2024, "001500-1", 2022, 80_000),  # another model year: not this purchase
    )
    row = aggregate.cohort(prices).iloc[0]
    assert (row["purchase_year"], row["age"], row["n"]) == (2023, 1, 1)
    assert row["median_nominal"] == 0.99
    assert row["median_real"] == 0.9


def test_loss_by_age_leaves_out_the_shock_year():
    prices = table(
        price(2021, "001500-1", 2020, 100_000, deflator=1.0),
        price(2022, "001500-1", 2020, 120_000, deflator=1.0),  # the 2022 arrival: left out
        price(2023, "001500-1", 2020, 108_000, deflator=1.0),
    )
    out = aggregate.loss_by_age(prices)
    assert out["age"].tolist() == [3]
    assert out.loc[0, "median_real"] == -0.1


def test_four_year_change_pairs_the_same_car_four_years_apart():
    prices = table(
        price(2021, "001500-1", 2018, 100_000, deflator=1.0),
        price(2025, "001500-1", 2018, 93_000, deflator=1.0),
    )
    row = aggregate.four_year_change(prices).iloc[0]
    assert (row["from_year"], row["to_year"], row["n"], row["median_real"]) == (2021, 2025, 1, -0.07)


def test_holds_value_compares_with_cars_bought_the_same_year(monkeypatch):
    monkeypatch.setattr(aggregate, "HOLDS_VALUE_MIN_N", 1)
    monkeypatch.setattr(aggregate, "PRICE_BANDS", ["q1"])  # one band: compare with the whole purchase year
    rows = []
    for codigo, brand, kept in [("001", "Toyota", 0.66), ("002", "Fiat", 0.60), ("003", "Fiat", 0.54)]:
        new = price(2015, codigo, 0, 100_000, is_new=True, deflator=1.0)
        used = price(2020, codigo, 2015, 100_000 * kept, deflator=1.0)
        new["brand"] = used["brand"] = brand
        rows += [new, used]
    out = aggregate.holds_value(table(*rows)).set_index(["group_type", "group"])
    assert out.loc[("brand", "Toyota"), "median_relative"] == pytest.approx(1.1, abs=1e-3)
    assert out.loc[("brand", "Fiat"), "n"] == 2


def test_version_gap_compares_top_and_entry_of_a_family(monkeypatch):
    rows = []
    for codigo, model, paid, kept in [
        ("001", "Palio 1.0 Fire", 100_000, 0.60),
        ("002", "Palio 1.4 ELX", 120_000, 0.57),
        ("003", "Palio 1.8 Sporting", 150_000, 0.54),
    ]:
        new = price(2015, codigo, 0, paid, is_new=True, deflator=1.0)
        used = price(2020, codigo, 2015, paid * kept, deflator=1.0)
        new["model"] = used["model"] = model
        rows += [new, used]
    out = aggregate.version_gap(table(*rows), ages=(5,)).iloc[0]
    assert out["groups"] == 1
    assert out["median_gap"] == pytest.approx(-0.1)
    assert out["share_top_keeps_less"] == 1.0


def test_fuel_relabels_counts_label_changes(monkeypatch):
    prices = table(
        price(2010, "001500-1", 2008, 50_000, fuel="Gasolina"),
        price(2011, "001500-1", 2008, 45_000, fuel="Diesel"),
    )
    out = aggregate.fuel_relabels(prices, min_n=1)
    assert out.to_dict("records") == [
        {"from_year": 2010, "to_year": 2011, "fuel_from": "Gasolina", "fuel_to": "Diesel", "cars": 1}
    ]
