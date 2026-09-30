#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")"

if ! command -v python >/dev/null 2>&1; then
  pkg update -y
  pkg install python -y
fi

echo "Starting AI Hub server..."
python serve.py
