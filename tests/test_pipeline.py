import json

import pandas as pd

from fipe.api import Client, Response
from fipe.cache import Cache
from fipe.pipeline import build, coverage

HEADER = "ano_ref;mes_ref;marca;modelo;ano_fab;valor;combustivel;codigo_fipe\n"


def test_build_joins_csvs_and_cache_and_deflates(tmp_path):
    raw = tmp_path / "raw"
    (raw / "janeiros-2004-2023").mkdir(parents=True)
    (raw / "janeiros-2024-2025").mkdir()
    (raw / "janeiros-2004-2023" / "janeiro-2023 ").write_text(
        HEADER + "2023;janeiro;Fiat;Uno 1.0;2010;R$ 15.000,00;Flex;001200-1\n", "utf-8"
    )
    (raw / "janeiros-2024-2025" / "janeiro-2024.csv").write_text(
        HEADER + "2024;janeiro;Fiat;Uno 1.0;2010;R$ 15.900,00;Flex;001200-1\n"
        "2024;janeiro;Fiat;Mobi 1.0;32000;R$ 70.000,00;Flex;001400-1\n",
        "utf-8",
    )
    body = {
        "Valor": "R$ 15.900,00",
        "Marca": "Fiat",
        "Modelo": "Uno 1.0",
        "AnoModelo": 2010,
        "Combustivel": "Flex",
        "CodigoFipe": "001200-1",
        "MesReferencia": "janeiro de 2024 ",
    }
    cache = Cache(
        Client(transport=lambda e, p: Response(200, json.dumps(body)), min_interval=0),
        raw / "fipe_api.sqlite",
    )
    cache.get("ConsultarValorComTodosParametros", {"codigoModelo": "1"})
    cache.close()
    ipca = tmp_path / "ipca.csv"
    ipca.write_text("year,month,ipca_index\n2023,1,100\n2024,1,106\n", "utf-8")

    prices, report = build(raw, ipca)

    assert report["rows_in"] == 4
    assert report["duplicates_dropped"] == 1  # the 2024 Uno is in both the CSV and the cache
    uno = prices[prices["model"] == "Uno 1.0"].set_index("ref_year")
    assert uno.loc[2024, "source"] == "api"
    assert uno.loc[2023, "price_real_brl"] == 15900.0  # 15,000 * 106/100
    cov = coverage(prices).set_index("ref_year")
    assert cov.loc[2024, "prices"] == 2
    assert cov.loc[2024, "new_car_prices"] == 1
    assert isinstance(prices, pd.DataFrame)
