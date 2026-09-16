#!/usr/bin/env python3
"""C2 事實正確性的機器部分:kid/more(zh)文字裡出現的每個數字,是否能在(a)同卡事實欄 (b)本倉 docs/ 記錄
(c)研究倉 ../fly 的 PROGRESS/CLAUDE/docs 裡找到同一個數字字串。找不到的列出來給人審——它不判對錯,只找「沒有出處的數字」。"""
import os, json, re, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
cards = json.loads((ROOT/"content/cards.json").read_text())["cards"]
corpus = ""
FLY = ROOT.parent/"fly"   # 研究倉(不公開)。NO_FLY=1 時不讀它,模擬公開倉的自足檢查:網站上每個數字都要在本倉找得到出處
FLY_SRC = [] if os.environ.get("NO_FLY") else (list(FLY.glob("*.md")) + list((FLY/"docs").glob("*.md")) + list((FLY/"runs").glob("*.json"))
                                               + list((FLY/"runs").glob("*.txt")) + list((FLY/"runs").glob("**/*.md")))
SRC = list((ROOT/"docs").glob("*.md")) + [ROOT/"CLAUDE.md", ROOT/"PROGRESS.md"] + list((ROOT/"scripts/fly/out").glob("*.json")) + FLY_SRC   # scripts/fly/out:自研究倉複製的量測輸出
for p in SRC:
    if p.exists(): corpus += p.read_text(errors="ignore")
corpus_n = corpus.replace(",", "")
NUM = re.compile(r"\d[\d,\.]*")
CN = {"零":0,"一":1,"二":2,"兩":2,"三":3,"四":4,"五":5,"六":6,"七":7,"八":8,"九":9}
def cn2num(s):
    """中文數詞 → 阿拉伯數字(十六萬五千 → 165000;八百六十億 → 86000000000)。熱審 2026-09-15:原本只認阿拉伯數字"""
    total, section, num = 0, 0, 0
    for ch in s:
        if ch in CN: num = CN[ch]
        elif ch == "十": section += (num or 1) * 10; num = 0
        elif ch == "百": section += (num or 1) * 100; num = 0
        elif ch == "千": section += (num or 1) * 1000; num = 0
        elif ch == "萬": total += (section + num) * 10_000; section = num = 0
        elif ch == "億": total += (section + num) * 100_000_000; section = num = 0
    return total + section + num
CNNUM = re.compile(r"[零一二兩三四五六七八九十百千萬億]{2,}")
TRIVIAL = {"1","2","3","4","5","6","7","8","9","10","11","12","14","100"}
orphans = []
for c in cards:
    facts = " ".join(f["value"] + " " + f.get("value_en", "") + " " + f["label"]["zh"] + " " + f["label"]["en"] + " " + f["source"] for f in c["facts"]).replace(",", "")
    for layer, lg in (("kid", "zh"), ("more", "zh"), ("kid", "en"), ("more", "en")):   # 英文層一樣掃(2026-09-16 起)
        for n in [str(cn2num(m)) for m in CNNUM.findall(c[layer][lg]) if cn2num(m) >= 1000] + NUM.findall(c[layer][lg]):
            n = n.strip(".,")
            if n in TRIVIAL or not n: continue
            nn = n.replace(",", "")
            if nn in facts or nn in corpus_n: continue
            # 四捨五入的近似值(170≈169、1,700≈1,747、114.9≈114.88):找同數量級±3% 的數字是否在事實欄/語料
            try:
                v = float(nn)
                cand = re.findall(r"\d[\d\.]*", facts) 
                if any(abs(float(x) - v) <= 0.03 * max(v, 1) for x in cand if x.replace(".","",1).isdigit()): continue
            except ValueError: pass
            orphans.append((c["id"], layer, n))
print(f"cards={len(cards)} orphan_numbers={len(orphans)}")
for o in orphans: print("  ", *o)
