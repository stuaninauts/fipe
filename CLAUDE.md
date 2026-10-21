# FIPE

Análise dos preços de carros da Tabela FIPE (2004 em diante), feita para ir ao ar em `fipe.stuaninauts.com`.
Repositório público: tudo aqui é lido por qualquer pessoa.

Começou em 2023 como trabalho final de INF01124 (Classificação e Pesquisa de Dados, UFRGS), em dupla com
Gustavo Lacroix (@gpl27): scraper, índices em C (B-tree e trie) e dashboard em Shiny. A versão nova reaproveita
os dados e refaz o resto no padrão do CopaData. A tag `v1.0-academic` marca a versão da disciplina.

## Decisões que valem para todo código (detalhes em `docs/adr/`)
- **Dados brutos da FIPE nunca entram no git.** A FIPE não dá licença aberta. O bruto fica só na máquina do autor
  (`data/raw/`, ignorado pelo git) e o repositório publica apenas agregados, com atribuição. Nada de CSV, JSON ou
  Parquet com preço por modelo versionado.
- **Site estático:** pipeline Python gera os agregados; o site Astro lê o export no build e desenha os gráficos em
  SVG. Sem servidor, sem JS para calcular número, CSP estrita. Deploy em Cloudflare Workers (Workers Builds).
- **Sem busca por placa.** Dependia de scraping de site de terceiro e envolve dado pessoal.
- **Código em C é legado:** fica congelado em `legacy/`, documentado, fora do pipeline e do site.
- **Idiomas:** PT na raiz do site e EN em `/en/`. Código, nomes de colunas e docstrings em inglês; docs e ADRs
  em português.
- **Crédito:** a versão original é em dupla com @gpl27; README e site dizem isso.

## Identidade de um preço (fonte comum dos bugs da versão antiga)
- Um preço é único em `(ref_year, ref_month, codigo_fipe, is_new, model_year, fuel)`. Para seguir um carro entre
  meses, use `CAR = (codigo_fipe, is_new, model_year, fuel_group)` de `fipe/clean.py`: em jan/2024 a FIPE trocou o
  rótulo "Gasolina" por Flex, Híbrido, Elétrico e Gás Natural nos mesmos carros, e `fuel_group` (álcool, diesel,
  gasolina) atravessa essa troca. Nome + ano não identifica carro (mistura gasolina e álcool).
- `codigo_fipe` é texto com zeros à esquerda (`"001004-9"`), nunca número.
- O ano 32000 da API significa zero km: vira `is_new = True`, e 32000 nunca chega a uma conta ou a um gráfico.
- Preço vem como `"R$ 1.234,56"` e vira número em reais; valores são nominais até passarem pela correção do IPCA,
  e a coluna diz qual é qual.

## Coleta na API da FIPE
- Endpoint não documentado (`veiculos.fipe.org.br/api/veiculos/...`): não chamar de "API oficial".
- Só rodar coleta com pedido explícito do autor. Sempre com limite de taxa, retomável e com cache do bruto em
  `data/raw/`; nunca coleta em paralelo agressiva nem dentro de teste ou CI.
- Coletor: `fipe/collect.py` (cliente em `fipe/api.py`, cache SQLite em `fipe/cache.py`, em
  `data/raw/fipe_api.sqlite`). `uv run python -m fipe.collect --list` lista os meses de referência;
  `uv run python -m fipe.collect janeiro/2024` coleta um mês inteiro (1 chamada por segundo por padrão). Rodar de
  novo só pede o que falta, inclusive o que falhou. Testes usam transporte falso, nunca a rede.
- `--known <csv>` pula os preços que já estão num CSV do scraper v1 (casa marca, modelo, ano e combustível pelos
  rótulos da API) e conta as linhas do CSV que não casaram com nada.

## Pipeline
- `uv run python -m fipe.pipeline` lê tudo em `data/raw/` (CSVs do v1 em `janeiros-*/` e o cache do coletor),
  limpa (`fipe/clean.py`), corrige pela inflação (`fipe/inflation.py`) e grava `data/processed/prices.parquet` e
  `coverage.csv` (locais, não versionados).
- `fipe/clean.py` é o único lugar que define a identidade de um preço e a validação; mudou regra, muda teste em
  `tests/test_clean.py`. Onde a coleta e o CSV têm o mesmo preço, vale o da coleta.
