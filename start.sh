#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"
echo "[start] Iniciando MasterNet Bot..."

if ! command -v nix-shell &>/dev/null; then
    echo "[ERRO] nix-shell nao encontrado. Execute manualmente:"
    echo "  pip install -r requirements.txt"
    echo "  python3 bot.py"
    exit 1
fi

exec nix-shell shell.nix --run 'python3 bot.py'
