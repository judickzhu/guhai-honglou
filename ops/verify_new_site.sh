#!/bin/bash
# verify_new_site.sh — 新站上线后逐项验证
# 用法: bash /tmp/verify_new_site.sh [新站URL] [新倉庫目錄]
BASE="${1:-https://judickzhu.github.io/guhai-honglou}"
NEW="${2:-.}"
echo "=== 1. 線上可用性 ==="
for p in "" index.html framework.html characters.html shixi.html pingyu.html mapping.html qa.html jiaxu.html funding.html chapters/000.html chapters/001.html chapters/076.html chapters/120.html zi-hao-data.js search-data.js style.css; do
  printf "  %s  %s\n" "$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "$BASE/$p")" "/$p"
done
echo "=== 2. 舊址跳轉 ==="
curl -s --max-time 15 "https://judickzhu.github.io/guhai/honglou/index.html" | grep -c "guhai-honglou" | sed 's/^/  含新址連結數: /'
echo "=== 3. 關鍵內容抽查 ==="
curl -s --max-time 15 "$BASE/index.html" | grep -c "作者定位\|閨閣之事" | sed 's/^/  首頁體系定位: /'
curl -s --max-time 15 "$BASE/framework.html" | grep -c "核對總表" | sed 's/^/  框架頁核對總表: /'
curl -s --max-time 15 "$BASE/chapters/076.html" | grep -c "贔屭朝光透" | sed 's/^/  076 中心思想: /'
echo "=== 4. 本地生成器冪等 ==="
if [ -f "$NEW/tools/build_honglou_site.py" ]; then
  ( cd "$NEW" && python3 tools/build_honglou_site.py >/dev/null 2>&1 && echo "  跑通 ✓ 差異數:$(git status --short | wc -l | tr -d ' ')" ) || echo "  ✗ 生成器失敗"
else echo "  (未找到生成器:$NEW/tools/)"; fi
echo "=== 5. 斷鏈 ==="
if [ -d "$NEW" ]; then
python3 - "$NEW" <<'PY'
import re,glob,os,sys
root=sys.argv[1]; os.chdir(root)
bad=[]
for f in glob.glob('**/*.html', recursive=True):
    d=os.path.dirname(f)
    for m in re.findall(r'(?:href|src)="([^"]+)"', open(f,encoding='utf-8',errors='ignore').read()):
        if m.startswith(('http','#','mailto')): continue
        p=m.split('#')[0]
        if p and not os.path.exists(os.path.normpath(os.path.join(d,p))): bad.append((f,m))
print(f"  斷鏈: {len(bad)}", bad[:5])
PY
fi
echo "=== 6. 大檔策略 ==="
[ -f "$NEW/dc-honglou-base-120.pdf" ] && echo "  ⚠ PDF 仍在倉庫(應走 Releases)" || echo "  ✓ PDF 未入庫"
