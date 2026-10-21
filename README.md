# FIPE

How much a car loses value in Brazil, from two decades of the FIPE price table (January 2004 to 2025), following
the same car over time and adjusting for inflation. A Python pipeline builds aggregate tables and a static,
bilingual site (PT/EN) publishes them at `fipe.stuaninauts.com`.

> 🚧 The site is not live yet.

The six analyses: what a car keeps after its first year, how much it loses at each age, how what is left depends
on the year of purchase, the 2022 used-car shock and what was left of it, what holds value (entry versions,
cheaper cars, some brands, diesel) and what the FIPE table does and does not measure. An explore page compares
brands, fuels and price bands.

## Background

The first version (2023) was the final assignment for INF01124 - Sorting and Searching Data at
[INF/UFRGS](https://www.inf.ufrgs.br/), built together with Gustavo Lacroix ([@gpl27](https://github.com/gpl27)):
a scraper, B-tree and trie indexes in C with a terminal search app, and a Shiny dashboard. That state is tagged
[`v1.0-academic`](https://github.com/stuaninauts/fipe/tree/v1.0-academic); the C code lives on, frozen, in
[`legacy/`](legacy/).

## Data

FIPE (Fundação Instituto de Pesquisas Econômicas) publishes its table without an open license. Raw prices are
collected locally and never committed; this repository and the site publish only aggregates, with attribution
([ADR 0001](docs/adr/0001-dados-brutos-locais.md)).

## How it works

| Step | Code | Output |
|---|---|---|
| Collect (rate limited, resumable) | `fipe/collect.py` | local SQLite cache in `data/raw/` |
| Clean (car identity, prices, duplicates) | `fipe/clean.py` | `data/processed/prices.parquet` (local) |
| Inflation (IBGE IPCA) | `fipe/inflation.py` | real values, `reference/ipca.csv` |
| Analyses (cohort, loss by age, what holds value) | `fipe/aggregate.py` | `web/public/data/` (aggregates only) |
| Site (Astro, charts drawn at build time) | `web/` | `fipe.stuaninauts.com` |

The export is pinned by golden tests, since CI has no raw data.

## Development

Requires [uv](https://docs.astral.sh/uv/) (Python 3.13) and, for the site, Node (version in `web/.node-version`).

```bash
uv sync
uv run lefthook install   # git hooks: secret scan, raw-data guard, commit message format
uv run ruff check && uv run ruff format --check && uv run pytest
uv run python -m fipe.pipeline && uv run python -m fipe.export   # needs the local raw data
cd web && npm ci && npm run check && npm run build
```

Decisions are recorded (in Portuguese) in [`docs/adr/`](docs/adr/). Contributions go through a branch and a pull
request, merged by rebase, with [Conventional Commits](https://www.conventionalcommits.org/).

## License

Code under the [MIT License](LICENSE). Source data: Tabela FIPE, © Fundação Instituto de Pesquisas Econômicas.
