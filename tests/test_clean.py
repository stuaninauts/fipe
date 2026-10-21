import json

import pandas as pd
import pytest

from fipe.api import Client, Response
from fipe.cache import Cache
from fipe.clean import RAW_COLUMNS, clean, parse_price, read_api_cache, read_v1_csv

HEADER = "ano_ref;mes_ref;marca;modelo;ano_fab;valor;combustivel;codigo_fipe\n"


def raw(*rows, source="csv_v1"):
    """Raw rows as (ref_year, brand, model, model_year, price, fuel, codigo), all in January."""
    return pd.DataFrame(
        [(y, 1, b, m, my, p, f, c, source) for y, b, m, my, p, f, c in rows],
        columns=RAW_COLUMNS,
    )


def test_parse_price_reads_brazilian_reais():
    got = parse_price(pd.Series(["R$ 1.234,56", "R$ 999,00", "R$ 1.234.567,89", "1234", "R$ 12,3"]))
    assert got.iloc[:3].tolist() == [1234.56, 999.0, 1234567.89]
    assert got.iloc[3:].isna().all()


def test_read_v1_csv_keeps_codes_as_text(tmp_path):
    path = tmp_path / "janeiro-2023 "  # v1 file names end in a space
    path.write_text(
        HEADER + "2023;janeiro;Acura;Integra GS 1.8;1992;R$ 12.109,00;Gasolina;038003-2\n", "utf-8"
    )
    df = read_v1_csv(path)
    assert df.loc[0, "codigo_fipe"] == "038003-2"
    assert (df.loc[0, "ref_year"], df.loc[0, "ref_month"]) == (2023, 1)


def test_brand_new_cars_become_a_flag_not_year_32000():
    prices, _ = clean(raw((2024, "Fiat", "Mobi", "32000", "R$ 70.000,00", "Flex", "001400-1")))
    row = prices.iloc[0]
    assert bool(row["is_new"])
    assert pd.isna(row["model_year"])


def test_fuel_is_part_of_the_key():
    prices, report = clean(
        raw(
            (2010, "VW", "Gol 1.0", "2008", "R$ 20.000,00", "Gasolina", "005004-6"),
            (2010, "VW", "Gol 1.0", "2008", "R$ 19.000,00", "Álcool", "005004-6"),
        )
    )
    assert len(prices) == 2
    assert report.duplicates_dropped == 0


def test_same_car_under_two_brands_is_kept_once():
    prices, report = clean(
        raw(
            (2021, "Baby", "Buggy 1.6 2-Lug.", "1988", "R$ 2.216,00", "Gasolina", "040001-7"),
            (2021, "Buggy", "Buggy 1.6 2-Lug.", "1988", "R$ 2.216,00", "Gasolina", "040001-7"),
        )
    )
    assert len(prices) == 1
    assert (report.duplicates_dropped, report.duplicate_conflicts) == (1, 0)


def test_collector_copy_wins_over_the_old_csv():
    both = pd.concat(
        [
            raw((2024, "Fiat", "Uno", "2010", "R$ 15.000,00", "Flex", "001200-1")),
            raw((2024, "Fiat", "Uno", "2010", "R$ 15.500,00", "Flex", "001200-1"), source="api"),
        ]
    )
    prices, report = clean(both)
    assert prices["source"].tolist() == ["api"]
    assert prices["price_brl"].tolist() == [15500.0]
    assert report.duplicate_conflicts == 1


def test_invalid_rows_are_dropped_and_counted():
    prices, report = clean(
        raw(
            (2012, "Fiat", " Palio 1.0 ", "2010", "R$ 18.000,00", "Flex", "001267-0"),
            (2012, "Fiat", "Palio 1.0", "2010", "R$ 18.000,00", "Flex", "1267"),
            (2012, "Fiat", "Palio 1.0", "2011", "consulte", "Flex", "001267-0"),
            (2012, "Fiat", "Palio 1.0", "dois mil", "R$ 18.000,00", "Flex", "001267-0"),
        )
    )
    assert (report.invalid_codigo, report.invalid_price, report.invalid_year) == (1, 1, 1)
    assert prices["model"].tolist() == ["Palio 1.0"]  # stripped


def test_read_api_cache_parses_the_reference_month(tmp_path):
    body = {
        "Valor": "R$ 51.655,00",
        "Marca": "Agrale",
        "Modelo": "MARRUÁ AM 200 2.8 CS TDI Diesel",
        "AnoModelo": 2007,
        "Combustivel": "Diesel",
        "CodigoFipe": "060007-5",
        "MesReferencia": "março de 2024 ",
    }
    client = Client(transport=lambda e, p: Response(200, json.dumps(body)), min_interval=0)
    cache = Cache(client, tmp_path / "c.sqlite")
    cache.get("ConsultarValorComTodosParametros", {"codigoModelo": "1"})
    cache.close()
    df = read_api_cache(tmp_path / "c.sqlite")
    assert (df.loc[0, "ref_year"], df.loc[0, "ref_month"], df.loc[0, "model_year_raw"]) == (2024, 3, "2007")
    assert df.loc[0, "source"] == "api"


@pytest.mark.parametrize("month", ["janeiro", "Janeiro "])
def test_month_names_are_normalized(tmp_path, month):
    path = tmp_path / "x.csv"
    path.write_text(HEADER + f"2010;{month};Fiat;Uno;2005;R$ 10.000,00;Flex;001100-1\n", "utf-8")
    assert read_v1_csv(path).loc[0, "ref_month"] == 1


def test_fuel_group_follows_a_car_across_the_2024_relabel():
    prices, report = clean(
        raw(
            (2023, "Fiat", "Argo 1.0", "2020", "R$ 60.000,00", "Gasolina", "001500-1"),
            (2024, "Fiat", "Argo 1.0", "2020", "R$ 58.000,00", "Flex", "001500-1"),
            (2024, "Fiat", "Argo 1.0", "2019", "R$ 52.000,00", "Álcool", "001500-1"),
        )
    )
    assert prices["fuel_group"].tolist() == ["gasoline", "alcohol", "gasoline"]
    assert prices.groupby(["codigo_fipe", "model_year", "fuel_group"]).size().max() == 2
    assert report.fuel_group_collisions == 0


def test_two_gasoline_labels_for_the_same_car_and_month_are_flagged():
    _, report = clean(
        raw(
            (2024, "Fiat", "Argo 1.0", "2020", "R$ 58.000,00", "Flex", "001500-1"),
            (2024, "Fiat", "Argo 1.0", "2020", "R$ 59.000,00", "Gasolina", "001500-1"),
        )
    )
    assert report.fuel_group_collisions == 2
