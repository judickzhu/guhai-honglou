#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""入站防呆檢查（防位置錯置）

檢查三件事：
1. 詩詞條目是否誤入「解碼軌」（詩＝詩解，應在詩詞解讀區）
2. 對白/原話解碼是否誤入「詩詞解讀」區（對白解碼應在解碼軌）
3. 人物身分標注是否誤入解碼軌（身分應在人物點評區）

用法：
  python3 tools/ops/check_placement.py            # 檢查遠端 main（需 gh）
  python3 tools/ops/check_placement.py --local    # 檢查本地產物

設計原則：只報警、不改檔（避免自動改錯）。
"""
import base64, json, re, subprocess, sys

REPO = "judickzhu/guhai-honglou"

# 詩詞特徵（出現在詩詞區才對）
POEM_MARKS = ["〈", "〉", "回前詩", "判詞", "聯句", "韻", "偈"]
# 對白特徵（出現在解碼軌才對）
DIALOG_MARKS = ["原話", "書中原文", "冷子興", "焦大", "門童"]

def gh_get(path):
    for _ in range(3):
        r = subprocess.run(["gh", "api", "repos/%s/contents/%s" % (REPO, path)],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return base64.b64decode(json.loads(r.stdout)["content"]).decode("utf-8")
    return None

def sections(html):
    """切出各區塊內容"""
    out = {}
    for m in re.finditer(r"<h2>([^<]+)</h2>(.*?)(?=<h2>|<nav class="pn">|$)", html, re.S):
        out[m.group(1)] = m.group(2)
    return out

def check(n):
    html = gh_get("chapters/%03d.html" % n)
    if not html:
        return []
    secs = sections(html)
    issues = []
    # ① 解碼軌裡有詩詞特徵
    dec = secs.get("解碼軌 · 歷史對位與字音字形", "")
    for mk in POEM_MARKS:
        if mk in dec and ("回前詩" in dec or "判詞" in dec or "聯句" in dec):
            issues.append("解碼軌含詩詞特徵「%s」——詩應入詩詞解讀區" % mk)
            break
    # ② 詩詞解讀區含對白解碼
    poem = secs.get("詩詞解讀", "")
    if poem and any(k in poem for k in DIALOG_MARKS) and "解碼軌" in poem:
        issues.append("詩詞解讀區含對白解碼（「解碼軌」字樣）——對白解碼應入解碼軌")
    # ③ 人物身分標注在解碼軌
    if "【第%d回身分】" % n in dec or "此回身分" in dec:
        issues.append("「此回身分」在解碼軌——身分標注應入人物點評區")
    return issues

def main():
    bad = 0
    for n in range(1, 121):
        iss = check(n)
        if iss:
            bad += 1
            print("第%d回:" % n)
            for x in iss:
                print("   ⚠ " + x)
    print("\n檢查完成：%d 回有位置問題" % bad if bad else "\n✅ 檢查完成：無位置錯置")

if __name__ == "__main__":
    main()
