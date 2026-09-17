#!/usr/bin/env python3
"""限制揭露傳播檢查:專業層承認的模型限制,讀者層不准悄悄不提(確定性)。

這支是 2026-09-17 那條 P1 的機制化。當時的情況是:
  - 專業層(escape-two-muscles/more)寫著「教科書的 GF→PSI→DLMn 含電突觸,本模型只有化學突觸」——寫對了;
  - 而字幕(stage 30)寫「PSI 完全沒放電(被抑制壓住)」、小朋友層寫「訊號走了另一條路,
    你看到的跟教科書不完全一樣」——兩處都對同一件事給了**跟自家專業層互相矛盾的因果解釋**。
  - 文獻(Augustin 2019, PMC6469880)逐字:電突觸是果蠅巨纖維系統的**主要**突觸型別,
    化學突觸只是次要角色。所以模型缺的正是那條路的主要傳遞方式,它量不了那條路。

規則(全站,不分卡):
  1. 任一**專業層**句子裡同時出現「具名細胞/結構 E」與「限制字樣」→ E 進入受限清單,並記下是哪一句。
  2. 凡**讀者層**(小朋友層、卡片標題、舞台字幕)提到 E 且對 E 做了行為或因果陳述
     (放電/沒放電/走哪條路/驅動/fires/never fired/drives…),該句就必須自己也帶限制字樣。
  3. 沒帶 → FAIL,並印出專業層那一句當對照。

**這裡有一個承重的判斷,寫明白**:「在這個模擬裡」「in this model」**不算**已揭露。
限定範圍不等於說出限制:讀者被告知「模擬裡是這樣」,仍然會推論「那教科書可能有問題」,
而真正的原因是這個模型按建構就做不出那條路。要通過,句子得指出**缺的是什麼**。

用法:python3 scripts/disclosure_lint.py        # 產生 audit/disclosure.tsv
      python3 scripts/disclosure_lint.py --self-test
exit 0 = 沒有未傳播的限制,非 0 = 有。
"""
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "audit/disclosure.tsv"

# 凍結的預期受限清單。專業層對這些實體**已知**承認過帶行為語的限制;
# 哪天它們從 limited 裡消失,代表限制句被改寫掉了(2026-09-18 真的發生過:
# 我重寫那段時把「PSI 被驅動得又弱又慢」拿掉,受限清單瞬間變空集合,整道檢查恆真通過)。
# 「空集合就 FAIL」擋得住全滅,擋不住只掉一個,所以這裡要逐個點名。
EXPECTED_LIMITED = {"PSI"}

ENTITY = re.compile(
    r"\b(?:LC\d+|LPLC\d+|DNp\d+|DNa\d+|MDN|pIP\d+|PSI|TTMns?|DLMns?|DVMns?|MN\d+|AN\d+[A-Z]\d+"
    r"|KC|MBON|APL|T4|T5|Mi\d+|Tm\d+|shakB|Shaking-B)\b|巨纖維|\bgiant fib(?:er|re)\b")

# 「這件事模型做不到/不是資料」的字樣。承認限制,不是限定範圍。
LIMIT = re.compile(
    r"電突觸|間隙連接|縫隙連接|只有化學突觸|沒有電突觸|模型(?:裡)?沒有|引擎沒有|連接組沒有|資料裡沒有"
    r"|量不了|測不到|做不到|不是資料|我們畫的|我們加的|注入|沒有可塑性|沒有肌肉|示意|未驗證|待確認"
    r"|gap junction|electrical synapse|only chemical|no plasticity|not in the connectome"
    r"|drawn by us|injected|illustrative|unverified|cannot (?:compute|do|test|measure)")

