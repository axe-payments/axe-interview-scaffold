#!/usr/bin/env bash
#
# OPTIONAL — only powers your editor (Cursor/VSCode) autocomplete, auto-import, and linting.
# The app itself runs in Docker; you do NOT need this to do the exercise.
#
# Creates a local .venv with the app + dev dependencies. The .vscode settings already point
# at ./.venv/bin/python, so once this finishes the editor should resolve imports.
#
# Needs Python 3.12 on your machine. Prefer zero local installs? Use the dev container
# instead: "Dev Containers: Reopen in Container" (see .devcontainer/).
#
#   ./scripts/setup_venv.sh
#   # then in Cursor/VSCode: "Python: Select Interpreter" -> ./.venv/bin/python

set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-python3}"

echo "Creating .venv with $PYTHON ..."
"$PYTHON" -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements-dev.txt

echo
echo "Done. In Cursor/VSCode run 'Python: Select Interpreter' and pick ./.venv/bin/python"
echo "(settings already default to it). Reload the window if imports don't resolve yet."
