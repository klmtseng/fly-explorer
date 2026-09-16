#!/usr/bin/env python3
"""釘住宣稱(validity-audit 第 1 步,確定性):把 content/cards.json 每個事實欄與 content/stages.json 的數字
列成表,並機器檢查 source 欄裡「像路徑的東西」是否真的存在。
輸出 audit/claims.md。exit 0 = 全部路徑存在;1 = 有缺。不驗內容是否支持宣稱(那是第 3 步人審)。"""
import json, re, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
cards = json.loads((ROOT/"content/cards.json").read_text())["cards"]
stages = json.loads((ROOT/"content/stages.json").read_text())["stages"]
rows, missing = [], []
PATH_RE = re.compile(r"(?<![\w/])(?:\.\./fly/)?(?:scripts|docs|runs|content|src|public)/[\w./-]+")
def check(src):
    hits = [h for h in PATH_RE.findall(src) if "github.com" not in src or h not in src.split("github.com",1)[1].split("(")[0]]; bad = []   # 外部 repo 的路徑不查本機
    for h in hits:
        cand = [ROOT/h, ROOT/h.replace("../", "../")]
        p = (ROOT/h) if not h.startswith("../") else (ROOT.parent/h[3:])
        p = pathlib.Path(str(p).rstrip(".;,)"))
        # runs/ 屬研究倉 ../fly/runs 或本倉 runs
        if h.startswith("../fly/"): bad.append(h + "(研究倉路徑:公開版必須自足,腳本請複製到 scripts/fly/)"); continue   # 2026-09-16 發表前置
        if not p.exists(): bad.append(h)
    return hits, bad
for c in cards:
    for f in c["facts"]:
        hits, bad = check(f["source"])
        rows.append((c["id"], f["value"], f["label"]["zh"], f["provenance"], f["source"], "缺:"+",".join(bad) if bad else ("路徑OK" if hits else "非路徑(論文/標註)")))
        missing += [(c["id"], b) for b in bad]
for s in stages:
    hits, bad = check(s.get("src",""))
    nums = re.findall(r"\d+(?:\.\d+)?\s*(?:ms|顆|%|Hz)", s.get("sub",""))
    rows.append((f"stage@{s['t']}ms", "; ".join(nums) or "(無數字)", s["zh"], "injected" if s.get("injected") else "measured", s.get("src",""), "缺:"+",".join(bad) if bad else ("路徑OK" if hits else "非路徑")))
    missing += [(f"stage@{s['t']}", b) for b in bad]
out = ["# 宣稱清單(機器產生,validity-audit 第 1 步)", "", f"卡片 {len(cards)} 張,事實 {sum(len(c['facts']) for c in cards)} 條,階段字幕 {len(stages)} 段。", "",
       "| 卡/階段 | 數值 | 標籤 | 標記 | 來源欄 | 路徑檢查 |", "|---|---|---|---|---|---|"]
out += ["| %s | %s | %s | %s | %s | %s |" % tuple(str(x).replace("|","\\|") for x in r) for r in rows]
out += ["", f"路徑缺失:{len(missing)}"] + [f"- {a}: {b}" for a, b in missing]
(ROOT/"audit/claims.md").write_text("\n".join(out)+"\n")
dups = [str(q) for q in list(ROOT.glob("public/**/cards.json")) + list(ROOT.glob("public/**/stages.json")) + list(ROOT.glob("src/**/*.json"))]
if dups: missing.append(("單一真相", "content/ 之外還有副本:" + ", ".join(dups) + "(熱審 2026-09-15:public/ 舊快照含全部撤回句)"))
print(f"facts={sum(len(c['facts']) for c in cards)} stages={len(stages)} missing_paths={len(missing)}")
for a, b in missing: print("  MISSING", a, b)
sys.exit(1 if missing else 0)
