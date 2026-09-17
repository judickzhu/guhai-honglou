# 交接狀態檔 · 一起讀紅樓白話(2026-09-11 更新:方案B已執行)

## 一、已完成(本日,經 gh 執行,未等工作區解鎖)
| 項 | 狀態 |
|---|---|
| **新站獨立** | ✅ https://judickzhu.github.io/guhai-honglou/(public repo `guhai-honglou`) |
| 遷移內容 | honglou/ 全站 624 文件(43MB,排除60MB PDF)→ 新倉庫根;README/robots/sitemap(131 URL) |
| 甲戌本 | ✅ 482 頁翻頁正常(pg-001/pg-482 全 200) |
| 章卡/欄目 | ✅ 全部 200(index/framework/characters/shixi/pingyu/mapping/qa/jiaxu/funding + 000/001/076/120) |
| 斷鏈 | ✅ 0 |
| **舊址跳轉** | ✅ /guhai/honglou/index.html → 新站(meta refresh + canonical) |
| **robots 禁抓** | ✅ /guhai/robots.txt → Disallow: / |
| **敏感文件刪除** | ✅ 8 個已刪並 404(v31_prompt.txt/DCOGAI開發需求單/DC姐姐人格主檔/X帳號內容包×3/backend_snapshot×2) |
| EPUB | ✅ 遷至新倉庫 Releases(jiaxu-epub,43MB 可下載),jiaxu.html 鏈接已改指 |
| PDF(60MB) | 上傳新倉庫 Releases(base-pdf)後台中 |

## 二、待辦(需工作區解鎖,~/Downloads 仍被 TCC 鎖)
1. **神瑛侍者解碼**:已寫入 `build_honglou_site.py`(第1回+子嗥),**未生成/未提交**——解鎖後跑生成器,或把生成器 copy 進新倉庫 tools/ 後在新站補上
2. **人物檔案(賈寶玉)補注**「神瑛侍者＝寶玉前身＝胤礽…」(honglou_characters.json 寫入被拒)
3. **生成器進新倉庫 tools/** + content-source 素材進新倉庫(消除單點故障;目前新站是「成品站點」,無生成器)
4. 新站與舊站內容同步後,可選:舊倉庫 honglou/ 其餘文件刪除(只留跳轉)
5. (可選)git filter-repo 清舊倉庫歷史

## 三、安全(已做 vs 待做)
- ✅ robots Disallow、敏感文件刪除、新站自足(EPUB 在新倉庫)
- 🔴 **ima KB key 輪換(用戶側)**:`tools/gen_yuanwen_from_ima.py:22` 硬編碼 key 曾公開,須在 ima 後台撤銷
- ⚠️ 舊倉庫歷史仍含已刪文件(需 filter-repo 才徹底清除;現實上假設已泄露)

## 四、工件(/tmp,重開機即失——解鎖後收進新倉庫 tools/)
runbook_b.md / migrate_b.sh / patch_generator_paths.py / redact_internal.sh / verify_new_site.sh / gen_sitemap.py / audit_20260911.md / split_plan.md / HANDOFF.md / newrepo_files/

## 五、解鎖後
```bash
mkdir -p ~/dev && mv ~/Downloads/电子书ipa ~/dev/
cp /tmp/*.md /tmp/*.sh /tmp/*.py ~/dev/电子书ipa/網站/tools/ 2>/dev/null
# 生成器入新倉庫
cp ~/dev/电子书ipa/build_honglou_site.py /tmp/hl_new/tools/
cp ~/dev/电子书ipa/honglou_*.json /tmp/hl_new/tools/content-source/
python3 /tmp/patch_generator_paths.py /tmp/hl_new/tools/build_honglou_site.py
cd /tmp/hl_new && python3 tools/build_honglou_site.py && git add -A && git commit -m "生成器入庫+素材入庫(神瑛侍者等)" && git push
# 驗證
bash /tmp/verify_new_site.sh
```

## 追加(2026-09-11 13:xx)
- ✅ 神瑛侍者解碼已上线新站(001.html + 子嗥 glyph 18条;push cb1e861)——不经工作区,直接改新站成品文件
- ⏳ 第3项 filter-repo 清旧仓历史:filter-repo 已装(/tmp/frvenv);镜像克隆 bash-2 后台中
- 待办剩余:生成器入库(需解锁);ima key 轮换(用户侧)

## 追加2(2026-09-11 完成)
- ✅ **第2項 神瑛侍者**:已上線新站(001.html + 子嗥 glyph 18條);**生成器入庫仍待工作區解鎖**
- ✅ **第3項 舊倉歷史清理(完成)**:
  - git-filter-repo 清除歷史中所有敏感檔(v31_prompt/DCOGAI*/DC姐姐*/backend_snapshot*/測試結果/日誌)+ `honglou/*`
  - 倉庫 210MB → 105MB;重寫 416 提交
  - 重建 `honglou/index.html` 跳轉頁(舊深鏈 404,新站為正典)
  - **強推成功**:`+ 2dbeeafc...badfa592 (forced update)`,遠端 HEAD = badfa592
  - 核驗:歷史中敏感檔出現 **0 次**;舊站根 200;跳轉 200;新站 200;敏感檔 404
  - 商業站完整(HEAD 212 檔,index/style/app/kb/dc-kb/phenomena/acts/checklist/mapping/framework/robots 全在)
