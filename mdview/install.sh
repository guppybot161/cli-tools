#!/usr/bin/env bash
# Install mdview via pipx and drop the stylesheet into ~/.config/mdview/
set -e

echo "[1/2] Installing mdview via pipx..."
pipx install "$(dirname "$0")"

echo "[2/2] Installing stylesheet..."
mkdir -p ~/.config/mdview
cp "$(dirname "$0")/style.css" ~/.config/mdview/style.css

echo "Done. Usage: mdview <file.md>  |  mdview --pdf <file.md>"
