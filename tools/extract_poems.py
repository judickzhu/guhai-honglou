#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_poems.py — 從抄本原文（honglou_yuanwen.json）提取詩詞原文，供落回各自回目。
用法: python3 tools/extract_poems.py [--write]
原則: 逐首以「起錨（首句）＋止錨（後文標記）」精準切片，寧缺勿錯；
      提取結果標【原詩·待解讀】，解讀由提問者後補。
"""
import json, os, re, sys, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YW = os.path.join(ROOT, "tools", "content-source", "honglou_yuanwen.json")
POEM = os.path.join(ROOT, "tools", "content-source", "honglou_poem.json")

# (回, 詩題, 作者, 起錨首句, 止錨後文標記)
SPECS = [
    (37, "詠白海棠（探春）", "蕉下客", "斜陽寒草帶重門", "珍重芳姿晝掩門"),
    (37, "詠白海棠（寶釵）", "蘅蕪君", "珍重芳姿晝掩門", "秋容淺淡映重門"),
    (37, "詠白海棠（寶玉）", "怡紅公子", "秋容淺淡映重門", "半卷湘簾半掩門"),
    (37, "詠白海棠（黛玉）", "瀟湘妃子", "半卷湘簾半掩門", "神仙昨日降都門"),
    (37, "詠白海棠（湘雲·其一）", "枕霞舊友", "神仙昨日降都門", "蘅芷階通蘿薜門"),
    (37, "詠白海棠（湘雲·其二）", "枕霞舊友", "蘅芷階通蘿薜門", "衆人看了"),
    (45, "秋窗風雨夕（代別離）", "瀟湘妃子", "秋花慘淡秋草黃", "吟罷擲筆"),
]

def clean(s):
    s = re.sub(r"\([^)]{0,80}\)", "", s)      # 去半角括號批語
    s = re.sub(r"（[^）]{0,80}）", "", s)      # 去全角括號批語
    s = re.sub(r"\s+", "", s)
    return s.strip("，,。 ")

def main():
    write = "--write" in sys.argv
    d = json.load(open(YW, encoding="utf-8"))
    poems = json.load(open(POEM, encoding="utf-8"))
    added = 0
    for ch, title, author, start_a, end_a in SPECS:
        t = d.get(str(ch), "")
        i = t.find(start_a)
        if i < 0:
            print(f"  ✗ 第{ch}回 [{title}] 起錨未找到"); continue
        j = t.find(end_a, i + len(start_a))
        seg = t[i: j if j > 0 else i + 400]
        seg = clean(seg)
        if len(seg) < 20:
            print(f"  ✗ 第{ch}回 [{title}] 過短({len(seg)})"); continue
        print(f"  ✓ 第{ch}回 [{title}] {len(seg)}字: {seg[:44]}…")
        if write:
            v = poems.setdefault(str(ch), [])
            name = f"{title}｜原詩（{author}）"
            if not any(name in x[0] for x in v):
                v.append([name, f"原詩：{seg}　【解讀待補·提問者後補】"])
                added += 1
    if write:
        json.dump(poems, open(POEM, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"已寫入 {added} 首")

if __name__ == "__main__":
    main()
