#!/usr/bin/env python3
"""釘住宣稱(validity-audit 第 1 步,確定性):把 content/cards.json 每個事實欄與 content/stages.json 的數字
列成表,並機器檢查 source 欄裡「像路徑的東西」是否真的存在。
輸出 audit/claims.md。exit 0 = 全部路徑存在;1 = 有缺。不驗內容是否支持宣稱(那是第 3 步人審)。
--self-test(2026-09-16 VA 補):三個負向案例——來源指向不存在的檔、來源指向未公開的研究倉、content/ 之外多一份卡片副本,
三者都必須 exit 非 0。之前這支與 audit_numbers 是唯二沒有負向案例的閘門,而 README 宣稱「每支都有」。"""
import json, re, pathlib, sys, os, copy, tempfile, subprocess
ROOT = pathlib.Path(__file__).resolve().parent.parent
CARDS_PATH = pathlib.Path(os.environ.get("AUDIT_CLAIMS_CARDS", ROOT/"content/cards.json"))
if "--self-test" in sys.argv:
    base = json.loads((ROOT/"content/cards.json").read_text()); me = pathlib.Path(__file__).resolve()
    def run(mutate, label):
        v = copy.deepcopy(base); mutate(v)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump(v, fh, ensure_ascii=False); tmp = fh.name
        r = subprocess.run([sys.executable, str(me)], env=dict(os.environ, AUDIT_CLAIMS_CARDS=tmp), capture_output=True, text=True)
        ok = r.returncode != 0
        print(f"  {'✓' if ok else '✗'} {label}: exit {r.returncode}(預期非 0)")
        return ok
    def m_missing(v): v["cards"][0]["facts"][0]["source"] = "scripts/這支不存在.py"
    def m_private(v): v["cards"][0]["facts"][0]["source"] = "../fly/scripts/io_inventory.py"   # 未公開的研究倉路徑
    r0 = subprocess.run([sys.executable, str(me)], capture_output=True, text=True)
    print(f"  {'✓' if r0.returncode == 0 else '✗'} 正向:未改動的內容 exit {r0.returncode}(預期 0)")
    res = [r0.returncode == 0, run(m_missing, "負向:來源指向不存在的檔"), run(m_private, "負向:來源指向未公開的研究倉")]
    print("SELF-TEST", "PASS" if all(res) else "FAIL"); sys.exit(0 if all(res) else 1)
cards = json.loads(CARDS_PATH.read_text())["cards"]
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
# 卡片張數的覆蓋宣稱:任何地方寫「N 張卡 / N cards」都必須等於實際張數
# (2026-09-17:加了一張「模型學不會東西」後,index.html/README/宣傳稿三處還寫著 33,使用者的提問才讓它曝光)
COUNT_RE = re.compile(r"(\d+)\s*(?:張(?:說明)?卡|(?:explanation\s+)?cards)")
for f in [ROOT/"index.html", ROOT/"README.md"] + sorted((ROOT/"docs").glob("*.md")):
    if not f.exists(): continue
    # 歸檔的審查報告在講「哪幾張卡有問題」,不是在宣稱總數,整份豁免(與 retraction_lint 同一個原則)
    if f.name.startswith("review_") or f.name.startswith("promo_"): continue
    for i, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        for m in COUNT_RE.finditer(line):
            if int(m.group(1)) != len(cards):
                missing.append((f"{f.relative_to(ROOT)}:{i}", f"寫著 {m.group(1)} 張卡,實際 {len(cards)} 張"))
dups = [str(q) for q in list(ROOT.glob("public/**/cards.json")) + list(ROOT.glob("public/**/stages.json")) + list(ROOT.glob("src/**/*.json"))]
if dups: missing.append(("單一真相", "content/ 之外還有副本:" + ", ".join(dups) + "(熱審 2026-09-15:public/ 舊快照含全部撤回句)"))
print(f"facts={sum(len(c['facts']) for c in cards)} stages={len(stages)} missing_paths={len(missing)}")
for a, b in missing: print("  MISSING", a, b)
sys.exit(1 if missing else 0)
