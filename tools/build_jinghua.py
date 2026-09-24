#!/usr/bin/env python3
# build_jinghua.py —— 將《深度分析報告提純精華版.md》轉成網站一頁 jinghua.html
# 用法：將此 script 同 md 放喺 repo，執行 `python3 tools/build_jinghua.py` 即可重新生成。
# 「一份源、一鍵生成」：改 md → 重跑 → jinghua.html 更新 → push。兩處永遠一致。
import sys, re, html, os

# --- 可自行調整 ---
MD_REL = 'analysis/深度分析报告提纯精华版.md'
OUT_REL = 'jinghua.html'
TITLE = '深度精華·深度分析報告提純｜一起讀紅樓白話'
DESC = '《深度分析報告合集》637行提純精華版——紅樓夢／古文經典／漢字方言／人生哲思四源分析'
use_run = os.path.basename(sys.argv[0])
if len(sys.argv) >= 3:
    MD_REL = sys.argv[1]
    OUT_REL = sys.argv[2]
if len(sys.argv) == 2:
    MD_REL = sys.argv[1]

def inline(s):
    s = s.replace('`', '')
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<!\*)\*([^*\n]+?)\*(?!\*)', r'<i>\1</i>', s)
    return s

def convert(text):
    lines = text.split('\n')
    out = []
    i = 0
    n = len(lines)
    in_table = False
    in_list = False
    list_is_ul = False
    while i < n:
        line = lines[i].rstrip()
        s = line.strip()
        if s.startswith('|') and s.endswith('|'):
            cells = [inline(c.strip()) for c in s.strip('|').split('|')]
            if all(re.fullmatch(r':?-{2,}:?', re.sub(r'<[^>]+>', '', c)) for c in cells):
                i += 1
                continue
            if not in_table:
                out.append('<table class="acts"><thead><tr>' + ''.join('<th>' + c + '</th>' for c in cells) + '</tr></thead><tbody>')
                in_table = True
            else:
                out.append('<tr>' + ''.join('<td>' + c + '</td>' for c in cells) + '</tr>')
            i += 1
            continue
        else:
            if in_table:
                out.append('</tbody></table>')
                in_table = False
        m = re.match(r'^(#{1,3})\s+(.*)$', s)
        if m:
            level = len(m.group(1))
            out.append('<h%d>%s</h%d>' % (level, inline(m.group(2)), level))
            i += 1
            continue
        if s.startswith('>'):
            out.append('<blockquote>' + inline(s.lstrip('>').strip()) + '</blockquote>')
            i += 1
            continue
        m2 = re.match(r'^[-*]\s+(.*)$', s)
        if m2:
            if not in_list:
                out.append('<ul class="plain">')
                in_list = True
                list_is_ul = True
            out.append('<li>' + inline(m2.group(1)) + '</li>')
            i += 1
            continue
        m3 = re.match(r'^(\d+)\.\s+(.*)$', s)
        if m3:
            if not in_list:
                out.append('<ol>')
                in_list = True
                list_is_ul = False
            out.append('<li>' + inline(m3.group(2)) + '</li>')
            i += 1
            continue
        if in_list:
            out.append('</ul>' if list_is_ul else '</ol>')
            in_list = False
        if re.fullmatch(r'-{3,}|\*{3,}|_{3,}', s):
            out.append('<hr>')
            i += 1
            continue
        if s == '':
            i += 1
            continue
        out.append('<p>' + inline(s) + '</p>')
        i += 1
    if in_table:
        out.append('</tbody></table>')
    if in_list:
        out.append('</ul>' if list_is_ul else '</ol>')
    return '\n'.join(out)

HEADER = '''<!DOCTYPE html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TITLE</title>
<meta name="description" content="DESC">
<meta property="og:title" content="TITLE">
<meta property="og:description" content="DESC">
<meta property="og:type" content="website">
<link rel="stylesheet" href="style.css">
<script>var PREFIX="";</script>
</head><body>
<header><div class="bar"><a class="brand" href="index.html">一起讀紅樓白話</a><nav><a href="index.html">首頁</a><a href="chapters/000.html">逐回目錄</a><a href="framework.html">解讀框架</a><a class="act" href="jinghua.html">深度精華</a><a href="characters.html">人物對標</a><a href="mapping.html">三層映射</a><a href="pingyu.html">脂批</a><a href="jiaxu.html">甲戌本</a><a href="shixi.html">世系</a><a href="qa.html">問答區</a></nav></div><div class="tools"><input id="q" placeholder="檢索全部回目…" onkeyup="if(event.key=='Enter')searchSite()"><button onclick="searchSite()">檢索</button><span class="spacer"></span><button class="tbtn" onclick="setSize('s')" title="小字">A</button><button class="tbtn" onclick="setSize('m')" title="中字">A</button><button class="tbtn" onclick="setSize('l')" title="大字">A</button><button class="tbtn" onclick="toggleTheme()" id="themeBtn">◐</button></div><div id="sr" class="sr hidden"></div></header>
<main>
<p class="crumbs"><a href="index.html">首頁</a> › <a href="jinghua.html">深度精華</a></p>
'''

FOOTER = '''</main>
<footer><p>一起讀紅樓白話 · 白話文解讀書中白話。本站「深度精華」一頁由源文件《深度分析報告提純精華版.md》一鍵生成，改源後重跑 <code>tools/build_jinghua.py</code> 即同步。站內「歷史對位/字音字形」均為<strong>提問者個人讀法</strong>，非紅學或史學界共識；【用户原話】保留原話、【AI 扩展·待核】為 AI 引申待查證。</p><p class="foot-fund"><a href="https://github.com/sponsors/judickzhu" target="_blank" rel="noopener">♥ 資助本站（GitHub Sponsors）</a> —— 用於網站維護。</p></footer>
<script src="app.js"></script>
<script src="search-data.js"></script>
<script src="zi-hao-data.js"></script>
<script src="zi-hao.js"></script>
</body></html>
'''

def main():
    if not os.path.exists(MD_REL):
        print('找不到源文件: %s' % MD_REL)
        sys.exit(1)
    body = convert(open(MD_REL, encoding='utf-8').read())
    htmlout = HEADER.replace('TITLE', TITLE).replace('DESC', DESC) + body + FOOTER
    open(OUT_REL, 'w', encoding='utf-8').write(htmlout)
    print('已生成 %s（%s 字元）' % (OUT_REL, len(htmlout)))

if __name__ == '__main__':
    main()