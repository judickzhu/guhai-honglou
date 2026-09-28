#!/bin/bash
# update.sh — 一次過:重新生成「深度精華」頁 + 全站 + 自檢 + 同步推送（含推送後複核）
# 用法: bash tools/update.sh ["commit message"]
# 流程: 改 md 源檔 → 跑本腳本 → 網站自動更新（GitHub Pages 約 1 分鐘後生效）
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
MSG="${1:-更新:標準更新流程(生成深度精華+全站+自檢)}"

echo "=== 0. 源檔檢查 ==="
SRC="analysis/深度分析报告提纯精华版.md"
[ -f "$SRC" ] && echo "  ✓ 源檔存在: $SRC ($(wc -l <"$SRC") 行)" || { echo "  ✗ 搵唔到 $SRC"; exit 1; }

echo "=== ① 生成「深度精華」頁 (build_jinghua.py) ==="
python3 tools/build_jinghua.py

echo "=== ② 全站重建 (build_honglou_site.py) ==="
python3 tools/build_honglou_site.py

echo "=== ③ 站點自檢 (selfcheck.sh) ==="
if bash tools/selfcheck.sh; then
  echo "  ✓ 自檢通過"
else
  echo "  ⚠️ 自檢有警告，繼續（可檢查後再決定）"
fi

echo "=== ④ 本地提交（記錄用） ==="
if [ -z "$(git status --porcelain)" ]; then
  echo "  本地無改動"
else
  git add -A
  git -c user.name="judickzhu" -c user.email="judickzhu@users.noreply.github.com" commit -m "$MSG" 2>&1 | tail -1
fi

echo "=== ⑤ 同步推送（GitHub API，帶重試＋推送後全站複核） ==="
# 注意：本機 git push 走唔通（HTTPS/SSH 被網絡擋），且 API 推送可能靜默失敗，
#       故一律用 sync_push.py：它會逐檔比對遠端雜湊，只推有異嘅，並在推送後複核。
python3 tools/sync_push.py "$MSG"

echo ""
echo "=== 完成 ==="
echo "線上檢查: https://judickzhu.github.io/guhai-honglou/jinghua.html"
