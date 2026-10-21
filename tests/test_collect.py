import json

import pytest

from fipe.api import ApiError, Client, Response
from fipe.cache import Cache
from fipe.collect import collect_reference, load_known, resolve_refs

# A tiny fake of the endpoint: 2 brands, 3 models, 4 model years (one of them brand new, year 32000).
FAKE = {
    "ConsultarMarcas": [{"Label": "Acura", "Value": "1"}, {"Label": "Citroën", "Value": "13"}],
    ("ConsultarModelos", "1"): {"Modelos": [{"Label": "Integra GS 1.8", "Value": 1}], "Anos": []},
    ("ConsultarModelos", "13"): {
        "Modelos": [{"Label": "C3 1.6", "Value": 7}, {"Label": "C4 2.0", "Value": 8}],
        "Anos": [],
    },
    ("ConsultarAnoModelo", "1"): [{"Label": "1992 Gasolina", "Value": "1992-1"}],
    ("ConsultarAnoModelo", "7"): [
        {"Label": "32000 Gasolina", "Value": "32000-1"},
        {"Label": "2012 Álcool", "Value": "2012-2"},
    ],
    ("ConsultarAnoModelo", "8"): [{"Label": "2015 Gasolina", "Value": "2015-1"}],
}


class FakeApi:
    def __init__(self, broken: set[str] | None = None):
        self.calls: list[tuple[str, dict]] = []
        self.broken = broken or set()  # model codes whose price call answers 503

    def __call__(self, endpoint, params):
        self.calls.append((endpoint, dict(params)))
        if endpoint == "ConsultarMarcas":
            body = FAKE[endpoint]
        elif endpoint == "ConsultarModelos":
            body = FAKE[(endpoint, params["codigoMarca"])]
        elif endpoint == "ConsultarAnoModelo":
            body = FAKE[(endpoint, params["codigoModelo"])]
        else:
            if params["codigoModelo"] in self.broken:
                return Response(503, "")
            body = {
                "Valor": "R$ 10.000,00",
                "CodigoFipe": f"00100{params['codigoModelo']}-9",
                "AnoModelo": int(params["anoModelo"]),
            }
        return Response(200, json.dumps(body))


def make_cache(api, path=":memory:"):
    client = Client(transport=api, min_interval=0, backoff=0, sleep=lambda s: None)
    return Cache(client, path)


def price_calls(api):
    return [c for c in api.calls if c[0] == "ConsultarValorComTodosParametros"]


def test_walks_every_brand_model_and_year():
    api = FakeApi()
    stats = collect_reference(make_cache(api), ref=330)
    assert stats.prices == 4
    assert stats.failures == 0
    first = price_calls(api)[0][1]
    assert first["codigoTabelaReferencia"] == "330"
    assert first["anoModelo"] == "1992"
    assert first["codigoTipoCombustivel"] == "1"


def test_rerun_comes_from_the_cache(tmp_path):
    db = tmp_path / "cache.sqlite"
    first = FakeApi()
    collect_reference(make_cache(first, db), ref=330)
    second = FakeApi()
    stats = collect_reference(make_cache(second, db), ref=330)
    assert stats.prices == 4
    assert second.calls == []


def test_failures_are_recorded_and_retried_on_the_next_run(tmp_path):
    db = tmp_path / "cache.sqlite"
    broken = FakeApi(broken={"7"})
    cache = make_cache(broken, db)
    stats = collect_reference(cache, ref=330)
    assert (stats.prices, stats.failures) == (2, 2)
    assert cache.failure_count() == 2

    fixed = FakeApi()
    cache = make_cache(fixed, db)
    stats = collect_reference(cache, ref=330)
    assert (stats.prices, stats.failures) == (4, 0)
    assert len(price_calls(fixed)) == 2  # only the two that had failed
    assert cache.failure_count() == 0


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.sleeps: list[float] = []

    def time(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


def test_client_spaces_calls_out():
    clock = FakeClock()
    client = Client(
        transport=lambda e, p: Response(200, "[]"), min_interval=1.0, clock=clock.time, sleep=clock.sleep
    )
    for _ in range(3):
        client.post("ConsultarMarcas", {})
    assert clock.sleeps == [1.0, 1.0]


def test_client_retries_transient_errors_with_backoff():
    answers = iter([Response(503, ""), Response(429, ""), Response(200, "[]")])
    clock = FakeClock()
    client = Client(
        transport=lambda e, p: next(answers), min_interval=0, backoff=5.0, clock=clock.time, sleep=clock.sleep
    )
    assert client.post("ConsultarMarcas", {}) == "[]"
    assert client.calls == 3
    assert clock.sleeps == [5.0, 10.0]


@pytest.mark.parametrize(
    "response",
    [Response(404, "not found"), Response(200, '{"codigo": "0", "erro": "nadaencontrado"}')],
)
def test_client_gives_up_at_once_on_permanent_errors(response):
    client = Client(transport=lambda e, p: response, min_interval=0, backoff=0, sleep=lambda s: None)
    with pytest.raises(ApiError):
        client.post("ConsultarValorComTodosParametros", {})
    assert client.calls == 1


def test_resolve_refs_maps_labels_and_rejects_unknown_months():
    tables = [{"Codigo": 330, "Mes": "janeiro/2026 "}, {"Codigo": 318, "Mes": "janeiro/2025 "}]
    assert resolve_refs(tables, ["Janeiro/2025"]) == [(318, "janeiro/2025")]
    with pytest.raises(SystemExit):
        resolve_refs(tables, ["janeiro/2031"])


def write_csv(path, rows):
    header = "ano_ref;mes_ref;marca;modelo;ano_fab;valor;combustivel;codigo_fipe\n"
    path.write_text(header + "".join(";".join(r) + "\n" for r in rows), encoding="utf-8")


def test_known_csv_rows_skip_their_price_calls(tmp_path):
    csv_path = tmp_path / "janeiro2024 "  # old files end in a space
    write_csv(
        csv_path,
        [
            ("2024", "janeiro", "Citroën", "C3 1.6", "32000", "R$ 1,00", "Gasolina", "001007-9"),
            ("2024", "janeiro", "Citroën", "C3 1.6", "2012", "R$ 1,00", "Álcool", "001007-9"),
            ("2024", "janeiro", "Citroën", "C3 1.6", "2013", "R$ 1,00", "Álcool", "001007-9"),  # not offered
            (
                "2023",
                "janeiro",
                "Acura",
                "Integra GS 1.8",
                "1992",
                "R$ 1,00",
                "Gasolina",
                "038003-2",
            ),  # other month
        ],
    )
    known = load_known([csv_path], "janeiro/2024")
    assert len(known) == 3

    api = FakeApi()
    stats = collect_reference(make_cache(api), ref=305, known=known)
    assert (stats.prices, stats.known, stats.unmatched) == (2, 2, 1)
    asked = {(c[1]["codigoModelo"], c[1]["anoModelo"]) for c in price_calls(api)}
    assert asked == {("1", "1992"), ("8", "2015")}