# 行為/因果陳述:對 E 說了「它做了什麼、為什麼」,而不只是「它存在、有幾顆」。
BEHAVIOUR = re.compile(
    r"放電|沒放電|不放電|發放|傳(?:到|不到)|走[^,。]{0,8}(?:路|條)|驅動|接力|轉手|壓住|抑制|整合|決定"
    r"|\bfires?\b|\bfired\b|\bnever fired\b|\bdrives?\b|\bgoes\b|\brelays?\b|\bintegrat\w+\b|\bdetermines\b")

SPLIT = re.compile(r"(?<=[。!?;])\s*|(?<=[.!?])\s+(?=[A-Z(])|\n+")


def sents(t):
    return [re.sub(r"\s+", " ", s).strip(" -*>|") for s in SPLIT.split(t or "") if len(s.strip()) >= 8]


def entities(s):
    return {m.group(0) for m in ENTITY.finditer(s)}


def scan(cards, stages):
    limited = {}          # 實體 → (出處, 專業層那一句)
    for c in cards:
        for lang in ("zh", "en"):
            for s in sents((c.get("more") or {}).get(lang, "")):
                # 限制句本身也必須是在講「這東西做了什麼/被怎麼驅動」。
                # 第一版沒有這個條件,於是 model-vs-real 的解剖描述(「巨纖維與下游是混合突觸」)
                # 把「巨纖維」整站鎖住,15 個命中裡十個是誤報——而那些句子(電壓往上爬、3.3 ms 收到)
                # 跟那條限制根本無關。限制要管的是行為宣稱,所以限制句自己得有行為語。
                if LIMIT.search(s) and BEHAVIOUR.search(s):
                    for e in entities(s):
                        limited.setdefault(e, (f"card:{c['id']}/more.{lang}", s))
    hits = []
    surfaces = []
    for c in cards:
        for layer in ("title", "kid"):
            for lang in ("zh", "en"):
                surfaces.append((f"card:{c['id']}/{layer}.{lang}", (c.get(layer) or {}).get(lang, "")))
    for st in stages:
        surfaces.append((f"stage:{st['t']}.zh", st.get("sub", "")))
        surfaces.append((f"stage:{st['t']}.en", st.get("sub_en", "")))
    for where, text in surfaces:
        # 揭露算「同一段裡有」就好,不要求同一句。讀者看到的單位是整段字幕/整層卡片文字,
        # 硬要求同句會把句子逼成怪樣子。代價是很長的段落可能把限制埋在很遠的地方——
        # 這一段目前最長的是字幕,還在一眼看得完的範圍內。
        block_disclosed = bool(LIMIT.search(text or ""))
        for s in sents(text):
            if not BEHAVIOUR.search(s) or block_disclosed:
                continue
            for e in sorted(entities(s) & limited.keys()):
                src, pro = limited[e]
                hits.append((where, e, s, src, pro))
    return limited, hits


