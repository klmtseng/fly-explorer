#!/usr/bin/env python3
"""撤回回流閘門:content/retracted.json 列的說法,不得出現在 content/cards.json(任何層、兩語)與 content/stages.json。
動機(validity-audit 2026-09-15 冷審):verification_log 正確撤回了三個宣稱,卡片卻還在講撤回前的版本——缺的不是查證,是回流。
exit 0 = 乾淨;1 = 命中。--self-test:塞一條撤回句進暫存副本,必須被擋。"""
import json, sys, pathlib, copy
ROOT = pathlib.Path(__file__).resolve().parent.parent
R = json.loads((ROOT / "content/retracted.json").read_text())["phrases"]
def scan(cards, stages):
    hits = []
    for c in cards:
        blobs = [("kid.zh", c["kid"]["zh"]), ("kid.en", c["kid"]["en"]), ("more.zh", c["more"]["zh"]), ("more.en", c["more"]["en"]),
                 ("title", json.dumps(c["title"], ensure_ascii=False)), ("facts", json.dumps(c["facts"], ensure_ascii=False)),
                 ("question", json.dumps(c.get("question", {}), ensure_ascii=False))]
        for where, text in blobs:
            for r in R:
                for k in ("zh", "en"):
                    if r[k] and r[k] in text: hits.append((c["id"], where, r[k], r["ref"]))
    for s in stages:
        text = s["zh"] + s.get("sub", "")
        for r in R:
            for k in ("zh", "en"):
                if r[k] and r[k] in text: hits.append((f"stage@{s['t']}", "sub", r[k], r["ref"]))
    return hits
if __name__ == "__main__":
    cards = json.loads((ROOT / "content/cards.json").read_text())["cards"]
    stages = json.loads((ROOT / "content/stages.json").read_text())["stages"]
    if "--self-test" in sys.argv:
        base = scan(cards, stages); c2 = copy.deepcopy(cards); c2[0]["kid"]["zh"] += R[0]["zh"]
        neg = scan(c2, stages)
        print("基線:", "PASS" if not base else base); print("負向 塞撤回句:", "擋住 ✓" if neg else "沒擋住 ✗")
        ok = (not base) and bool(neg); print("SELF-TEST", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
    hits = scan(cards, stages)
    for h in hits: print("❌", *h)
    print(f"retracted phrases: {len(R)}; hits: {len(hits)}; RESULT:", "PASS" if not hits else "FAIL"); sys.exit(1 if hits else 0)
