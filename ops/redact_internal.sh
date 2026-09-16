#!/bin/bash
# redact_internal.sh — judickzhu/guhai 内部资料移出公开仓库
# 用法:
#   bash /tmp/redact_internal.sh            # 只列出(Dry-run,安全)
#   bash /tmp/redact_internal.sh --apply    # 实际搬移(搬到 _internal_private/)
#
# 设计原则:非破坏性「搬移」而非删除;站点依赖的文件一律不动。
set -u
REPO="${1:-$HOME/Downloads/电子书ipa/网站}"
APPLY=0; [ "${2:-}" = "--apply" ] && APPLY=1
[ "${1:-}" = "--apply" ] && { APPLY=1; REPO="$HOME/Downloads/电子书ipa/网站"; }
DEST="_internal_private"

cd "$REPO" 2>/dev/null || { echo "✗ 无法进入仓库:$REPO"; exit 1; }
echo "仓库:$REPO"
echo "模式:$([ $APPLY = 1 ] && echo '实际搬移' || echo 'Dry-run 仅列出')"
echo

# ── 内部资料模式(移出公开仓库)────────────────────────────
PATTERNS=(
  "v31_prompt.txt"          # DC姐姐系统提示词
  "v3*_*" "v4*_*"           # 内部测试集/结果/红队
  "*_results.jsonl" "*_judged.json"
  "backend_snapshot*"       # 后端快照
  "qa_log.json" "kb_queries.jsonl" "kb_selfreview*"
  "chain81_*"
  "verify_*.js" "rebuild_backend*.js" "website_tmp_fix*.js"
  "site_full_rebuild*"
  "DCOGAI*"                 # 产品文档
  "DC姐姐*"                 # 人格模型/营销/训练
  "認知鏈*.md" "答非所問自動監控機制.md"
)
# ── 保留(站点依赖,勿动)────────────────────────────────
# index.html style.css app.js auth.js dc-chat.js kb.html dc-kb.html
# phenomena.html acts.html checklist.html mapping.html framework.html
# 404.html og.png chapters/ gudao/ dc-sister/ orig/ pdf/ honglou/
# funding/ search-data.js site_bookcats.js kb-books.json kb-data_simplified.json

# 去重收集
LIST=$(mktemp)
for p in "${PATTERNS[@]}"; do
  for f in $p; do [ -f "$f" ] && echo "$f" >> "$LIST"; done
done
sort -u "$LIST" -o "$LIST"
echo "=== 将移出公开仓库的文件 ==="
TOTAL=0; COUNT=0
while IFS= read -r f; do
  sz=$(stat -f%z "$f" 2>/dev/null || echo 0)
  printf "  %8.1f KB  %s\n" "$(echo "$sz/1024" | bc -l)" "$f"
  TOTAL=$((TOTAL+sz)); COUNT=$((COUNT+1))
done < "$LIST"
printf "\n合计:%d 个文件,%.1f MB\n" "$COUNT" "$(echo "$TOTAL/1048576" | bc -l)"

if [ $APPLY = 1 ]; then
  echo; echo "=== 搬移中 ==="
  mkdir -p "$DEST"
  while IFS= read -r f; do
    mkdir -p "$DEST/$(dirname "$f")" 2>/dev/null
    git mv -k "$f" "$DEST/$f" 2>/dev/null || mv "$f" "$DEST/$f"
  done < "$LIST"
  # robots.txt → Disallow
  printf 'User-agent: *\nDisallow: /\n' > robots.txt
  rm -f sitemap.xml
  # .gitignore 补全
  cat >> .gitignore <<'EOF'
.DS_Store
_internal_private/
*_results.jsonl
*_judged.json
backend_snapshot*
qa_log.json
site_full_rebuild*
*.pdf
EOF
  # 生成器入库(消除单点故障)
  if [ -f "../build_honglou_site.py" ] && [ ! -f "tools/build_honglou_site.py" ]; then
    cp "../build_honglou_site.py" tools/build_honglou_site.py
    echo "✓ 生成器已入库 tools/build_honglou_site.py"
  fi
  echo "✓ 已搬移到 $DEST/(已加入 .gitignore)"
  echo
  echo "=== 下一步(人工确认后) ==="
  echo "  git status"
  echo "  git add -A && git commit -m '安全:内部资料移出公开仓库 + robots 禁止抓取'"
  echo "  git push origin main"
  echo
  echo "⚠ 历史仍含这些文件:彻底清除需"
  echo "  git filter-repo --path v31_prompt.txt ...  (会重写历史,需强推)"
else
  echo
  echo "确认无误后执行:bash /tmp/redact_internal.sh --apply"
fi
