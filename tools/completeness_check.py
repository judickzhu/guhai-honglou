#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""completeness_check.py — 120 回卡內容完整性掃描
檢查:①六字段區塊是否齊 ②「已有解碼素材」標記與實際內容是否一致
      ③子嗥/檢索引用的 ref 是否都存在 ④覆蓋率統計
用法: python3 tools/completeness_check.py [站點根]
"""
import re, os, sys, json, glob
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
os.chdir(ROOT)

SEC = ["本回金句", "解碼軌", "脂批路標", "人物點評", "詩詞解讀", "文學軌"]
issues, stats = [], {"cards": 0, "dec": 0, "jinju": 0, "pingyu": 0, "poem": 0, "has": 0, "none": 0}

def has_real(html, sec):
    m = re.search(r'<section[^>]*><h2>' + re.escape(sec) + r'[^<]*</h2>(.*?)</section>', html, re.S)
    if not m: return None, False
    body = m.group(1)
    return len(re.findall(r'<li>', body)), 'placeholder' not in body

for f in sorted(glob.glob("chapters/*.html")):
    n = os.path.basename(f)
    if n == "000.html": continue
    h = open(f, encoding="utf-8").read()
    stats["cards"] += 1
    # ① 區塊齊全
    for sec in SEC:
        if not re.search(r'<h2>' + re.escape(sec), h):
            issues.append((n, "缺區塊：" + sec))
    # ② 標記與內容一致
    st = re.search(r'class="st st-(has|none)"', h)
    st = st.group(1) if st else "?"
    _, dec_real = has_real(h, "解碼軌")
    if st == "has":
        stats["has"] += 1
        if not dec_real: issues.append((n, "標記『已有解碼素材』但解碼軌為空"))
        else: stats["dec"] += 1
    elif st == "none":
        stats["none"] += 1
        if dec_real: issues.append((n, "標記『待解碼』但解碼軌有內容"))
    # ③ 其他欄位覆蓋
    for key, sec in [("jinju","本回金句"), ("pingyu","脂批路標"), ("poem","詩詞解讀")]:
        _, real = has_real(h, sec)
        if real: stats[key] += 1
    # ④ 中心思想只在 76
    if "贔屭朝光透" in h and n != "076.html":
        issues.append((n, "非 076 卡出現中心思想句"))

# ⑤ 引用完整性：子嗥 + 檢索
def refs_from(jsfile, key):
    if not os.path.exists(jsfile): return []
    t = open(jsfile, encoding="utf-8").read()
    return re.findall(r'"' + key + r'":\s*"([^"]*)"', t)

for rf in refs_from("zi-hao-data.js", "ref") + refs_from("search-data.js", "url"):
    if not rf or rf.startswith(("http", "#")): continue
    p = rf.split("#")[0]
    if p and not os.path.exists(p):
        issues.append(("引用", "失效引用：" + rf))

print(f"回卡數：{stats['cards']}")
print(f"已有解碼素材：{stats['has']}（其中解碼軌有內容 {stats['dec']}）｜待解碼：{stats['none']}")
print(f"有金句：{stats['jinju']}｜有脂批：{stats['pingyu']}｜有詩詞：{stats['poem']}")
print(f"問題數：{len(issues)}")
for n, msg in issues[:30]:
    print(f"  ⚠ {n}：{msg}")
sys.exit(1 if issues else 0)
