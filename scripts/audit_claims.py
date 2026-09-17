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
    EMPTY = ROOT / "scripts/_empty_selftest.py"   # 自測用的空檔,跑完就刪(見下方 finally)
    def m_empty(v):
        EMPTY.write_text("")
        v["cards"][0]["facts"][0]["source"] = "scripts/_empty_selftest.py"
    def m_noen(v):
        for x in v["cards"]:
            for f in x["facts"]:
                if "source_en" in f: f.pop("source_en"); return
    def m_halfen(v):
        for x in v["cards"]:
            for f in x["facts"]:
                if "source_en" in f: f["source_en"] = "abstract 親讀"; return
    res = [r0.returncode == 0, run(m_missing, "負向:來源指向不存在的檔"), run(m_private, "負向:來源指向未公開的研究倉"),
           run(m_empty, "負向:出處指向空檔"), run(m_noen, "負向:中文出處缺 source_en"), run(m_halfen, "負向:source_en 沒翻完,仍含中文")]
    EMPTY.unlink(missing_ok=True)
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
        elif p.is_file() and p.stat().st_size == 0: bad.append(h + "(檔案存在但是空的:空檔不算出處)")   # 閘門稽核 2026-09-17
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
# 掃描集合 = 讀者/轉發者會看到的「現在式」宣稱檔。冷審 2026-09-17 抓到三個漏網:
#   DESIGN.md、docs/*.html(只 glob 過 *.md)、以及被我豁免掉的宣傳稿——而宣傳稿正是要發出去的那份。
# 仍然豁免的兩類,理由與 retraction_lint 相同,且清單會印出來不靜默跳過:
#   docs/review_*(歸檔審查報告在引用它要攻擊的舊數字)、PROGRESS.md(逐日進度,舊行本來就記著當時的張數)。
COUNT_SKIP = ("review_", "PROGRESS.md")
# 2026-09-17 閘門稽核:再加 src/(卡數會寫在介面字串裡)與 dist/(打包後的舊數字會留在產物裡)。
_count_files = ([ROOT/"index.html", ROOT/"README.md", ROOT/"README.zh-TW.md", ROOT/"DESIGN.md"]
                + sorted((ROOT/"docs").glob("*.md")) + sorted((ROOT/"docs").glob("*.html"))
                + sorted((ROOT/"src").rglob("*.ts")) + sorted((ROOT/"dist").rglob("*.html"))
                + sorted((ROOT/"dist").rglob("*.js")))
_count_skipped = []
for f in _count_files:
    if not f.exists(): continue
    if any(x in f.name for x in COUNT_SKIP): _count_skipped.append(str(f.relative_to(ROOT))); continue
    for i, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
        for m in COUNT_RE.finditer(line):
            if int(m.group(1)) != len(cards):
                missing.append((f"{f.relative_to(ROOT)}:{i}", f"寫著 {m.group(1)} 張卡,實際 {len(cards)} 張"))
# P5(2026-09-17 冷審 P1-9):英文版的出處欄曾是執行期正則翻譯,漏掉的中文原樣印出、
# 還會黏字(實際印過「摘要read first-hand」)。改成資料欄之後,這道擋「忘了寫」與「沒翻完」。
CJK = re.compile(r"[\u4e00-\u9fff]")
for c in cards:
    for f in c["facts"]:
        if CJK.search(f["source"]):
            e = f.get("source_en", "")
            if not e:
                missing.append((f"{c['id']}", f"source 有中文卻沒有 source_en:{f['source'][:40]}"))
            elif CJK.search(e):
                missing.append((f"{c['id']}", f"source_en 仍含中文:{e[:40]}"))
for s_ in stages:
    if CJK.search(s_.get("src", "")):
        e = s_.get("src_en", "")
        if not e or CJK.search(e):
            missing.append((f"stage@{s_['t']}", f"src_en 缺或仍含中文:{e[:40] or '(空)'}"))

dups = [str(q) for q in list(ROOT.glob("public/**/cards.json")) + list(ROOT.glob("public/**/stages.json")) + list(ROOT.glob("src/**/*.json"))]
if dups: missing.append(("單一真相", "content/ 之外還有副本:" + ", ".join(dups) + "(熱審 2026-09-15:public/ 舊快照含全部撤回句)"))
print(f"卡數比對掃過 {len(_count_files)} 檔,豁免 {len(_count_skipped)} 檔:{', '.join(_count_skipped) or '無'}")
print(f"facts={sum(len(c['facts']) for c in cards)} stages={len(stages)} missing_paths={len(missing)}")
for a, b in missing: print("  MISSING", a, b)
sys.exit(1 if missing else 0)
