#!/usr/bin/env python3
"""◆(paper)事實的引用記錄閘門。不驗論文真偽(那需要人親讀),只驗「本倉有沒有親讀記錄」:
每條 provenance=paper 的 source 第一個作者/識別字,必須出現在 docs/verification_log.md 或 docs/research_context_cards.md
或 audit/content_audit.md。熱審 2026-09-15:先前的 C3「捏造閘門」其實只自測了術語與編碼,引用沒有任何機器閘門。
exit 0 = 全部有記錄;--self-test:塞一條假論文必須被擋。"""
import json, re, sys, pathlib, copy
ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG_TEXT = "".join((ROOT / f).read_text() for f in ["docs/verification_log.md", "docs/research_context_cards.md", "audit/content_audit.md"] if (ROOT / f).exists())
LOG_LINES = LOG_TEXT.splitlines()
# 2026-09-17 閘門稽核:原本只問「這個作者字串在紀錄檔裡出現過嗎」,於是
#   ① key_of 落到 src[:20] 的後備時,鍵可能是一段路徑或常用字,隨便命中;
#   ② 命中的那一行可能只是別處的順口提及,不是引用登記。
# 現在要求:鍵長度 ≥4 且不在停用字表,且命中的行本身要像一筆引用登記(帶年份/DOI/arXiv/PMID/親讀字樣)。
STOP = {"the", "this", "and", "for", "with", "from", "data", "paper", "abstract", "official", "page", "docs", "scripts", "public", "runs"}
CITE_HINT = re.compile(r"(19|20)\d{2}|doi|DOI|arXiv|PMID|PMC|bioRxiv|親讀|read first-hand|二手|secondhand")

def recorded(key):
    hits = [l for l in LOG_LINES if key in l]
    return any(CITE_HINT.search(l) for l in hits)

def key_of(src):
    m = re.match(r"\s*([A-Za-z][A-Za-z&\.\- ]{1,40}?)(?: et al\.?|,|\s\(|\s\d{4}| in | Science| Nature| Development| Genome| Curr| J | eNeuro|:)", src)
    if m: return m.group(1).strip()
    m = re.search(r"(arXiv:\d+\.\d+|microns-explorer\.org|Bloomington|Wikipedia|FlyBase)", src)
    return m.group(1) if m else src[:20]
def scan(cards):
    bad = []
    # 專案的既有規定:二手轉引不得與親讀共用 ◆。這裡把它變成機器檢查。
    for c in cards:
        for f in c["facts"]:
            if re.search(r"二手|secondhand", f["source"] + f.get("source_en", "")) and f["provenance"] == "paper":
                bad.append((c["id"], f["value"], "來源自稱二手轉引,卻標成 ◆ 親讀"))
    for c in cards:
        for f in c["facts"]:
            if f["provenance"] != "paper": continue
            k = key_of(f["source"])
            if len(k) < 4 or k.lower() in STOP:
                bad.append((c["id"], f["value"], f"抓不出可查的作者鍵(得到 {k!r});來源欄請以作者或識別碼開頭")); continue
            if not recorded(k):
                bad.append((c["id"], f["value"], f"{k}:紀錄檔裡沒有一行同時含這個鍵與年份/DOI/arXiv/親讀字樣"))
    return bad
if __name__ == "__main__":
    cards = json.loads((ROOT / "content/cards.json").read_text())["cards"]
    if "--self-test" in sys.argv:
        base = scan(cards); c2 = copy.deepcopy(cards)
        def mut(fact):
            v = copy.deepcopy(cards); v[0]["facts"].append(dict({"label": {"zh": "假", "en": "fake"}}, **fact)); return scan(v)
        cases = [("假論文", {"value": "42", "provenance": "paper", "source": "Fakerson et al. Nature 999:1-2 (2030)"}),
                 ("二手卻標 ◆", {"value": "43", "provenance": "paper", "source": "White et al. (1986);原頁被擋,數字為二手轉引"}),
                 ("抓不出作者鍵", {"value": "44", "provenance": "paper", "source": "abstract"}),
                 ("鍵在紀錄裡但那行不是引用登記", {"value": "45", "provenance": "paper", "source": "Hexmap et al. Nature 1:1 (2030)"})]
        print("基線:", "PASS" if not base else base)
        res = [not base]
        for label, fact in cases:
            n = mut(fact); print(f"負向 {label}:", "擋住 ✓" if n else "沒擋住 ✗"); res.append(bool(n))
        print("SELF-TEST", "PASS" if all(res) else "FAIL"); sys.exit(0 if all(res) else 1)
    bad = scan(cards)
    for b in bad: print("❌ 無親讀記錄:", *b)
    print(f"paper facts checked; RESULT: {'PASS' if not bad else 'FAIL'}"); sys.exit(1 if bad else 0)
