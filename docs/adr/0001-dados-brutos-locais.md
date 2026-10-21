# Dados brutos da FIPE ficam só locais; o repositório publica agregados

Data: 2026-10-16.

A Tabela FIPE é publicada pela Fundação Instituto de Pesquisas Econômicas sem licença aberta ("todos os direitos
reservados"). Até a v1 (tag `v1.0-academic`) o repositório público versionava a base inteira raspada (os CSVs de
janeiro de 2004 a 2023, o `database.csv` e os binários de índice gerados a partir dela), sob MIT. Isso redistribuía
a base, não só o código.

Decidimos:

- **Bruto só na máquina do autor.** A coleta grava em `data/raw/`, ignorado pelo git. Não há cópia em repositório
  privado nem em bucket.
- **Repositório e site publicam agregados.** Índices, medianas, curvas e contagens por recorte, com atribuição
  "Fonte: Tabela FIPE (Fundação Instituto de Pesquisas Econômicas)". Nada que reconstitua a tabela, como preço por
  modelo e ano em arquivo para download.
- **Histórico limpo.** O histórico do git foi reescrito uma vez (git filter-repo) para tirar os dados, os binários
  de índice, executáveis compilados e um notebook com placas reais. Autores e datas foram preservados; os hashes
  mudaram. O backup do histórico original fica só local.
- **Guardas automáticas:** `.gitignore` em `data/`, o hook `scripts/hooks/check-staged.sh` (pre-commit) recusa
  arquivo em `data/` ou acima de 1 MB, e o guard do Claude Code bloqueia `git add -f` em `data/`.

## Considered Options

- **Manter o bruto no git público:** simples e reprodutível por qualquer pessoa, mas redistribui uma base sem
  licença aberta. Rejeitada.
- **Bruto em repositório privado ou bucket R2:** permitiria CI reprocessando do zero e coleta agendada na nuvem.
  Fica como evolução se a coleta mensal automática entrar; por ora, só local.
- **Manter o histórico antigo e só parar de versionar:** sem force push, mas a base continuaria acessível nos
  commits antigos e o clone seguiria com dezenas de MB. Rejeitada.

## Consequences

- O CI não reprocessa a partir do bruto: testa o código com fixtures pequenas e sintéticas, e confere o export
  versionado.
- Reproduzir do zero exige rodar a coleta, que é lenta por respeito à API (limite de taxa).
- Quem tinha clone antigo precisa clonar de novo.
