#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
patch_generator_paths.py — 把生成器路径改为「新仓库布局」
从:ROOT=電子書ipa、OUT=ROOT/網站/honglou、素材=ROOT/honglou_*.json
到:ROOT=倉庫根、OUT=倉庫根、素材=ROOT/tools/content-source/honglou_*.json

用法:python3 patch_generator_paths.py <新仓库里的 build_honglou_site.py>
"""
import re, sys, os

p = sys.argv[1] if len(sys.argv) > 1 else "tools/build_honglou_site.py"
s = open(p, encoding="utf-8").read()
orig = s

# 1) ROOT:生成器在 tools/ 下 → 倉庫根 = 上一層
s = re.sub(r'^ROOT\s*=\s*os\.path\.dirname\(os\.path\.abspath\(__file__\)\).*$',
           'ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 倉庫根（tools/ 的上一層）',
           s, count=1, flags=re.M)

# 2) 素材目錄常量(插在 ROOT 定義後)
if 'SRC = os.path.join' not in s:
    s = re.sub(r'(^ROOT\s*=.*$)', r'\1\nSRC  = os.path.join(ROOT, "tools", "content-source")  # 素材（honglou_*.json）',
               s, count=1, flags=re.M)

# 3) OUT:站點根
s = re.sub(r'^OUT\s*=\s*os\.path\.join\(ROOT,\s*"网站",\s*"honglou"\).*$',
           'OUT  = ROOT  # 站點根（新倉庫根即站點）', s, count=1, flags=re.M)

# 4) 所有素材路徑 ROOT/"honglou_*.json" → SRC/"honglou_*.json"
s = re.sub(r'os\.path\.join\(ROOT,\s*"(honglou_[a-z_]+\.json)"\)',
           r'os.path.join(SRC, "\1")', s)

open(p, "w", encoding="utf-8").write(s)

# 驗證:語法 + 關鍵常量
import ast
ast.parse(open(p, encoding="utf-8").read())
print("✓ 路徑已改寫並通過語法檢查")
print("  改動行:")
for ln in open(p, encoding="utf-8").read().split("\n")[:30]:
    if ln.startswith(("ROOT", "SRC", "OUT", "MEN", "DLG", "CHR", "POEM", "PINGYU", "YUANWEN", "CHARS_ARCH", "JINJU", "FBACK")):
        print("   ", ln[:100])
if s == orig:
    print("⚠ 未偵測到任何改動——請確認原檔案的常量寫法")
