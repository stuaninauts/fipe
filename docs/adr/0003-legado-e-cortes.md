# Código da disciplina vira legado; busca por placa e Shiny saem

Data: 2026-10-16.

A v1 foi o trabalho final de INF01124 (UFRGS), em dupla com Gustavo Lacroix (@gpl27): scraper em Node, índices em C
(B-tree e trie) com app de busca em terminal, e dashboard Shiny com busca por placa. A revisão de 2026 achou o C
corrompendo memória com UTF-8, a busca por placa morta (o site de terceiro responde 403 com captcha) e o Shiny
quebrando com as versões atuais.

Decidimos:

- **C congelado em `legacy/`**, com README explicando o que era o trabalho da disciplina. Fica fora do pipeline, do
  site e do CI de produção; não recebe correção de funcionalidade.
- **Busca por placa removida.** Dependia de scraping de site de terceiro e envolve dado pessoal (placa).
- **Dashboard Shiny aposentado**, substituído pelo site estático ([ADR 0002](./0002-site-estatico.md)).
- **Scraper Node substituído** por um coletor Python no pipeline, retomável e com limite de taxa.
- **Crédito:** README e site dizem que a versão original é em dupla com @gpl27. A tag `v1.0-academic` marca o estado
  entregue na disciplina.

## Consequences

- Quem quiser ver o trabalho original tem a tag e a pasta `legacy/`.
- Nenhum código novo depende do C nem do Shiny.
