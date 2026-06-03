#!/usr/bin/env bash
# Install cheat via pipx.
set -e

echo "Installing cheat via pipx..."
pipx install "$(dirname "$0")"

echo "Done. Usage: cheat            (uses default data dir)"
echo "            cheat --dir DIR   (override the cheatsheet directory)"
echo "            CHEAT_DIR=DIR cheat"
