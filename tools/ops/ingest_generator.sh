#!/bin/bash
# ingest_generator.sh — 解鎖後:把主生成器入庫,消除單點故障與雙源漂移
#
# 用法:
#   bash tools/ops/ingest_generator.sh                       # 自動偵測工作區,dry-run
#   bash tools/ops/ingest_generator.sh <工作區> --apply      # 實際執行
#
# 前置:工作區內應有 build_honglou_site.py 與 honglou_*.json(素材)
set -u
cd "$(dirname "$0")/../.." || exit 1     # 站點根
ROOT=$(pwd)
APPLY=0
WS=""
for a in "$@"; do
  case "$a" in
    --apply) APPLY=1 ;;
    *) WS="$a" ;;
  esac
done
[ -z "$WS" ] && for c in "$HOME/dev/电子书ipa" "$HOME/Downloads/电子书ipa"; do
  [ -f "$c/build_honglou_site.py" ] && WS="$c" && break
done

echo "站點根:$ROOT"
echo "工作區:${WS:-（未找到）}"
echo "模式:$([ $APPLY = 1 ] && echo '實際執行' || echo 'dry-run（僅檢查）')"
echo
[ -z "$WS" ] || [ ! -f "$WS/build_honglou_site.py" ] && { echo "✗ 找不到工作區的 build_honglou_site.py"; echo "  用法: bash tools/ops/ingest_generator.sh <工作區> --apply"; exit 1; }

run() { if [ $APPLY = 1 ]; then eval "$@"; else echo "  [將執行] $*"; fi; }

echo "=== 1. 生成器入庫 ==="
run "cp '$WS/build_honglou_site.py' tools/build_honglou_site.py"
[ $APPLY = 1 ] && python3 -c "import ast;ast.parse(open('tools/build_honglou_site.py',encoding='utf-8').read())" && echo "  ✓ 語法OK"

echo "=== 2. 素材刷新(content-source/) ==="
run "cp '$WS'/honglou_*.json tools/content-source/ 2>/dev/null"

echo "=== 3. 改寫生成器路徑(→ 新倉佈局) ==="
run "python3 tools/ops/patch_generator_paths.py tools/build_honglou_site.py"

echo "=== 4. 回填手改內容(消除雙源:076中心思想 / 神瑛侍者) ==="
if [ $APPLY = 1 ]; then
  python3 tools/ops/backport_direct_edits.py tools --apply || echo "  ⚠ 回填有問題,請人工確認"
else
  echo "  [將執行] python3 tools/ops/backport_direct_edits.py tools --apply"
fi

echo "=== 5. 跑生成器 ==="
if [ $APPLY = 1 ]; then
  python3 tools/build_honglou_site.py 2>&1 | tail -3 || { echo "  ✗ 生成器失敗,中止"; exit 1; }
  echo "  --- 生成後變更檔案 ---"
  git status --short | head -20
  echo "  變更數: $(git status --short | wc -l | tr -d ' ')"
else
  echo "  [將執行] python3 tools/build_honglou_site.py"
fi

echo "=== 6. 冪等檢查(再跑一次) ==="
if [ $APPLY = 1 ]; then
  python3 tools/build_honglou_site.py >/dev/null 2>&1
  n=$(git status --short | wc -l | tr -d ' ')
  echo "  二次跑後差異數:$n（與首次相同即冪等 ✓）"
fi

echo "=== 7. 自檢 ==="
if [ $APPLY = 1 ]; then bash tools/selfcheck.sh || echo "  ⚠ 自檢有問題"; else echo "  [將執行] bash tools/selfcheck.sh"; fi

echo
if [ $APPLY = 1 ]; then
cat <<'EOF'
=== 下一步(人工確認後提交) ===
  git diff --stat                    # 看生成器產出與現站的差異
  git add -A && git commit -m "主生成器入庫+路徑改寫+雙源回填;冪等0;自檢全綠"
  git push origin main
EOF
else
  echo "確認後執行: bash tools/ops/ingest_generator.sh \"$WS\" --apply"
fi
