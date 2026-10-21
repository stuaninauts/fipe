#!/usr/bin/env bash
# PreToolUse(Bash): bloqueia comandos git/rm destrutivos. É guardrail, não fronteira de segurança:
# a proteção real da main é o ruleset do GitHub. Testes: .claude/hooks/test-guard-bash.sh
set -uo pipefail
command -v jq >/dev/null || { echo "guard-bash: jq ausente, bloqueando por segurança" >&2; exit 2; }
INPUT=$(cat)
CMD=$(printf '%s' "$INPUT" | jq -r '.tool_input.command // empty')
CWD=$(printf '%s' "$INPUT" | jq -r '.cwd // empty')

block() { echo "Bloqueado por .claude/hooks/guard-bash.sh: $1. Se for intencional, o humano roda manualmente." >&2; exit 2; }
has() { printf '%s' "$CMD" | grep -Eq -- "$1"; }

# rm recursivo + forçado (-rf, -fr, -r -f, --recursive --force)
if has '(^|[;&|( ])rm[[:space:]]' && has '[[:space:]]-(-recursive|[a-zA-Z]*[rR])' && has '[[:space:]]-(-force|[a-zA-Z]*f)'; then
  block "rm recursivo forçado"
fi
has '\bgit\b.*\breset\b.*--hard' && block "git reset --hard"
has '\bgit\b.*\bclean\b.*[[:space:]]-[a-zA-Z]*f' && block "git clean -f"
has '\bgit\b.*--no-verify' && block "git --no-verify (pula o scan de segredos)"
if has '\bgit\b.*\bpush\b'; then
  has '(--force|--force-with-lease|--mirror|--delete|[[:space:]]-[a-zA-Z]*[fd]\b|[[:space:]]\+[^[:space:]]+)' && block "git push forçado/destrutivo"
  has '([[:space:]:]|refs/heads/)(main|master)([[:space:]]|$)' && block "git push para main/master (use branch + PR)"
  BRANCH=$(git -C "${CWD:-.}" rev-parse --abbrev-ref HEAD 2>/dev/null || true)
  [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]] && block "git push estando em $BRANCH (use branch + PR)"
fi
# dado bruto da FIPE nunca vai para o git (docs/adr/0001); data/ é ignorado, então só um add forçado o levaria
has '\bgit\b.*\badd\b.*[[:space:]](-f|--force)\b' && has '(^|[[:space:]/])data/' && block "git add -f em data/ (dado bruto da FIPE não entra no git)"
# gh direto usaria a conta padrão do gh, que pode não ser a dona deste repo; aqui só via scripts/gh.sh
has '(^|[;&|(][[:space:]]*|[[:space:]]&&[[:space:]]*)gh[[:space:]]' && block "gh direto (use bash scripts/gh.sh, que usa a conta dona do repo)"
# deploy manual pula CI e revisão: produção só sai do merge na main (Workers Builds)
has '\bwrangler\b.*\bdeploy\b' && block "wrangler deploy manual (o deploy sai do merge na main)"
exit 0
