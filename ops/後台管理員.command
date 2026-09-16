#!/bin/bash
# 後台管理員啟動器（macOS 雙擊即用）
cd "$(dirname "$0")"
PORT=8701
# 已在跑就直接開瀏覽器
if curl -s -o /dev/null http://127.0.0.1:$PORT/ 2>/dev/null; then
  open "http://127.0.0.1:$PORT"
  echo "後台已在運行：http://127.0.0.1:$PORT"
else
  echo "後台管理員啟動中…"
  nohup python3 网站/tools/admin_server.py $PORT >/tmp/admin_server.log 2>&1 &
  sleep 2
  open "http://127.0.0.1:$PORT"
  echo "已啟動：http://127.0.0.1:$PORT"
  echo "（關閉請：pkill -f admin_server）"
fi
echo ""
echo "按 Enter 關閉此視窗…"
read -r
