#!/usr/bin/env python3
"""◆(paper)事實的引用記錄閘門。不驗論文真偽(那需要人親讀),只驗「本倉有沒有親讀記錄」:
每條 provenance=paper 的 source 第一個作者/識別字,必須出現在 docs/verification_log.md 或 docs/research_context_cards.md
或 audit/content_audit.md。熱審 2026-09-15:先前的 C3「捏造閘門」其實只自測了術語與編碼,引用沒有任何機器閘門。
exit 0 = 全部有記錄;--self-test:塞一條假論文必須被擋。"""
import json, re, sys, pathlib, copy
ROOT = pathlib.Path(__file__).resolve().parent.parent
LOGS = "".join((ROOT / f).read_text() for f in ["docs/verification_log.md", "docs/research_context_cards.md", "audit/content_audit.md"] if (ROOT / f).exists())
def key_of(src):
    m = re.match(r"\s*([A-Za-z][A-Za-z&\.\- ]{1,40}?)(?: et al\.?|,|\s\(|\s\d{4}| in | Science| Nature| Development| Genome| Curr| J | eNeuro|:)", src)
    if m: return m.group(1).strip()
    m = re.search(r"(arXiv:\d+\.\d+|microns-explorer\.org|Bloomington|Wikipedia|FlyBase)", src)
    return m.group(1) if m else src[:20]
def scan(cards):
    bad = []
    for c in cards:
        for f in c["facts"]:
            if f["provenance"] != "paper": continue
            k = key_of(f["source"])
            if k not in LOGS: bad.append((c["id"], f["value"], k))
    return bad
if __name__ == "__main__":
    cards = json.loads((ROOT / "content/cards.json").read_text())["cards"]
    if "--self-test" in sys.argv:
        base = scan(cards); c2 = copy.deepcopy(cards)
        c2[0]["facts"].append({"value": "42", "label": {"zh": "假", "en": "fake"}, "provenance": "paper", "source": "Fakerson et al. Nature 999:1-2 (2030)"})
        neg = scan(c2); print("基線:", "PASS" if not base else base); print("負向 假論文:", "擋住 ✓" if neg else "沒擋住 ✗")
        ok = (not base) and bool(neg); print("SELF-TEST", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
    bad = scan(cards)
    for b in bad: print("❌ 無親讀記錄:", *b)
    print(f"paper facts checked; RESULT: {'PASS' if not bad else 'FAIL'}"); sys.exit(1 if bad else 0)
