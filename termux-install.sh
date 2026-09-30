#!/data/data/com.termux/files/usr/bin/bash
set -e

REPO="https://github.com/mrshadowsir/AI-Tools-Hub.git"
DIR="$HOME/AI-Tools-Hub"

echo "== Open-Source AI Hub | Termux =="
echo "[1/4] Updating Termux packages..."
pkg update -y
pkg upgrade -y

echo "[2/4] Installing Git + Python..."
pkg install -y git python

echo "[3/4] Getting AI Hub..."
if [ -d "$DIR/.git" ]; then
  git -C "$DIR" pull --ff-only
else
  rm -rf "$DIR"
  git clone "$REPO" "$DIR"
fi

echo "[4/4] Starting browser server..."
cd "$DIR"
chmod +x start-termux.sh
bash start-termux.sh
