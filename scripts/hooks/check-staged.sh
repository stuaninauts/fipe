#!/usr/bin/env bash
# pre-commit: barra dado bruto da FIPE e arquivo grande no commit (docs/adr/0001).
set -euo pipefail
MAX_KB=1024
fail=0
while IFS= read -r -d '' f; do
  case "$f" in
    data/*) echo "check-staged: $f está em data/ (dado bruto da FIPE não entra no git)" >&2; fail=1; continue ;;
  esac
  [ -f "$f" ] || continue
  kb=$(( $(git cat-file -s ":$f") / 1024 ))
  if [ "$kb" -gt "$MAX_KB" ]; then
    echo "check-staged: $f tem ${kb} KB (limite ${MAX_KB} KB); dado grande não vai para o git" >&2; fail=1
  fi
done < <(git diff --cached --name-only --diff-filter=ACMR -z)
exit $fail
