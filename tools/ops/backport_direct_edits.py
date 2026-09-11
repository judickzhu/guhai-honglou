#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""backport_direct_edits.py — 把手改進 HTML 的內容回填到「生成器/資料源」,消除雙源漂移

背景:工作區鎖住期間,以下兩處是直接改站點 HTML 的,生成器/資料源裡沒有:
  ① 076 回卡「中心思想」(金句 + 解碼軌)
  ② 人物檔案「賈寶玉」卡的神瑛侍者注
本腳本把它們寫進生成器資料源(冪等:已存在則跳過),之後重跑生成器即可產出,不再需要手改 HTML。

用法: python3 tools/ops/backport_direct_edits.py <tools目錄>          # dry-run 檢查
      python3 tools/ops/backport_direct_edits.py <tools目錄> --apply  # 實際寫入
"""
import json, os, sys, re

TOOLS = sys.argv[1] if len(sys.argv) > 1 else "tools"
APPLY = "--apply" in sys.argv
GEN = os.path.join(TOOLS, "build_honglou_site.py")
JINJU = os.path.join(TOOLS, "content-source", "honglou_jinju.json")
CHARS = os.path.join(TOOLS, "content-source", "honglou_characters.json")

# ① 076 中心思想 —— 解碼軌條目(生成器 CURATED 用)
DEC_076 = ('("U","【全書中心思想在此回】「贔屭朝光透，罘罳曉露屯」＝妙玉續詩十三韻——'
           '贔屭＝被棄（粵語閉翳）／朝廷失光走下坡；罘罳＝閉門反思挽救敗局、建設美好家園；'
           '義理化用岳陽樓記「先天下之憂而贔屭，後天下之樂而罘罳」；'
           '根柢是君臣之道，接《大學》明明德·親民·止於至善。不在第1回、不在第5回")')
# ① b 076 金句
JINJU_076 = ["贔屭朝光透，罘罳曉露屯", "全書中心思想（妙玉續詩十三韻）：朝光透＝朝廷失光走下坡；曉露屯＝閉門反思建設家園"]
# ② 賈寶玉檔案補注
CHARS_NOTE = ("；神瑛侍者＝寶玉前身＝胤礽——作者以神瑛侍者（上層建築視角）寫宮牆之內，非凡人視角")

def log(msg): print(("  [寫入] " if APPLY else "  [將寫] ") + msg)

def patch_generator():
    if not os.path.exists(GEN):
        print("✗ 找不到生成器:", GEN); return False
    s = open(GEN, encoding="utf-8").read()
    if "全書中心思想在此回" in s:
        print("✓ 生成器已有 076 中心思想條目,跳過"); return False
    # 整行定位:找 76:[ 起始行,再找該區塊收尾行(以 )], 結尾)
    lines = s.split('\n')
    st = None
    for i, l in enumerate(lines):
        if l.startswith('76:['):
            st = i; break
    if st is None:
        print("✗ 生成器找不到 76:[ 區塊——請人工確認結構"); return False
    ci = None
    for j in range(st, len(lines)):
        if lines[j].rstrip().endswith(')],'):
            ci = j; break
    if ci is None:
        print("✗ 生成器 76 區塊收尾未找到"); return False
    # 收尾行拆開:去掉 )], 補 , 再插入新條目 + 收尾
    lines[ci] = lines[ci].rstrip()[:-3] + '),'
    lines[ci+1:ci+1] = ['    ' + DEC_076 + '],']   # DEC 已含收尾 ),故只補 ],
    new = '\n'.join(lines)
    log(f"生成器 76:[ 區塊插入中心思想條目(行 {st+1}..{ci+1})")
    if APPLY:
        open(GEN, "w", encoding="utf-8").write(new)
        import ast; ast.parse(open(GEN, encoding="utf-8").read())
    return True

def patch_jinju():
    if not os.path.exists(JINJU):
        print("✗ 找不到", JINJU); return False
    d = json.load(open(JINJU, encoding="utf-8"))
    if "76" in d and any("贔屭朝光透" in (x[0] if isinstance(x, list) else str(x)) for x in d["76"]):
        print("✓ 金句源已有 076 中心思想,跳過"); return False
    d.setdefault("76", []).append(JINJU_076)
    log("金句源 honglou_jinju.json 加 76 條目")
    if APPLY:
        json.dump(d, open(JINJU, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return True

def patch_characters():
    if not os.path.exists(CHARS):
        print("✗ 找不到", CHARS); return False
    d = json.load(open(CHARS, encoding="utf-8"))
    if "贾宝玉" not in d:
        print("✗ 人物檔案無「贾宝玉」鍵"); return False
    if "神瑛侍者" in d["贾宝玉"].get("fanzhuan", ""):
        print("✓ 人物檔案已有神瑛侍者注,跳過"); return False
    d["贾宝玉"]["fanzhuan"] = d["贾宝玉"].get("fanzhuan", "") + CHARS_NOTE
    log("人物檔案 贾宝玉.fanzhuan 追加神瑛侍者注")
    if APPLY:
        json.dump(d, open(CHARS, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return True

def main():
    print("=== 回填手改內容到生成器/資料源 ===")
    changed = sum([patch_generator(), patch_jinju(), patch_characters()])
    print()
    if changed and not APPLY:
        print("以上為 dry-run。確認無誤後加 --apply 實際寫入。")
    elif changed:
        print(f"✓ 已完成 {changed} 處回填。接著:")
        print("  python3 tools/build_honglou_site.py && bash tools/selfcheck.sh")
    else:
        print("無需回填(皆已存在)——雙源已消除。")

if __name__ == "__main__":
    main()
