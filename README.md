# 一起讀紅樓白話

《紅樓夢》逐回解讀網站——**表層閨閣之事,裡層宮牆之內**。

- 站點:<https://judickzhu.github.io/guhai-honglou/>
- 中心思想(第76回妙玉續詩):「贔屭朝光透,罘罳曉露屯」
- 方法:只讀九子奪嫡還原的真相,只對書中的白話文字;不索隱猜謎,對比版本差異(甲戌本/庚辰本/蒙古王府本/程乙本)
- 直讀之解碼皆經資料庫核對(史實/脂批/字義),分級標註 ✅有據 / ⚠️推斷待核
- 邊界:粵語解碼在紅學主流無話語權;本站不求推翻紅學,唯補其未讀之層

## 結構
```
/                 站點根(生成產物)
chapters/         120 回卡片
jiaxu/            甲戌本 482 頁影印
tools/build_honglou_site.py    站點生成器(唯一真源)
tools/content-source/          素材(honglou_*.json,生成器讀取源)
tools/obsidian-kb/             Obsidian 知識庫(127 md,由 build_obsidian_kb.py 生成)
tools/build_obsidian_kb.py     Obsidian 知識庫生成器(讀 content-source,寫 obsidian-kb)
tools/build_jilu.py / build_jinghua.py   記錄頁 / 深度精華頁生成器
tools/completeness_check.py    回卡完整性檢查
tools/gen_yuanwen_json.py      原文(無標點) JSON 生成
tools/mine_user_material.py    逐回素材挖掘(只取提問者原話,排除 AI 輸出;--chapter/--kw/--stats)
tools/admin_server.py          本地後台管理員(子嗥補充審核)
tools/ops/                     治理文檔(HANDOFF 交接檔、安全審計、拆倉手冊、遷移/驗證腳本)
tools/sync_push.py / update.sh 發布 / 更新輔助
```

## 生成站點（一鍵迭代）
```bash
bash tools/update.sh "commit message"   # 一鍵：四生成器 → 自檢 → 提交 → 直推
```
流程：改源檔（`tools/content-source/*.json`、`analysis/*.md`）→ 跑 update.sh → GitHub Pages 約 1 分鐘後生效。
單跑生成器（update.sh 已含全部四個，漏跑任一會令該頁過時）：
```bash
python3 tools/build_honglou_site.py   # 主站：首頁/框架/人物/映射/脂批/世系/問答/留言/字考/卡/目錄/檢索/sitemap
python3 tools/build_jilu.py           # 記錄欄（索引）
python3 tools/build_jinghua.py        # 深度精華
python3 tools/build_obsidian_kb.py    # Obsidian 知識庫
```

## 自檢與運維
```bash
bash tools/selfcheck.sh          # 一鍵自檢:斷鏈/子嗥JSON/關鍵內容/120回卡完整性/生成器冪等
python3 tools/completeness_check.py .   # 單跑:回卡六字段+標記一致性+引用完整性
```
`tools/ops/` 收存治理文檔(HANDOFF 交接檔、安全審計報告、拆倉手冊、遷移/驗證腳本)。

## 編輯紀律
- 內容改動**優先改資料源**(`tools/content-source/*.json`),再重跑生成器;**不要手工改 HTML**(重跑會被覆蓋)
- 手工改 HTML 只限生成器不管的獨立頁(如 `jiaxu.html`)
- 每次改動後跑 `tools/selfcheck.sh`,全綠才提交

## 解碼素材判定準則(2026-10 定)
- 入「解碼軌」者,必須是**歷史對位**(人物/事件↔九子奪嫡)或**字音字形/拆字**的判斷。
- **不計入**者:純劇情概述、文學象徵評論(無歷史映射)、表格碎片、研究清單等 AI 雜訊——
  此類回目誠實標「待解碼」,不硬編充數。
- 挖掘素材只取**提問者原話**(`tools/mine_user_material.py`,排除 AI 輸出);每條附「总纲 L行號」以便回查。
- 每回皆標**幕**;雙軌(文學軌/解碼軌)分列不混寫。