- **遺留**:①生成器入庫(需解鎖)②ima KB key 輪換(用戶側)③舊深鏈 404(已接受)
- /tmp 已清理(鏡像/下載/venv 刪除);保留 hl_new(新站工作副本 86M)+ 9 個工件檔

## 追加3(2026-09-11 自检发现并修复)
- 🐛 **自检脚本抓出真问题**:076 回卡缺「罘罳」「朝光透」「中心思想」——**中心思想句所在回,卡上反而没有它**
  - 已补:本回金句加「贔屭朝光透，罘罳曉露屯」+ 解码轨加中心思想条(含三层:字面/义理/根柢)
- ✅ 贾宝玉档案卡补「神瑛侍者＝寶玉前身＝胤礽——作者以神瑛侍者(上層建築視角)寫宮牆之內」
- ✅ 治理工件入库:`tools/ops/`(HANDOFF/审计报告/拆仓手册/迁移脚本/验证脚本/sitemap工具)
- ✅ 自检脚本 `tools/selfcheck.sh`(断链/子嗥JSON/8项关键内容/生成器幂等)——现全绿
- push: b8123c0

## 追加4(2026-09-11 自检强化)
- ✅ 新增 `tools/completeness_check.py`:120 回卡六字段齐全 + 「已有解碼素材/待解碼」标记与内容一致 + 子嗥(109 refs)/检索(128 urls)引用完整性
- ✅ 已接入 `tools/selfcheck.sh`(第3b步);**扫描有效性已验证**(注入坏引用 chapters/999.html → 成功抓到 → 还原)
- 📊 扫描结果:120 卡 · 已有解碼 54(全有内容)· 待解碼 66 · 金句 18 · 脂批 26 · 詩詞 35 · **問題 0**
- ✅ README 补「自检与运维」+「编辑纪律」(改 JSON 勿手改 HTML;每次改后跑 selfcheck)

## 追加5(2026-09-11 第1项部分完成)
- ✅ **資料源入新倉** `tools/content-source/`(11 個素材 JSON——生成器讀取源,終於進版本管理)
- ✅ **配套工具入新倉**:admin_server.py / build_obsidian_kb.py / gen_yuanwen_json.py / merge_yuanwen_pdfs.py / assets/ / README.md
- ✅ **Obsidian 知識庫入新倉** `tools/obsidian-kb/`(127 md)
- 🔒 **安全**:`gen_yuanwen_from_ima.py` 已消毒——移除硬編碼 KB key,改讀 `~/.config/ima/kb_id`(驗證無殘留)
- ✅ tools/README 說明:佈局 / **待補主生成器** / 編輯紀律 / 已知雙源
- ✅ 自檢修正:斷鏈掃描排除 `tools/`(404.html 模板非站點頁,曾致 2 個假斷鏈)
- ⏸ **仍待**:主生成器 `build_honglou_site.py`(在鎖住的工作區裡,唯一未入庫項)

