#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
  exec python3 serve.py
elif command -v python >/dev/null 2>&1; then
  exec python serve.py
else
  echo "Python 3 is not installed."
  echo "Install Python 3, then run: bash start.sh"
  exit 1
fi
