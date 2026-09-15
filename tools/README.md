# tools/ — 生成、自檢與運維

## 目錄
| 路徑 | 用途 |
|---|---|
| `selfcheck.sh` | **一鍵自檢**:斷鏈 / 子嗥JSON語法 / 關鍵內容 / 120回卡完整性 / 生成器冪等 |
| `completeness_check.py` | 120 回卡完整性:六字段齊全 + 標記一致性 + 引用完整性(子嗥109/檢索128) |
| `content-source/*.json` | **內容資料源**(生成器讀取源):人物檔案、原文、脂批、詩詞、金句、逐回素材、問答回饋 |
| `content-mirror/*.json` | 資料鏡像(備份用) |
| `obsidian-kb/` | Obsidian 知識庫(127 md,含 00-總覽/01-人物/02-手法/03-世系/04-脂批/05-金句/06-體系定位 + 逐回) |
| `admin_server.py` | 本地後台管理員(子嗥補充審核,127.0.0.1:8701) |
| `build_obsidian_kb.py` | 由 content-source 產出 obsidian-kb/ |
| `gen_yuanwen_*.py` / `merge_yuanwen_pdfs.py` | 原文管線(從 ima 分冊 PDF 抽字 → JSON;合集 PDF) |
| `ops/` | 治理文檔:HANDOFF 交接檔、安全審計報告、拆倉手冊、遷移/驗證腳本 |

## ⚠️ 待補:主生成器
`build_honglou_site.py`(站點生成器,唯一真源)**尚未入庫**——它在被 macOS 鎖住的舊工作區
(`~/Downloads/电子书ipa/`)裡。解鎖後第一件事:
```bash
cp ~/dev/电子书ipa/build_honglou_site.py tools/
python3 tools/build_honglou_site.py      # 跑通 + 冪等 0
bash tools/selfcheck.sh                  # 全綠才提交
```
**在那之前**:站點是「成品站」,小改動可直接改 HTML/JS(但要同步改資料源,避免雙源漂移)。

## 編輯紀律
1. 內容改動**優先改 `content-source/*.json`**,再重跑生成器
2. **不要手工改生成器會覆蓋的頁面**(index/欄目/章卡/search-data/zi-hao-data)
3. 手改只限生成器不管的獨立頁(`jiaxu.html` 等)
4. 每次改動後跑 `bash tools/selfcheck.sh`,全綠才提交
5. **憑證不進倉庫**:ima 憑證讀 `~/.config/ima/`(client_id / api_key / kb_id)

## 已知雙源(待消除)
`神瑛侍者`(第1回)、`076 中心思想` 兩處內容目前**同時存在於**「生成器程式碼」與「本站 HTML/JS」。
兩邊內容一致(已驗證),但日後改一處須同步另一處——主生成器入庫 + 重跑後即可消除。

## ⚠️ 語料底稿聲明
- `ops/红楼梦解读总纲_整理版.md` = **AI 整理版,含錯誤,待逐條修正**(提問者 2026-09-11)
- 站點內容不以此為準;凡衝突,以站點(原文三層+核對)為準
