#!/usr/bin/env bash
# Roda o gh com a conta dona deste repo, numa config própria (GH_CONFIG_DIR),
# independente da conta que o gh usa por padrão.
# Primeiro uso (interativo):  bash scripts/gh.sh auth login
set -euo pipefail
export GH_CONFIG_DIR="${FIPE_GH_CONFIG_DIR:-$HOME/.config/gh-stuaninauts}"
exec gh "$@"
