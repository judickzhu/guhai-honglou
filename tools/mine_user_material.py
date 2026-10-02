#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mine_user_material.py — 從《紅樓夢對話合併》挖掘「提問者」原話素材。

用途
----
為「一起讀紅樓白話」逐回卡補素材時，**只取提問者本人發言**（`### 👤 提問者`），
排除 AI 輸出（`### 🤖 DeepSeek 回答`）——避免把 AI 戲謔式推演誤當史實灌入站點
（站規：來源必標、無素材寫「待解碼」、不硬編）。

典型流程
--------
1. `python3 tools/mine_user_material.py --stats`            看語料規模
2. `python3 tools/mine_user_material.py --chapter 46`       看某回有無提問者素材
3. `python3 tools/mine_user_material.py --kw 鴛鴦 尤三姐`    用獨特詞檢索
4. 逐段審讀 → 把提問者真解碼寫進 `CURATED`（帶「总纲 L行號」）→ 重跑生成器

注意
----
* 語料繁簡混雜；提問者原話以**繁體**為主，故關鍵詞建議用繁體。
* `### 👤 提問者` 區塊內亦可能有「貼上的原文／AI 回覆」——仍需人工審讀，勿整段照搬。
* 只加**與該回直接相關**的解碼（人物／事件在該回），勿把泛論硬掛到某一回。
""".

版權聲明：本工具及其產出之素材屬「一起讀紅樓白話」核心資產，依 CC BY-NC-SA 4.0 授權（© 2026）：非商業使用、轉載須署名、未經授權不得用作 AI 模型訓練資料。詳見 LICENSE。
"""
import argparse
import os
import re
import sys

DEFAULT_SRC = os.path.expanduser("~/Desktop/DeepSeek对话合集/Markdown源文件/紅樓夢.md")
CHP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build_honglou_site.py")


def parse_user_blocks(path):
    """解析合併檔，回傳提問者區塊 [(起行號, 對話標題, 內容), ...]。"""
    lines = open(path, encoding="utf-8").read().split("\n")
    blocks, cur_sec, spk, buf, start = [], "", None, [], 0

    def flush():
        if spk == "👤 提問者" and buf:
            t = "\n".join(buf).strip()
            if t:
                blocks.append((start, cur_sec, t))

    for i, ln in enumerate(lines, 1):
        if re.match(r"^## 📖 ", ln):
            flush(); cur_sec, spk, buf = ln[5:].strip(), None, []
            continue
        m = re.match(r"^### (👤 提問者|🤖 DeepSeek 回答)\s*$", ln)
        if m:
            flush(); spk, buf, start = m.group(1), [], i + 1
            continue
        if spk is not None:
            buf.append(ln)
    flush()
    return blocks


def cn_num(n):
    d0 = "零一二三四五六七八九"
    if n <= 10:
        return "十" if n == 10 else d0[n]
    if n < 20:
        return "十" + (d0[n - 10] if n % 10 else "")
    if n < 100:
        return d0[n // 10] + "十" + (d0[n % 10] if n % 10 else "")
    if n == 100:
        return "一百"
    if n < 110:
        return "一百" + d0[n - 100]
    if n < 120:
        return "一百" + d0[(n - 100) // 10] + "十" + (d0[n % 10] if n % 10 else "")
    return "一百二十"


def hui_titles():
    """自站點生成器取回目（回號 → 上聯/下聯），供第N回檢索。"""
    import importlib.util
    spec = importlib.util.spec_from_file_location("bhs", CHP)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {n: (up, low) for n, up, low, act in mod.CH}


def main():
    ap = argparse.ArgumentParser(description="挖掘提問者原話素材（逐回卡補素材用）")
    ap.add_argument("--src", default=DEFAULT_SRC, help="《紅樓夢.md》合併檔路徑")
    ap.add_argument("--chapter", type=int, help="回號（比對「第N回」及回目上下聯）")
    ap.add_argument("--kw", nargs="*", default=[], help="關鍵詞（任一命中即列出）")
    ap.add_argument("--stats", action="store_true", help="只印統計")
    ap.add_argument("--maxlen", type=int, default=600, help="每段截斷長度")
    a = ap.parse_args()

    if not os.path.exists(a.src):
        sys.exit(f"找不到語料：{a.src}")

    blocks = parse_user_blocks(a.src)
    if a.stats:
        secs = {s for _, s, _ in blocks}
        print(f"提問者區塊: {len(blocks)}｜涉及對話: {len(secs)}")
        return

    if not a.chapter and not a.kw:
        ap.error("需給 --chapter 或 --kw（或用 --stats）")

    if a.chapter:
        up, low = hui_titles()[a.chapter]
        cpat = [f"第{a.chapter}回", f"第{cn_num(a.chapter)}回", up, low]
        hits = [b for b in blocks
                if any(p in b[2] for p in cpat) and (not a.kw or any(k in b[2] for k in a.kw))]
    else:
        hits = [b for b in blocks if any(k in b[2] for k in a.kw)]

    print(f"命中 {len(hits)} 段\n")
    for L, sec, t in hits:
        print(f"===== L{L} [{sec[:40]}] =====")
        print(t[: a.maxlen] + ("…" if len(t) > a.maxlen else ""))
        print()


if __name__ == "__main__":
    main()
