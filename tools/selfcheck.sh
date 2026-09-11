#!/bin/bash
# selfcheck.sh — 站點自檢(斷鏈/關鍵內容/子嗥JSON/生成器冪等)
# 用法: bash tools/selfcheck.sh
cd "$(dirname "$0")/.." || exit 1
FAIL=0
echo "=== 1. 斷鏈掃描 ==="
python3 - <<'PY'
import re,glob,os
bad=[]
for f in glob.glob('**/*.html', recursive=True):
    d=os.path.dirname(f)
    for m in re.findall(r'(?:href|src)="([^"]+)"', open(f,encoding='utf-8',errors='ignore').read()):
        if m.startswith(('http','#','mailto')): continue
        p=m.split('#')[0]
        if p and not os.path.exists(os.path.normpath(os.path.join(d,p))): bad.append((f,m))
print('  斷鏈:', len(bad))
for b in bad[:8]: print('   ', b)
raise SystemExit(1 if bad else 0)
PY
[ $? -ne 0 ] && FAIL=1
echo "=== 2. 子嗥 JSON 語法 ==="
if command -v node >/dev/null; then node --check zi-hao-data.js && echo "  ✓ 語法OK" || FAIL=1; else echo "  (無 node,跳過)"; fi
echo "=== 3. 關鍵內容抽查 ==="
check() { n=$(grep -c "$1" "$2" 2>/dev/null); n=${n:-0}; if [ "$n" -gt 0 ]; then echo "  ✓ $1 → $2"; else echo "  ✗ 缺: $1 → $2"; FAIL=1; fi; }
check "作者定位" index.html
check "核對總表" framework.html
check "判別線圖" shixi.html
check "贔屭朝光透" chapters/076.html
check "神瑛侍者" chapters/001.html
check "神瑛侍者" characters.html
check "神瑛侍者" zi-hao-data.js
check "阿巴亥" chapters/013.html
echo "=== 3b. 120 回卡完整性掃描 ==="
python3 tools/completeness_check.py . && echo "  ✓ 完整性OK" || FAIL=1
echo "=== 4. 生成器冪等(若有) ==="
if [ -f tools/build_honglou_site.py ]; then
  python3 tools/build_honglou_site.py >/dev/null 2>&1 && d=$(git status --short | wc -l | tr -d ' ') && echo "  跑通 ✓ 差異數: $d" && [ "$d" != "0" ] && FAIL=1
else echo "  (生成器未入庫,跳過)"; fi
echo
[ $FAIL = 0 ] && echo "✅ 全部通過" || echo "⚠ 有問題(見上)"
exit $FAIL
