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
tools/content-mirror/          素材鏡像(備份)
tools/obsidian-kb/             Obsidian 知識庫(127 md)
tools/admin_server.py          本地後台管理員(子嗥補充審核)
```

## 生成站點
```bash
python3 tools/build_honglou_site.py     # 冪等:重跑結果一致
```
