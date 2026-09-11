#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_sitemap.py — 為新站生成 sitemap.xml（根頁 + 120 章 + 欄目頁）"""
import os, sys, datetime, glob
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
BASE = sys.argv[2] if len(sys.argv) > 2 else "https://judickzhu.github.io/guhai-honglou"
urls = []
for f in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
    urls.append(os.path.relpath(f, ROOT).replace(os.sep, "/"))
for f in sorted(glob.glob(os.path.join(ROOT, "chapters", "*.html"))):
    urls.append("chapters/" + os.path.basename(f))
today = datetime.date.today().isoformat()
out = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in urls:
    out.append(f"  <url><loc>{BASE}/{u}</loc><lastmod>{today}</lastmod></url>")
out.append("</urlset>")
open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write("\n".join(out) + "\n")
print(f"✓ sitemap.xml 已生成:{len(urls)} 個 URL → {BASE}")
