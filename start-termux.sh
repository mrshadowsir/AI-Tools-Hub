#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")"

echo ""
echo "🆓 Open-Source AI Hub"
echo "Starting server..."
echo ""

python serve.py &
SERVER_PID=$!

sleep 2

URL="http://127.0.0.1:8000/"
echo "Open in browser: $URL"

if command -v termux-open-url >/dev/null 2>&1; then
  termux-open-url "$URL" >/dev/null 2>&1 || true
fi

echo ""
echo "Server PID: $SERVER_PID"
echo "Stop: Ctrl+C"
wait "$SERVER_PID"