def main():
    if "--self-test" in sys.argv:
        def card(cid, kid, more):
            return {"id": cid, "title": {"zh": "", "en": ""}, "kid": {"zh": kid, "en": ""},
                    "more": {"zh": more, "en": ""}, "facts": []}
        cases = [
            ("負向:專業層說缺電突觸,小朋友層講 PSI 的行為卻不提",
             [card("x", "PSI 從頭到尾沒放電,訊號走了另一條路。", "教科書那條含電突觸,本模型只有化學突觸,PSI 被驅動得很弱。")], True),
            ("負向:『在這個模擬裡』只是限定範圍,不算揭露限制",
             [card("x", "在這個模擬裡 PSI 完全沒放電。", "教科書那條含電突觸,本模型只有化學突觸,PSI 被驅動得很弱。")], True),
            ("正向:專業層只描述解剖(混合突觸),沒有行為宣稱 → 不鎖住這個實體",
             [card("x", "巨纖維的電壓爬過閾值就會放電。", "巨纖維與下游是混合突觸:化學突觸加上間隙連接。")], False),
            ("正向:限制寫在同一段的下一句 → 放行",
             [card("x", "PSI 從頭到尾沒放電。教科書那條路靠電突觸,而連接組只記錄化學突觸。", "教科書那條含電突觸,本模型只有化學突觸,PSI 被驅動得很弱。")], False),
            ("正向:同一句自己說出缺什麼 → 放行",
             [card("x", "PSI 沒放電——教科書那條路靠電突觸,而連接組只記錄化學突觸。", "教科書那條含電突觸,本模型只有化學突觸。")], False),
            ("正向:只是描述存在、沒有行為陳述 → 不該誤報",
             [card("x", "PSI 是一顆位在胸部的神經細胞。", "教科書那條含電突觸,本模型只有化學突觸。")], False),
            ("正向:專業層從沒對這個實體承認過限制 → 讀者層自由",
             [card("x", "LC4 放電之後把訊號送出去。", "LC4 有 126 顆,全部連到巨纖維。")], False),
        ]
        # 受限清單為空時必須 FAIL(不得恆真通過)
        empty_ok = (lambda lim: not lim)(scan([{"id": "z", "title": {"zh": "", "en": ""}, "kid": {"zh": "PSI 沒放電。", "en": ""},
                                                "more": {"zh": "PSI 有兩顆。", "en": ""}, "facts": []}], [])[0])
        drop = scan([{"id": "z", "title": {"zh": "", "en": ""}, "kid": {"zh": "PSI 沒放電。", "en": ""},
                      "more": {"zh": "教科書那條含電突觸,本模型只有化學突觸。PSI 被驅動得很弱。", "en": ""}, "facts": []}], [])[0]
        ok = [("受限清單為空時偵測得到(主程式會據此 FAIL)", empty_ok),
              ("限制語與行為語被拆成兩句時,該實體會掉出清單(靠凍結清單抓)", "PSI" not in drop)]
        for label, cards, want_hit in cases:
            _, hits = scan(cards, [])
            good = bool(hits) == want_hit
            ok.append((label, good))
            print(f"  {'✓' if good else '✗'} {label}" + ("" if good else f" → hits={len(hits)}"))
        for label, good in ok[:2]:
            print(f"  {'✓' if good else '✗'} {label}")
        good_all = all(g for _, g in ok)
        print("SELF-TEST", "PASS" if good_all else "FAIL")
        sys.exit(0 if good_all else 1)

    cards = json.loads((ROOT / "content/cards.json").read_text())["cards"]
    stages = json.loads((ROOT / "content/stages.json").read_text())["stages"]
    limited, hits = scan(cards, stages)
    OUT.write_text("where\tentity\treader_sentence\tpro_source\tpro_sentence\n" +
                   "".join("\t".join(h) + "\n" for h in hits), encoding="utf-8")
    print(f"專業層承認過限制的實體 {len(limited)} 個:{', '.join(sorted(limited)) or '(空)'}")
    missing = EXPECTED_LIMITED - set(limited)
    if missing and limited:
        print(f"  ❌ 預期受限的實體不在清單裡:{', '.join(sorted(missing))}"
              "——專業層對它的限制句被改寫掉了(限制語與行為語要落在同一句)")
        print("RESULT: FAIL"); sys.exit(1)
    if not limited:
        # 2026-09-18:我改寫專業層時把唯一一句「帶行為語的限制句」弄掉了,受限清單變成空集合,
        # 這道檢查於是恆真通過。空集合不是通過,是這道檢查沒有東西可守。
        print("  ❌ 受限清單是空的——本站一定有模型限制,這代表專業層的限制句不再帶行為語,或正則與內容脫鉤")
        print("RESULT: FAIL"); sys.exit(1)
    print(f"讀者層未傳播的 {len(hits)} 處 → {OUT.relative_to(ROOT)}")
    for where, e, s, src, pro in hits:
        print(f"  ❌ {where} 講 {e}:「{s[:70]}」")
        print(f"     專業層({src})卻寫著:「{pro[:80]}」")
    print("RESULT:", "PASS" if not hits else "FAIL")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
