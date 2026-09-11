#!/bin/bash
# migrate_b.sh — 红樓站獨立到 guhai-honglou（方案 B）
#
# 用法:
#   bash /tmp/migrate_b.sh <工作區> <新倉庫目錄>            # Dry-run（只列出）
#   bash /tmp/migrate_b.sh <工作區> <新倉庫目錄> --apply    # 實際執行
#
# 例:
#   bash /tmp/migrate_b.sh ~/dev/电子书ipa ~/dev/hl-new --apply
#
set -u
WS="${1:-}"
NEW="${2:-}"
APPLY=0; [ "${3:-}" = "--apply" ] && APPLY=1

[ -z "$WS" ] || [ -z "$NEW" ] && { echo "用法: bash migrate_b.sh <工作區> <新倉庫目錄> [--apply]"; exit 1; }
[ -d "$WS/网站/honglou" ] || { echo "✗ 找不到 $WS/网站/honglou"; exit 1; }
[ -d "$NEW" ] || { echo "✗ 找不到新倉庫目錄 $NEW(請先 git clone 空倉庫)"; exit 1; }

echo "工作區:$WS"
echo "新倉庫:$NEW"
echo "模式:$([ $APPLY = 1 ] && echo '實際執行' || echo 'Dry-run 僅列出')"
echo

run() { if [ $APPLY = 1 ]; then eval "$@"; else echo "  [將執行] $*"; fi; }

echo "=== Step 1 站點檔案 honglou/* → 新倉庫根（排除大檔 PDF）==="
run "mkdir -p '$NEW'"
if [ $APPLY = 1 ]; then
  ( cd "$WS/网站/honglou" && for f in *; do
      case "$f" in *.pdf) echo "  (跳過大檔) $f";; *) cp -R "$f" "$NEW/";; esac
  done )
else
  echo "  [將複製] $WS/网站/honglou/* → $NEW/（*.pdf 除外）"
fi

echo
echo "=== Step 2 工具 tools/ ==="
run "mkdir -p '$NEW/tools'"
for t in admin_server.py build_obsidian_kb.py gen_yuanwen_from_ima.py gen_yuanwen_json.py merge_yuanwen_pdfs.py README.md; do
  [ -f "$WS/网站/tools/$t" ] && run "cp '$WS/网站/tools/$t' '$NEW/tools/'"
done
for d in content-mirror obsidian-kb assets; do
  [ -d "$WS/网站/tools/$d" ] && run "cp -R '$WS/网站/tools/$d' '$NEW/tools/'"
done

echo
echo "=== Step 3 生成器 + 素材 ==="
run "cp '$WS/build_honglou_site.py' '$NEW/tools/build_honglou_site.py'"
run "mkdir -p '$NEW/tools/content-source'"
for j in "$WS"/honglou_*.json; do
  [ -f "$j" ] && run "cp '$j' '$NEW/tools/content-source/'"
done

echo
echo "=== Step 4 改寫生成器路徑（新佈局）==="
run "python3 /tmp/patch_generator_paths.py '$NEW/tools/build_honglou_site.py'"

echo
echo "=== Step 5 .gitignore ==="
if [ $APPLY = 1 ]; then
  cat > "$NEW/.gitignore" <<'EOF'
.DS_Store
*.pdf
*.epub
*.zip
__pycache__/
EOF
  echo "  ✓ 已寫入"
else
  echo "  [將寫入] .gitignore（.DS_Store/*.pdf/*.epub/*.zip/__pycache__）"
fi

echo
echo "=== Step 6 驗證 ==="
if [ $APPLY = 1 ]; then
  ( cd "$NEW" && python3 tools/build_honglou_site.py >/tmp/migrate_build.log 2>&1 && echo "  ✓ 生成器跑通" || { echo "  ✗ 生成器失敗:"; tail -5 /tmp/migrate_build.log; } )
  ( cd "$NEW" && python3 tools/build_honglou_site.py >/dev/null 2>&1 && n=$(git status --short | wc -l | tr -d ' ') && echo "  幂等檢查(第二次跑後差異數,應為0/僅未提交):$n" )
  echo "  檔案數:$(find "$NEW" -name '*.html' | wc -l | tr -d ' ') 個 html"
else
  echo "  [將驗證] 跑生成器 + 冪等檢查 + 統計 html 數"
fi

echo
echo "=== 下一步(人工) ==="
cat <<'EOF'
  1) git -C <新倉庫> add -A && git commit -m "紅樓站獨立上線"
  2) git -C <新倉庫> push origin main
  3) GitHub 新倉庫 → Settings → Pages → Source: main / (root) → 網址 https://judickzhu.github.io/guhai-honglou/
  4) 舊倉庫 guhai/honglou/index.html 改為跳轉頁(見 runbook_b.md Step 4)
  5) 舊倉庫跑 /tmp/redact_internal.sh --apply 清內部資料
  6) 大檔 60MB PDF → 新舊倉庫的 Releases
EOF
