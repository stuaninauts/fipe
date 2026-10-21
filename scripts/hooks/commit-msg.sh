#!/usr/bin/env bash
# commit-msg: assunto em Conventional Commits, minúsculo, até 72 caracteres, sem ponto final e sem travessão longo.
set -uo pipefail
SUBJECT=$(grep -v '^#' "$1" | sed -n '/./{p;q}')
grep -qE '^(Merge |Revert "|fixup! |squash! |amend! )' <<<"$SUBJECT" && exit 0
TYPES='feat|fix|docs|test|refactor|perf|chore|build|ci|style|revert'
fail() { printf 'commit-msg: %s\n  esperado: <tipo>(<escopo>): <descrição em minúscula>  tipos: %s\n  recebido: %s\n' "$1" "${TYPES//|/, }" "$SUBJECT" >&2; exit 1; }
grep -qE "^(${TYPES})(\([a-z0-9-]+\))?!?: [a-z0-9]" <<<"$SUBJECT" || fail "assunto fora do Conventional Commits"
[ "${#SUBJECT}" -le 72 ] || fail "assunto com mais de 72 caracteres"
grep -qE '\.$' <<<"$SUBJECT" && fail "assunto termina com ponto"
grep -q $'—' "$1" && fail "mensagem com travessão longo (em dash)"
exit 0
