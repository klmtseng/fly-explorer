#!/usr/bin/env python3
"""撤回回流閘門:content/retracted.json 列的說法,不得出現在 content/cards.json(任何層、兩語)、content/stages.json,
以及**讀者讀得到的文件**:docs/*.md、README.md、index.html(2026-09-16 VA 冷審抓到——原本只掃 content/,
於是 docs/verification_log.md 裡還活著一句已撤回的「安全區」,而 README 正是指讀者去看那個檔)。
文件層的豁免:同一行若帶「撤回 / retracted / ~~」即視為在說明這條已被撤回,不算命中。
動機(validity-audit 2026-09-15 冷審):verification_log 正確撤回了三個宣稱,卡片卻還在講撤回前的版本——缺的不是查證,是回流。
exit 0 = 乾淨;1 = 命中。--self-test:塞一條撤回句進暫存副本,必須被擋。"""
import json, sys, pathlib, copy
ROOT = pathlib.Path(__file__).resolve().parent.parent
R = json.loads((ROOT / "content/retracted.json").read_text())["phrases"]
def _positions(text, needle):
    i = text.find(needle); out = []
    while i >= 0: out.append(i); i = text.find(needle, i + 1)
    return out


def scan(cards, stages):
    hits = []; exempted = []
    for c in cards:
        blobs = [("kid.zh", c["kid"]["zh"]), ("kid.en", c["kid"]["en"]), ("more.zh", c["more"]["zh"]), ("more.en", c["more"]["en"]),
                 ("title", json.dumps(c["title"], ensure_ascii=False)), ("facts", json.dumps(c["facts"], ensure_ascii=False)),
                 ("question", json.dumps(c.get("question", {}), ensure_ascii=False))]
        for where, text in blobs:
            for r in R:
                for k in ("zh", "en"):
                    if not r[k]: continue
                    for pos in _positions(text, r[k]):
                        # 2026-09-17:卡片也需要文件層那種豁免——「本卡原本寫 X,已撤回」按建構會含 X。
                        # 但不給整卡豁免(那等於加一個詞就能亂寫):撤回字樣必須出現在該句**附近 60 字**內。
                        near = text[max(0, pos - 120):pos + len(r[k]) + 120]
                        if any(x in near for x in EXEMPT):
                            exempted.append((c["id"], where, r[k])); continue
                        hits.append((c["id"], where, r[k], r["ref"]))
    for s in stages:
        text = s["zh"] + s.get("sub", "") + " " + s.get("en", "") + " " + s.get("sub_en", "")
        for r in R:
            for k in ("zh", "en"):
                if not r[k]: continue
                for pos in _positions(text, r[k]):
                    near = text[max(0, pos - 120):pos + len(r[k]) + 120]
                    if any(x in near for x in EXEMPT):
                        exempted.append((f"stage@{s['t']}", "sub", r[k])); continue
                    hits.append((f"stage@{s['t']}", "sub", r[k], r["ref"]))
    scan.exempted = exempted
    return hits

