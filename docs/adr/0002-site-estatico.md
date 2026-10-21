# Site estático em fipe.stuaninauts.com, no padrão do CopaData

Data: 2026-10-16.

A versão hospedada da v1 era um app Shiny for Python num EC2, desativado. Para portfólio de longa duração, servidor
que morre leva a demo junto. O CopaData (copa.stuaninauts.com) já resolveu o mesmo problema com site estático.

Decidimos:

- **Pipeline Python gera um export versionado de agregados** ([ADR 0001](./0001-dados-brutos-locais.md)), e um site
  Astro estático lê esse export no build.
- **Gráficos em SVG no build** (Observable Plot), sem JavaScript no navegador para calcular número. Interação, se
  entrar, é ilha pequena que só filtra o que já veio no HTML.
- **CSP estrita**, igual à do CopaData: `script-src 'self'` com hashes, sem `wasm-unsafe-eval`, sem CDN externa.
- **Hospedagem:** Cloudflare Workers com static assets, deploy por Workers Builds a cada merge na `main`, preview por
  branch, custom domain `fipe.stuaninauts.com`. Custo zero no plano free.
- **Idiomas:** PT na raiz e EN em `/en/`.

## Considered Options

- **Servidor Shiny hospedado:** reaproveita o app antigo, mas exige servidor pago ou que dorme. Rejeitada.
- **Shinylive (Pyodide):** dezenas de MB antes do primeiro gráfico, service worker e CSP afrouxada. Rejeitada.
- **DuckDB-WASM sobre Parquet:** filtros livres no navegador, mas ~2,5 MB de WASM, `wasm-unsafe-eval` e números
  calculados em JS. Rejeitada para o MVP.

## Consequences

- O ranking com filtros livres da v1 não volta como era: vira páginas pré-calculadas (por marca, por recorte).
- O repositório terá Python e Node (`web/`), e o CI cobre os dois.
- Merge na `main` publica o site, então segue a regra de horário de qualquer ação no GitHub.