- IPCA: `reference/ipca.csv` é versionado (IBGE, uso livre com citação); atualizar com
  `uv run python -m fipe.inflation --update`. `price_real_brl` está em reais do último mês da série
  ([ADR 0004](docs/adr/0004-valores-reais-ipca.md)); mês de referência sem IPCA é erro, nunca NaN silencioso.

## Análises e export ([ADR 0005](docs/adr/0005-analises-e-export.md))
- `fipe/aggregate.py` é o **único** lugar que define um número publicado: só janeiros, mediana com p25/p75 e
  sempre o `n`. Para seguir um carro entre anos, use `CAR`.
- `uv run python -m fipe.export` regrava `web/public/data/` (JSON, CSV e `manifest.json`) a partir de
  `data/processed/prices.parquet`; `--check` confere se o versionado está em dia. Nunca editar esses arquivos à mão.
- O export só tem agregados: nenhuma coluna com código FIPE, modelo ou preço de um carro (`tests/test_export.py`).
- O CI não tem os dados brutos: `tests/test_export.py` fixa os números publicados. Mudou um número, mude o teste e
  o texto do site no mesmo PR.

## Site (`web/`, [ADR 0002](docs/adr/0002-site-estatico.md))
- Astro estático, PT na raiz e EN em `/en/`; rotas e textos de interface em `web/src/i18n/ui.ts`, uma view por
  página em `web/src/views/` (textos da página nos dois idiomas, lado a lado).
- Número no texto sempre vem do export (`web/src/lib/data.ts`): nunca digitar um número, nunca calcular taxa em
  JavaScript (só selecionar linha, mínimo, máximo e formatar). Linha que não existe quebra o build.
- Gráficos: SVG do Observable Plot no build (`web/src/lib/charts.ts`), em duas larguras (desktop e celular). O
  `<style>` que o Plot gera é removido; as regras ficam em `global.css`. Cores das séries validadas com o checador
  de paleta; séries sempre com rótulo direto e tabela.
- Explorar: única página com JS (`web/src/scripts/explore.ts`), que lê `/data/explore_*.json` e usa a mesma lógica
  do build (`web/src/lib/explore.ts`). Estado na URL; pontos com n < 30 ficam fora das linhas.
- Node da `web/.node-version`: `npm run check && npm run build` em `web/`; a CSP só existe no build, valide com
  `npm run preview`. Deploy por Workers Builds (root `web/`) no merge na `main`; nunca `wrangler deploy` manual.

## Git (GitHub Flow)
- Nunca commitar nem dar push na `main`. Branch `<tipo>/<descricao-kebab>` → PR → CI verde → "Rebase and merge".
- Commit, push e PR só quando o autor pedir: ele define os marcos. Ao terminar uma etapa, deixe as mudanças no
  working tree, liste os arquivos e sugira a mensagem.
- Commits em Conventional Commits, assunto em minúscula e até 72 caracteres (o hook `commit-msg` confere).
- PRs: skill `/pr` (gate de testes, push e PR pelo terminal, com `.github/pull_request_template.md` preenchido só
  com o que foi testado de fato).
- GitHub CLI: sempre `bash scripts/gh.sh ...` (conta dona do repo, config isolada). `gh` direto é bloqueado.
- `.claude/hooks/guard-bash.sh` bloqueia push na main, force push, `reset --hard`, `rm -rf`, `--no-verify`,
  `git add -f` em `data/`, deploy manual e `gh` direto. Testes: `bash .claude/hooks/test-guard-bash.sh`.
- Hooks locais pelo lefthook (`uv sync && uv run lefthook install` uma vez por clone): gitleaks no pre-commit, bloqueio de dado bruto
  e de arquivo grande, e formato da mensagem. Se o gitleaks apontar algo, não contorne: remova e avise o humano.

## Comandos
- Python 3.13 pelo uv (`requires-python` no `pyproject.toml`; sem `.python-version`, que quebraria o pyenv):
  `uv sync`, `uv run pytest`, `uv run ruff check`, `uv run ruff format`.
- Antes de qualquer PR: `uv run ruff check && uv run ruff format --check && uv run pytest` precisam passar.

## Escrita
- Nunca use o travessão longo (em dash) em textos, comentários, docs ou commits. Use vírgula, dois-pontos,
  parênteses ou ponto.
