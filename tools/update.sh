#!/bin/bash
# update.sh — 一次過:重新生成「深度精華」頁 + 全站 + 自檢 + 提交推送
# 用法: bash tools/update.sh   (或 ./tools/update.sh)
# 流程: 改 md 源檔 → 跑本腳本 → 網站自動更新（GitHub Pages 約 1 分鐘後生效）
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

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

echo "=== ④ git status ==="
git status --short

echo "=== ⑤ 提交 + 推送 ==="
if [ -z "$(git status --porcelain)" ]; then
  echo "  無改動，唔使提交"
else
  git add -A
  git -c user.name="judickzhu" -c user.email="judickzhu@users.noreply.github.com" \
    commit -m "更新:標準更新流程(生成深度精華+全站+自檢)" 2>&1 | tail -1
  git push origin main 2>&1 | tail -2
  echo "  ✓ 已推送 main"
fi

echo ""
echo "=== 完成 ==="
echo "線上檢查: https://judickzhu.github.io/guhai-honglou/jinghua.html"