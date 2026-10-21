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
- Um carro é `(codigo_fipe, model_year, fuel)`. Um preço é esse carro numa referência `(ref_year, ref_month)`.
  Nome + ano não identifica carro (mistura gasolina e álcool).
- `codigo_fipe` é texto com zeros à esquerda (`"001004-9"`), nunca número.
- O ano 32000 da API significa zero km: vira `is_new = True`, e 32000 nunca chega a uma conta ou a um gráfico.
- Preço vem como `"R$ 1.234,56"` e vira número em reais; valores são nominais até passarem pela correção do IPCA,
  e a coluna diz qual é qual.

## Coleta na API da FIPE
- Endpoint não documentado (`veiculos.fipe.org.br/api/veiculos/...`): não chamar de "API oficial".
- Só rodar coleta com pedido explícito do autor. Sempre com limite de taxa, retomável e com cache do bruto em
  `data/raw/`; nunca coleta em paralelo agressiva nem dentro de teste ou CI.

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
- Python 3.13 pelo uv (`requires-python` no `pyproject.toml`; sem `.python-version`, que quebraria o pyenv): `uv sync`, `uv run pytest`, `uv run ruff check`,
  `uv run ruff format`.
- Antes de qualquer PR: `uv run ruff check && uv run ruff format --check && uv run pytest` precisam passar.

## Escrita
- Nunca use o travessão longo (em dash) em textos, comentários, docs ou commits. Use vírgula, dois-pontos,
  parênteses ou ponto.
