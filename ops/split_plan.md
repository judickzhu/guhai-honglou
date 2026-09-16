# 拆仓方案 · 红樓站与商业站分域
日期:2026-09-11 ｜ 前置:待工作区解锁后执行

## 一、现状与约束
- 仓库 `judickzhu/guhai`:**public · 206MB · Pages 已启用**
- 根 URL `https://judickzhu.github.io/guhai/` = **股海雙書知識庫**(商业,DCOGAI/DC姐姐)
- 红樓 URL `https://judickzhu.github.io/guhai/honglou/` = **一起讀紅樓白話**(已发布,有外链与收录)
- 红樓的**生成器与素材只在本地**(未版本化)→ 单点故障
- 商业站正常运作**依赖**仓库内许多 json/js(kb-books.json、kb-data_simplified.json、search-data.js、phenomena.html 等)→ 不可盲删

## 二、三方案对比

| | 方案 A:商业站私有化 | **方案 B:红樓独立(推荐)** | 方案 C:红樓占根 |
|---|---|---|---|
| 做法 | 新建 private repo 存商业源文件,公开 repo 只留红樓 | 新建 public repo `guhai-honglou`,红樓提升为根 | 新建 repo 存商业站,`guhai` 根改为红樓 |
| 红樓新 URL | 不变 `/guhai/honglou/` | `/guhai-honglou/` | `/guhai/` |
| 商业站风险 | 中(需搬商业站) | **零(不动)** | 中(需搬商业站) |
| 分域干净度 | 中 | **高** | 高 |
| URL 断链 | 无 | 有(需跳转) | 有(需跳转) |
| 主要代价 | 公开 repo 仍需清内部资料+清历史 | 红樓 URL 变更 | 商业站迁移工作量大 |

### 推荐:**方案 B**(红樓独立),理由
1. 商业站**完全不动** → 零风险
2. 红樓自成一体 → 生成器/素材/工具**一起版本化**,消除单点故障
3. 两个读者群彻底分开,红樓读者不会串门看到 DCOGAI 资料
4. 代价仅 URL 变更,可用**跳转页**兜住旧链接

### 若坚持 URL 不变 → 用 **B′ 变体**
红樓独立 repo 后,在原 `guhai/honglou/index.html` 放一个跳转页(meta refresh → 新站),旧链接与收录均可用。

## 三、B 方案执行步骤(解锁后照做)

### Step 0 准备
```bash
cd ~/dev/电子书ipa            # 解锁后建议移出 ~/Downloads
git -C 网站 status            # 确认干净
```

### Step 1 建新仓库
GitHub 网页新建 **public** repo `guhai-honglou`(勿勾 README)
```bash
cd ~/dev
git clone https://github.com/judickzhu/guhai-honglou.git hl-new
cd hl-new
```

### Step 2 提取红樓为根
```bash
cp -R ~/dev/电子书ipa/网站/honglou/* .        # 站点文件(html/css/js/chapters/jiaxu/funding)
```
排除大文件(见 Step 6),然后:
```bash
mkdir -p tools
cp ~/dev/电子书ipa/build_honglou_site.py tools/
cp ~/dev/电子书ipa/build_obsidian_kb.py   tools/
cp ~/dev/电子书ipa/honglou_*.json         tools/content-source/   # 素材(生成器读取源)
cp -R ~/dev/电子书ipa/网站/tools/*        tools/                  # admin_server/gen_*/content-mirror/obsidian-kb
```

### Step 3 路径适配
生成器 `OUT = ROOT/網站/honglou`、素材读 `ROOT/honglou_*.json` → 新仓库里改为:
```python
OUT  = os.path.join(ROOT, ".")                    # 站点根
# 素材路径按 tools/content-source/ 调整
```
站内链接用 `PREFIX` 相对路径,已设计好 → **HTML 无需改**。

### Step 4 旧站留跳转
在 `guhai` 仓库改 `honglou/index.html`:
```html
<!DOCTYPE html><meta charset="utf-8">
<meta http-equiv="refresh" content="0;url=https://judickzhu.github.io/guhai-honglou/">
<link rel="canonical" href="https://judickzhu.github.io/guhai-honglou/">
<p>一起讀紅樓白話已移至 <a href="https://judickzhu.github.io/guhai-honglou/">新網址</a>。</p>
```

### Step 5 商业站清理内部资料
```bash
bash /tmp/redact_internal.sh            # 先 Dry-run 看清单
bash /tmp/redact_internal.sh --apply    # 确认后执行
git add -A && git commit -m "安全:内部资料移出公开仓库"
git push
```
(该脚本实测:只搬移不在站点依赖清单内的文件;robots→Disallow;生成器入库)

### Step 6 大文件策略
- 60MB `dc-honglou-base-120.pdf` → 不放 git,走 **GitHub Releases**(与 EPUB 同法)
- 甲戌本 482 图(42MB)→ 保留(站点读者需要)或转 Releases + 外链
- 新 repo `.gitignore`:`*.pdf`、`*.epub`、`*.zip`、`.DS_Store`

### Step 7 验证清单
- [ ] 新站首页/120 卡/世系/脂批/甲戌本翻页/EPUB 链接 全 200
- [ ] 零断链(内置断链检查脚本)
- [ ] 生成器在新路径跑通 + **幂等 0**
- [ ] 旧 URL 跳转生效
- [ ] `robots.txt` 允许红樓抓取;提交新 sitemap(仅红樓)
- [ ] 更新引用:Obsidian 库、README、站内 footer

### Step 8(可选)清历史
```bash
git filter-repo --path v31_prompt.txt --path-glob 'v3*_*' --path-glob 'DC姐姐*' --path-glob 'DCOGAI*' --invert-paths
git push --force
```
⚠ 重写历史 → 所有协作者需重新 clone;已在本地 clone 过的人仍保留旧对象。

## 四、风险与回滚
| 风险 | 缓解 |
|---|---|
| 新站 URL 变更导致外链失效 | Step 4 跳转页 + canonical |
| 生成器路径改错导致站点空 | 先在新 repo 跑生成器,验证幂等 0 再推 |
| 搬移脚本误伤商业站 | 脚本 Dry-run 默认;实测保留站点依赖文件 |
| 历史清理强推事故 | 先 `git clone --mirror` 备份,再执行 |

## 五、立即可做(不需解锁)
1. GitHub 新建 `guhai-honglou` 空仓库(public)
2. 轮换 ima KB key
3. 网页删最敏感文件:`v31_prompt.txt`、`DCOGAI開發需求單.md`、`DC姐姐V4.0第二階段_20種人格模型主檔.md`、`DC姐姐X帳號內容包v1~v3.md`、`backend_snapshot_*.json`
4. `robots.txt` → `Disallow: /`
