#!/usr/bin/env python3
# build_jilu.py —— 記錄欄：對話留底「索引」（不整篇渲染全文；源檔同步於 analysis/）
# 新增記錄：把對話 md 放入 analysis/ 並重跑本腳本即同步。
import sys, os, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_honglou_site as B


def main():
    files = sorted(glob.glob('analysis/昨日对话记录_*.md'))
    rows = []
    for f in files:
        text = open(f, encoding='utf-8').read()
        title = '昨日對話記錄'
        src = ''
        for line in text.split('\n'):
            ls = line.strip()
            if ls.startswith('# ') and title == '昨日對話記錄':
                title = ls[2:].strip()
            if '來源' in ls and not src:
                src = ls.lstrip('>').strip()
        date = os.path.basename(f).replace('昨日对话记录_', '').replace('.md', '')
        rows.append('<tr><td>%s</td><td>%s</td><td>%s</td><td>%.0fK</td><td>已收錄·不入頁面</td></tr>'
                    % (B.esc(date), B.esc(title), B.esc(src[:70]), len(text) / 1000))
    body = (B.eco_nav() + '''<h1>記錄欄 · 對話留底</h1>
<p class="lead">本站對話記錄源檔<b>同步收錄於倉庫 <code>analysis/</code></b>（GitHub 可查），<b>不在頁面整篇展示</b>——避免頁面過長；全文留底於源檔，可溯源、可核對。</p>
<table class="acts"><tr><th>日期</th><th>標題</th><th>來源</th><th>大小</th><th>狀態</th></tr>'''
            + ''.join(rows) + '''</table>
<p class="note">新增記錄：把對話 md 放入 <code>analysis/</code> 並重跑 <code>python3 tools/build_jilu.py</code> 即同步。頁面不渲染全文，源檔留底可溯源。</p>''')
    html = B.page('記錄欄 · 對話留底', '對話記錄索引（源檔同步·不入頁面）', body, '記錄')
    open('jilu.html', 'w', encoding='utf-8').write(html)
    print('已生成 jilu.html（%s 字元，收錄 %d 個記錄檔）' % (len(html), len(files)))


if __name__ == '__main__':
    main()
