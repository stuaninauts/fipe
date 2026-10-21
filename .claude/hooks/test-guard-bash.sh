#!/usr/bin/env bash
# Roda casos contra guard-bash.sh: bash .claude/hooks/test-guard-bash.sh
set -u
HOOK="$(dirname "$0")/guard-bash.sh"; fail=0
check() { # $1 = esperado (block|allow), $2 = comando
  local code; jq -n --arg c "$2" --arg d "$PWD" '{tool_name:"Bash",tool_input:{command:$c},cwd:$d}' | "$HOOK" 2>/dev/null; code=$?
  local got=allow; [[ $code -eq 2 ]] && got=block
  [[ $got == "$1" ]] && echo "ok    $1  $2" || { echo "FALHA esperado=$1 obtido=$got  $2"; fail=1; }
}
check block 'rm -rf dist'
check block 'rm -r -f dist'
check block 'cd x && rm -fr y'
check block 'git reset --hard HEAD~1'
check block 'git clean -fd'
check block 'git push origin main'
check block 'git -C . push origin main'
check block 'git push origin HEAD:main'
check block 'git push -f origin feat/x'
check block 'git push --force-with-lease'
check block 'git push origin +feat/x'
check block 'git push --delete origin feat/x'
check block 'git commit --no-verify -m x'
check block 'npx wrangler deploy'
check block 'gh pr create --title x'
check block 'cd site && gh pr merge 3'
check block 'git add -f data/raw/janeiro-2024.csv'
check block 'git add --force data/processed/prices.parquet'
check allow 'bash scripts/gh.sh pr create --title x'
check allow 'git push -u origin feat/x'
check allow 'git push origin feat/main-page'
check allow 'rm dist/file.txt'
check allow 'uv run pytest'
check allow 'git add fipe/clean.py tests/test_clean.py'
check allow 'git add -f docs/adr/0001-dados.md'
check allow 'git commit -m "feat: x"'
check allow 'npx wrangler whoami'
exit $fail
