---
name: pr
description: Open (or update) the pull request for the current branch against main, with a test gate first and an evidence-based description following .github/pull_request_template.md. Use when the user asks to open, create or update a PR.
argument-hint: "[--draft] [context, e.g. issue number or what to highlight]"
disable-model-invocation: true
allowed-tools: Bash(git status *) Bash(git log *) Bash(git diff *) Bash(git branch *) Bash(git fetch *) Bash(uv run ruff *) Bash(uv run pytest *) Bash(bash .claude/hooks/test-guard-bash.sh) Bash(bash scripts/gh.sh auth status *) Bash(bash scripts/gh.sh pr list *) Bash(bash scripts/gh.sh pr view *) Bash(bash scripts/gh.sh pr create *) Bash(bash scripts/gh.sh api -X PATCH 'repos/{owner}/{repo}/pulls/*)
---

# Pull Request com gate de testes

Abre um PR da branch atual para `main` (quando o site existir, o merge dispara o deploy) ou atualiza o PR que já existe.
Argumentos: `$ARGUMENTS` (`--draft` abre como rascunho; o resto é contexto extra do autor).

## Estado atual

- Branch: !`git branch --show-current`
- Working tree:

!`git status --short`

- Commits em relação a `origin/main`:

!`git log --format='%h %s' origin/main..HEAD`

---

## 1. Validação inicial

Pare com a mensagem indicada se:
- a branch é `main` → `❌ Você está na main. Crie uma branch tipo/descricao.`
- há mudanças não commitadas → `❌ Há mudanças não commitadas. Faça commit antes de abrir o PR.`
- não há commits à frente de `origin/main` → `❌ Nada para abrir: a branch não tem commits novos.`
- o nome não segue `tipo/descricao` (feat, fix, chore, docs, refactor, ci) → avise e pergunte se segue mesmo assim.

Conta do GitHub: rode `bash scripts/gh.sh auth status`. Use **sempre** `bash scripts/gh.sh`, nunca `gh` direto
(o `gh` direto usa a conta padrão, que pode não ser a dona do repo; o hook bloqueia). Se não estiver logado, pare:
> ❌ gh sem login na conta do repo. Rode uma vez: `! bash scripts/gh.sh auth login` (GitHub.com, SSH, login pelo navegador).

## 2. Sincronizar

```bash
git fetch origin main
git diff --stat origin/main...HEAD
```

Leia o diff (`git diff origin/main...HEAD`), não só os títulos dos commits.

## 3. Gate de testes (sempre)

Informe `▶ Rodando o gate…` e guarde o resultado real de cada item:
- `uv run ruff check`, `uv run ruff format --check` e `uv run pytest` (anote testes passados, erros e avisos).
- Nenhum dado bruto da FIPE no diff: `git diff --stat origin/main...HEAD -- data/` tem que sair vazio (docs/adr/0001).
- Mudou `.claude/hooks/`: `bash .claude/hooks/test-guard-bash.sh` (anote "N/N ok").
- Mudou o site (`web/`, quando existir): `npm run check && npm run build` dentro de `web/`, CSP conferida no `dist/` e
  `npm run preview` em PT/EN, tema claro/escuro, desktop/mobile.

Se algo falhar, pare: `❌ Gate falhou: <item>. PR cancelado.` e mostre o erro.

## 4. Push

```bash
git push -u origin <branch>
```

## 5. Descrição

Preencha `.github/pull_request_template.md` seção por seção:
- **Título:** Conventional Commits, `tipo(escopo opcional): resumo`, imperativo, até 72 caracteres.
- **Summary:** o resultado (para quem usa o site ou para quem roda o pipeline), em 1 a 3 frases.
- **Type of change:** só o que se aplica, com `[x]`; apague o resto.
- **Changes:** bullets factuais por área.
- **How has this been tested:** só o que rodou no passo 3, com o resultado. O que não rodou vai em "Not tested".
- **Verification:** onde foi validado. Mudança só de pipeline: o que rodou localmente. Mudança no site sem homologação: "Pending: validate on the Workers Builds preview URL".
- **Risk and rollback:** risco honesto com o motivo; rollback concreto.
- **Checklist:** `[x]` só no que foi verificado de fato.
- Remova comentários `<!-- -->` e seções que não se aplicam. Inglês, tom objetivo, **sem travessão longo (em dash)**.
- Termine com `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.

Salve o corpo num arquivo temporário (fora do repo).

## 6. Criar ou atualizar o PR

```bash
bash scripts/gh.sh pr list --head <branch> --state open --json number,url
```

- Já existe: atualize pela API REST (o `gh pr edit` do gh 2.4 falha por consultar o Projects classic, descontinuado):
  `bash scripts/gh.sh api -X PATCH 'repos/{owner}/{repo}/pulls/<número>' -f title="<título>" -F body=@<arquivo>`
- Não existe: `bash scripts/gh.sh pr create --base main --head <branch> --title "<título>" --body-file <arquivo>` (+ `--draft` se pedido)

## 7. Resultado final

```
✅ PR CRIADO (ou ✅ PR ATUALIZADO)
  Branch : <branch> → main
  Gate   : ruff ✅ · pytest ✅ (<N> testes) [· hook N/N ✅]
  URL    : <url>
```

## Notas

- **Não fazer merge.** O PR espera o CI verde (check `build`) e o preview do Workers Builds.
- Merge na `main` = deploy em produção. Só com pedido explícito do autor.
- Nunca force push.
