import pandas as pd
import pytest

from fipe.inflation import deflate, load_ipca, parse_sidra

IPCA = pd.DataFrame({"year": [2023, 2024, 2024], "month": [1, 1, 6], "ipca_index": [100.0, 105.0, 110.0]})


def prices(*months):
    return pd.DataFrame(
        {"ref_year": [y for y, _ in months], "ref_month": [m for _, m in months], "price_brl": 1000.0}
    )


def test_deflate_uses_the_latest_month_by_default():
    out = deflate(prices((2023, 1), (2024, 1)), IPCA)
    assert out["price_real_brl"].tolist() == [1100.0, 1047.62]
    assert out.attrs["price_base"] == "2024-06"


def test_deflate_with_an_explicit_base():
    out = deflate(prices((2023, 1)), IPCA, base=(2024, 1))
    assert out["price_real_brl"].tolist() == [1050.0]


def test_a_month_without_ipca_is_an_error():
    with pytest.raises(ValueError, match="2022-01"):
        deflate(prices((2022, 1)), IPCA)


def test_parse_sidra_skips_the_header_and_unpublished_months():
    payload = [
        {"D3C": "Mês (Código)", "V": "Valor"},
        {"D3C": "199912", "V": "1500.0"},  # before FIRST_YEAR
        {"D3C": "202401", "V": "7000.5"},
        {"D3C": "202402", "V": "..."},
    ]
    df = parse_sidra(payload)
    assert df.to_dict("records") == [{"year": 2024, "month": 1, "ipca_index": 7000.5}]


def test_versioned_series_covers_every_january_since_2004():
    ipca = load_ipca()
    januaries = set(ipca.loc[ipca["month"] == 1, "year"])
    assert set(range(2004, 2027)) <= januaries
    months = ipca["year"].astype(int) * 12 + ipca["month"].astype(int)
    assert (months.diff().dropna() == 1).all()  # no gaps
    assert (ipca["ipca_index"] > 0).all()
