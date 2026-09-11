# 方案 B 操作手冊 · 紅樓站獨立(guhai-honglou)
2026-09-11 ｜ 腳本已用假工作區實測通過

## 前置(一次性)
```bash
# 0. 解鎖工作區後,建議先移出 ~/Downloads
mkdir -p ~/dev && mv ~/Downloads/电子书ipa ~/dev/
export WS=~/dev/电子书ipa

# 1. 確認舊倉庫乾淨
git -C $WS/网站 status --short          # 應為空或僅預期改動
git -C $WS/网站 log --oneline -1        # 應為 0929f08b 或更新

# 2. GitHub 網頁:新建 public 空倉庫 guhai-honglou(勿勾 README)
cd ~/dev && git clone https://github.com/judickzhu/guhai-honglou.git hl-new
export NEW=~/dev/hl-new

# 3. 備份(回滾用)
git -C $WS/网站 clone --mirror . ~/dev/guhai-backup.git
```

## 執行遷移(腳本已實測)
```bash
bash /tmp/migrate_b.sh $WS $NEW            # 先 Dry-run 看清單
bash /tmp/migrate_b.sh $WS $NEW --apply    # 確認後執行
```
腳本會做:① 站點檔(honglou/* → 新倉庫根,排除 *.pdf) ② tools/(admin_server、content-mirror、obsidian-kb、assets、gen_*) ③ 生成器 → tools/ + 素材 → tools/content-source/ ④ **改寫生成器路徑**(實測:ROOT=倉庫根、SRC=tools/content-source、OUT=倉庫根) ⑤ 寫 .gitignore ⑥ 跑生成器 + 冪等檢查

## 上線新站
```bash
cd $NEW
git add -A
git commit -m "紅樓站獨立上線(自 guhai 分離)"
git push origin main
```
GitHub 網頁:新倉庫 → **Settings → Pages → Source: main / (root)** → 網址
**https://judickzhu.github.io/guhai-honglou/**

## 舊站留跳轉(URL 不斷)
在舊倉庫把 `honglou/index.html` 換成跳轉頁:
```html
<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8">
<title>一起讀紅樓白話(已移至新網址)</title>
<meta http-equiv="refresh" content="0;url=https://judickzhu.github.io/guhai-honglou/">
<link rel="canonical" href="https://judickzhu.github.io/guhai-honglou/">
</head><body><p>本站已移至
<a href="https://judickzhu.github.io/guhai-honglou/">https://judickzhu.github.io/guhai-honglou/</a></p>
</body></html>
```
並刪除舊倉庫 `honglou/` 其餘檔案(已遷走;歷史仍保留)。

## 清理舊倉庫內部資料
```bash
bash /tmp/redact_internal.sh $WS/网站            # Dry-run
bash /tmp/redact_internal.sh $WS/网站 --apply    # 搬移到 _internal_private/(已 gitignore)
cd $WS/网站 && git add -A && git commit -m "安全:內部資料移出公開倉庫 + robots 禁抓" && git push
```

## 大檔策略
```bash
# 60MB PDF:不走 git → Releases
#   新倉庫 Releases 建 tag jiaxu-epub(或 base-pdf)上傳 dc-honglou-base-120.pdf
#   站內下載連結改指 Releases URL
# 甲戌本 482 圖(42MB):保留(讀者需要);如嫌大再轉 Releases
```

## 驗證清單
```bash
# 新站可用性
for p in "" framework.html characters.html shixi.html pingyu.html mapping.html qa.html jiaxu.html chapters/001.html chapters/076.html; do
  curl -s -o /dev/null -w "%{http_code} /$p\n" "https://judickzhu.github.io/guhai-honglou/$p"
done
# 舊 URL 跳轉
curl -s "https://judickzhu.github.io/guhai/honglou/index.html" | grep -c "guhai-honglou"
# 生成器冪等(新倉庫)
cd $NEW && python3 tools/build_honglou_site.py >/dev/null && git status --short | wc -l   # 應 0
# 斷鏈
python3 - <<'EOF'
import re,glob,os
bad=[]
for f in glob.glob('**/*.html', recursive=True):
    d=os.path.dirname(f)
    for m in re.findall(r'(?:href|src)="([^"]+)"', open(f,encoding='utf-8').read()):
        if m.startswith(('http','#','mailto')): continue
        p=m.split('#')[0]
        if p and not os.path.exists(os.path.normpath(os.path.join(d,p))): bad.append((f,m))
print('斷鏈:', len(bad), bad[:5])
EOF
```

## 回滾
```bash
# 新站有問題 → 舊倉庫還原跳轉頁為原站(history 仍在)
git -C $WS/网站 checkout HEAD~1 -- honglou/
git -C $WS/网站 push
# 或從 mirror 備份還原
```

## 可直接做的安全項(不需解鎖)
1. 輪換 ima KB key
2. GitHub 網頁刪:`v31_prompt.txt`、`DCOGAI開發需求單.md`、`DC姐姐V4.0第二階段_20種人格模型主檔.md`、`DC姐姐X帳號內容包v1~v3.md`、`backend_snapshot_20260907_*.json`
3. `robots.txt` → `User-agent: *` / `Disallow: /`;刪 `sitemap.xml`

## 待辦(遷移後我接手)
- 「神瑛侍者」解碼(已寫入生成器,待生成上線)
- Obsidian 知識庫在新倉庫重新產出
- (可選)`git filter-repo` 清舊倉庫歷史
