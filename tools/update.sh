#!/bin/bash
# update.sh — 一鍵迭代：全生成器重建 → 自檢 → 提交 → 推送
# 用法: bash tools/update.sh ["commit message"]
# 流程: 改源檔（content-source/*.json、analysis/*.md、build_*.py）→ 跑本腳本 → 全站同步上線
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
MSG="${1:-更新:全站重建+自檢+推送}"

echo "=== ① 全生成器（四個；漏跑會令該頁過時）==="
python3 tools/build_honglou_site.py    # 主站：首頁/框架/人物/映射/脂批/世系/問答/留言/字考/卡/目錄/檢索/sitemap
python3 tools/build_jilu.py            # 記錄欄（索引，源檔 analysis/）
python3 tools/build_jinghua.py         # 深度精華（源檔 analysis/深度分析报告提纯精华版.md）
python3 tools/build_obsidian_kb.py     # Obsidian 知識庫（tools/obsidian-kb/）

echo "=== ② 完整性 + 自檢 ==="
python3 tools/completeness_check.py . | head -5
if bash tools/selfcheck.sh >/tmp/selfcheck.out 2>&1; then
  echo "  ✓ 自檢通過（斷鏈0/完整性OK/冪等）"
else
  echo "  ⚠️ 自檢有問題，請看 /tmp/selfcheck.out"
  tail -12 /tmp/selfcheck.out
fi

echo "=== ③ 本地提交 ==="
if [ -z "$(git status --porcelain)" ]; then
  echo "  無改動，跳過提交"
else
  git add -A
  git commit -q -m "$MSG" && echo "  已提交: $(git log --oneline -1)"
fi

echo "=== ④ 推送上線 ==="
if git push origin main 2>/dev/null; then
  echo "  ✓ git push 成功（GitHub Pages 約 1 分鐘後生效）"
else
  echo "  ⚠️ git push 失敗，改用 GitHub API：sync_push.py"
  python3 tools/sync_push.py "$MSG"
fi

echo
echo "=== 完成 ==="
echo "線上: https://judickzhu.github.io/guhai-honglou/"
