#!/bin/bash
cd "$(dirname "$0")/.."

PYTHON_BIN=".venv/bin/python3"
if [ -x "$PYTHON_BIN" ]; then
  PYTHON="$PYTHON_BIN"
else
  PYTHON="python3"
fi

# If no arguments or --help, run without sudo
if [ $# -eq 0 ] || [[ "$1" == "--help" ]]; then
  PYTHONPATH=src $PYTHON -m installer.install "$@"
else
  sudo PYTHONPATH=src $PYTHON -m installer.install "$@"
fi
