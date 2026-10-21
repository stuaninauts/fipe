# FIPE

Analysis of Brazilian used car prices from the FIPE price table, from 2004 onward. A Python pipeline builds
aggregate tables (price indices, depreciation curves, inflation-adjusted values) and a static site will publish
them at `fipe.stuaninauts.com`.

> 🚧 Being rebuilt. The pipeline and the site are not here yet.

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

## Development

Requires [uv](https://docs.astral.sh/uv/) (Python 3.13).

```bash
uv sync
uv run lefthook install   # git hooks: secret scan, raw-data guard, commit message format
uv run ruff check && uv run ruff format --check && uv run pytest
```

Decisions are recorded (in Portuguese) in [`docs/adr/`](docs/adr/). Contributions go through a branch and a pull
request, merged by rebase, with [Conventional Commits](https://www.conventionalcommits.org/).

## License

Code under the [MIT License](LICENSE). Source data: Tabela FIPE, © Fundação Instituto de Pesquisas Econômicas.