EXEMPT = ("撤回", "retracted", "Retracted", "retraction", "Retraction", "withdrew", "withdrawn", "Withdrawn", "~~")   # 同一行在講「這條已撤回」不算命中
# 歸檔的審查報告按性質就是在**引用**它要攻擊的宣稱,整份豁免;豁免清單會印在輸出裡,不靜默跳過
# content/retracted.json 是清單本身:它按定義一定含有每一句撤回句,掃它等於掃自己
EXEMPT_FILES = ("docs/review_", "audit/", "content/retracted.json")
def scan_docs():
    """讀者讀得到的文件:README 指過去的 docs/、首頁本身。逐行掃,帶豁免字樣的行跳過。"""
    hits = []
    # 2026-09-17 閘門稽核:先前只掃 docs/*.md 與三個檔,而**撤回句最可能活下來的地方是程式碼與
    # 打包後的產物**——src/ 的字串、public/ 的資料檔、dist/ 的舊 bundle 都直接送到讀者眼前。
    files = (sorted((ROOT / "docs").glob("*.md")) + sorted((ROOT / "docs").glob("*.html"))
             + [ROOT / "README.md", ROOT / "README.zh-TW.md", ROOT / "index.html", ROOT / "DESIGN.md", ROOT / "CLAUDE.md"]
             + sorted((ROOT / "src").rglob("*.ts")) + sorted((ROOT / "src").rglob("*.css"))
             + sorted((ROOT / "content").glob("*.json"))          # 2026-09-18:首頁大標住在 content/tracks.json,
             #   而內容層掃描只看 cards/stages,於是已撤回的那句在首頁活了兩天
             + sorted((ROOT / "public").rglob("*.json")) + sorted((ROOT / "dist").rglob("*.html"))
             + sorted((ROOT / "dist").rglob("*.js")) + sorted((ROOT / "dist/data").rglob("*.json")))
    skipped = []
    for f in files:
        if not f.exists(): continue
        rel = str(f.relative_to(ROOT))
        if any(rel.startswith(x) for x in EXEMPT_FILES):
            skipped.append(rel); continue
        for i, line in enumerate(f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if any(x in line for x in EXEMPT): continue
            for r in R:
                for k in ("zh", "en"):
                    if r[k] and r[k] in line:
                        hits.append((f"{f.relative_to(ROOT)}:{i}", "doc", r[k], r["ref"]))
    scan_docs.skipped = skipped; scan_docs.nfiles = len([f for f in files if f.exists()])
    return hits
if __name__ == "__main__":
    cards = json.loads((ROOT / "content/cards.json").read_text())["cards"]
    stages = json.loads((ROOT / "content/stages.json").read_text())["stages"]
    if "--self-test" in sys.argv:
        base = scan(cards, stages) + scan_docs()
        c2 = copy.deepcopy(cards); c2[0]["kid"]["zh"] += R[0]["zh"]
        neg = scan(c2, stages)
        import tempfile, os
        # 負向二:在 docs 放一行撤回句(不帶豁免字樣)必須被擋;帶「撤回」字樣的同一句必須放行
        tmpdoc = ROOT / "docs" / "_retraction_selftest_tmp.md"
        try:
            tmpdoc.write_text(f"這一行含 {R[0]['zh']} 且沒有豁免字樣\n本行說明 {R[0]['zh']} 已撤回,應放行\n", encoding="utf-8")
            d = scan_docs(); neg_doc = [h for h in d if str(h[0]).startswith("docs/_retraction_selftest_tmp")]
        finally:
            tmpdoc.unlink(missing_ok=True)
        print("基線:", "PASS" if not base else base)
        print("負向 卡片塞撤回句:", "擋住 ✓" if neg else "沒擋住 ✗")
        print(f"負向 docs 塞撤回句:", f"擋住 {len(neg_doc)} 行 ✓(豁免行放行)" if len(neg_doc) == 1 else f"✗ 命中 {len(neg_doc)} 行(應為 1)")
        ok = (not base) and bool(neg) and len(neg_doc) == 1
        print("SELF-TEST", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
    hits = scan(cards, stages) + scan_docs()
    for h in hits: print("❌", *h)
    ex = getattr(scan, "exempted", [])
    print(f"內容層豁免(撤回字樣在前後 120 字內):{len(ex)} 處 → {', '.join(f'{a}/{b}' for a, b, _ in ex) or '無'}")
    print(f"掃過的文件:{getattr(scan_docs, 'nfiles', 0)} 個(docs/*.md|html + README/index/DESIGN/CLAUDE + src/*.ts,css + public 與 dist 的 json/js/html);整份豁免(歸檔審查報告):{len(getattr(scan_docs, 'skipped', []))} 個 → {', '.join(getattr(scan_docs, 'skipped', []))}")
    print(f"retracted phrases: {len(R)}; hits: {len(hits)}; RESULT:", "PASS" if not hits else "FAIL"); sys.exit(1 if hits else 0)
