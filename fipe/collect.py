"""Collect car prices for whole reference months into the local cache.

    uv run python -m fipe.collect --list                       # reference months the endpoint offers
    uv run python -m fipe.collect janeiro/2024 janeiro/2025    # walk brands, models, years and prices

Only run with an explicit request from the author (CLAUDE.md). Safe to stop and rerun: answered calls come
from the cache, so a rerun only asks for what is still missing (including calls that failed before).
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from fipe.api import CAR, ApiError, Client
from fipe.cache import DEFAULT_PATH, Cache

log = logging.getLogger("fipe.collect")


@dataclass
class Stats:
    prices: int = 0
    failures: int = 0


def reference_tables(client: Client) -> list[dict]:
    """Every reference month, newest first: [{"Codigo": 293, "Mes": "janeiro/2023 "}, ...].

    Not cached: the list grows every month.
    """
    return json.loads(client.post("ConsultarTabelaDeReferencia", {}))


def resolve_refs(tables: list[dict], wanted: list[str]) -> list[tuple[int, str]]:
    """Map labels like "janeiro/2024" to reference codes. Unknown labels are an error, not a skip."""
    by_label = {t["Mes"].strip().lower(): int(t["Codigo"]) for t in tables}
    missing = [w for w in wanted if w.strip().lower() not in by_label]
    if missing:
        raise SystemExit(f"reference month not offered by the endpoint: {', '.join(missing)}")
    return [(by_label[w.strip().lower()], w.strip().lower()) for w in wanted]


def collect_reference(cache: Cache, ref: int, progress_every: int = 500) -> Stats:
    """Walk brands, models and model years of one reference month, fetching every price."""
    stats = Stats()
    base = {"codigoTabelaReferencia": str(ref), "codigoTipoVeiculo": str(CAR)}

    def fetch(endpoint: str, params: dict[str, str]):
        try:
            return cache.get_json(endpoint, params)
        except ApiError as err:
            stats.failures += 1
            log.warning("%s", err)
            return None

    brands = fetch("ConsultarMarcas", base) or []
    for brand in brands:
        brand_params = {**base, "codigoMarca": str(brand["Value"])}
        models = (fetch("ConsultarModelos", brand_params) or {}).get("Modelos", [])
        for model in models:
            model_params = {**brand_params, "codigoModelo": str(model["Value"])}
            years = fetch("ConsultarAnoModelo", model_params) or []
            for year in years:
                model_year, fuel = str(year["Value"]).split("-")
                price_params = {
                    **model_params,
                    "anoModelo": model_year,
                    "codigoTipoCombustivel": fuel,
                    "tipoVeiculo": "carro",
                    "modeloCodigoExterno": "",
                    "tipoConsulta": "tradicional",
                }
                if fetch("ConsultarValorComTodosParametros", price_params) is not None:
                    stats.prices += 1
                    if stats.prices % progress_every == 0:
                        log.info(
                            "ref %s: %d prices (%d API calls, %d from cache, %d failures)",
                            ref,
                            stats.prices,
                            cache.client.calls,
                            cache.hits,
                            stats.failures,
                        )
    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("months", nargs="*", help='reference months, e.g. "janeiro/2024"')
    parser.add_argument("--list", action="store_true", help="list the reference months and exit")
    parser.add_argument("--db", type=Path, default=DEFAULT_PATH, help=f"cache file (default: {DEFAULT_PATH})")
    parser.add_argument("--min-interval", type=float, default=1.0, help="seconds between calls (default: 1)")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", stream=sys.stderr)

    client = Client(min_interval=args.min_interval)
    tables = reference_tables(client)
    if args.list or not args.months:
        for t in tables:
            print(f"{t['Codigo']}\t{t['Mes'].strip()}")
        return 0

    cache = Cache(client, args.db)
    started = time.monotonic()
    total = Stats()
    try:
        for ref, label in resolve_refs(tables, args.months):
            log.info("collecting %s (ref %d)", label, ref)
            stats = collect_reference(cache, ref)
            total.prices += stats.prices
            total.failures += stats.failures
            log.info("done %s: %d prices, %d failures", label, stats.prices, stats.failures)
    finally:
        log.info(
            "finished in %.0f min: %d prices, %d API calls, %d from cache, %d failures pending in the cache",
            (time.monotonic() - started) / 60,
            total.prices,
            client.calls,
            cache.hits,
            cache.failure_count(),
        )
        cache.close()
    return 1 if total.failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