## 追加6(2026-09-11 ✅ 第1項完成——單點故障消除)
**觸發**:工作區權限部分恢復(生成器 103KB/964 行 + 3 個素材可讀)→ 立刻搶救並完成入庫。

| 步驟 | 結果 |
|---|---|
| 生成器入庫 | ✅ `tools/build_honglou_site.py`(964 行,唯一真源) |
| 路徑改寫 | ✅ 12 個常量 → ROOT=倉庫根 / SRC=tools/content-source / OUT=倉庫根 |
| 素材刷新 | ✅ 搶救到的 char_review/poem/yuanwen 刷新 content-source(其餘沿用鏡像) |
| **雙源回填** | ✅ 076 中心思想 → 生成器 CURATED(207-211 行);神瑛侍者 → 賈寶玉檔案 + 金句源 |
| 生成器跑通 | ✅ 產物與現站差異僅 **7 文件 / 10 增 6 刪**(格式歸併,內容零丟失) |
| **冪等** | ✅ 提交後再跑 **差異數 0** |
| 自檢 | ✅ 全部通過(含生成器冪等 0) |
| 線上 | ✅ 076 中心思想/characters 神瑛侍者/zi-hao 全正常;生成器已在倉庫 |

**成果**:新倉現為**完整可重跑的自足站**——生成器(真源)+ 素材 + 自檢 + Obsidian 庫 + 後台 + 運維文檔,雙源隱患消除,單點故障不再存在。
push: 14e8858

## 追加7(2026-09-11 工作区完全可读·数据确认)
- ✅ 工作区权限**完全恢复**:9 个素材 + 总纲(3.2MB)+ ima_sync + 启动器全部抢救
- ✅ **数据确认**:仓库 content-source 即权威最新版(7/8 与工作区相同;jinju.json 工作区反而旧,勿再刷新)
- ✅ 总纲 `红楼梦解读总纲_整理版.md`(3.2MB)入库 tools/ops/(此前未入任何仓库)
- 🔒 **ima_sync.py 含凭证,不入库**(保留在 /tmp/salvage + 工作区;注意轮换 key)
- 後台管理員.command 已入库(参考)

## 追加8(2026-09-11 語料聲明)
- ⚠️ 总纲(红楼梦解读总纲_整理版.md)= **AI整理版,含錯誤,待修正**——已加警示头;站點為準,衝突以站點為準
- 修正方式:日後逐條對照抄本原文/脂批/版本(原文三層+核對)

## 追加9(2026-09-12 成書三環節+近期解碼)
- ✅ **第76回「問妙玉修改的如何」＝成書過程終極交代**:黛玉=胤礽(修改者)、湘雲=胤祥(旁證)、妙玉=順治(舊有材料提供者+最終審批者)——修正順治舊有《風月寶鑑》加入九子奪嫡親身經歷,妙玉續詩收尾=順治確認定稿。**成書三環節:一芹(胤礽寫)→一脂(胤祥批)→審批(順治定稿)**;「修改」對應第1回「編述一集」(編非作)
- ✅ 近期入站:皇統脈絡(關外寫起+76回聯詩時間線對齊)、神話框架=遮擋、石頭記=石刻歷史、鸚哥學舌=一芹一脂、通靈=被廢後反思通咗、香菱學詩=胤祥吸取教訓、書中教讀
- ✅ 全站健康檢查:12/12 頁面 200;遠端 HEAD 396edc1
- ⚠️ Hindsight 記憶服務未運行(127.0.0.1:9077 ECONNREFUSED)——本檔即持久層,服務恢復後可補錄
- 🔧 工具:`tools/ops/gh_push.sh` 已實測多次(git 被 Xcode 門禁時的 REST 提交備援)
