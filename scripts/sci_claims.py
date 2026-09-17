#!/usr/bin/env python3
"""科學宣稱的候選過濾器(確定性;評估系統的第一段)。

動機:使用者 2026-09-17 問「科學上錯誤但用詞乾淨的句子,有沒有辦法辨識出邏輯再去查文獻」。
全站有 34 張卡 × 兩層 × 兩語 + 8 段字幕 + 宣傳稿,逐句查文獻的成本不可行。
這支負責把「值得花錢查的句子」揀出來。條件是**有外部指涉物**,再加上兩種觸發之一:

  ① 外部指涉物(具名神經元/細胞型、「教科書」、「文獻」、論文)——必要條件。
     沒有外部指涉物的純自家量測歸既有閘門(audit_numbers/audit_claims)管,不進這個池子。
  ② trigger=causal:句子裡有**推論連接詞**(因為/所以/走…那條路/because/drives…)
     ——做推論的句子才會犯「前提對、推論錯」這種錯。
  ③ trigger=quant:句子把**帶單位的數字**掛在那個實體上——即使沒有推論詞,
     它本身就是可查的宣稱(單位、口徑、以及「這是模型值還是果蠅的值」)。

輸出 audit/sci_claims.tsv,每列一個候選,claim_id 由內容雜湊而來(句子改了 id 就變,
所以「這條查過了」不會被偷偷搬到另一句上)。

這支**不判斷對錯**,只負責揀句子。判斷在 scripts/verify_quotes.py(逐字對原文)
與 scripts/disclosure_lint.py(站內互比),而它們兩個的鑑別力由 scripts/sci_eval.py 量。

用法:python3 scripts/sci_claims.py            # 產生 audit/sci_claims.tsv
      python3 scripts/sci_claims.py --self-test
exit 0 = 正常產出,非 0 = 過濾器自己壞了。
"""
import hashlib, json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "audit/sci_claims.tsv"

# 推論連接詞。挑的是「把兩件事連起來」的詞,不是「描述一件事」的詞。
CAUSAL = re.compile(
    r"因為|所以|因此|於是|導致|使得|表示|代表|意味|證明|才會|是因為|決定|靠著|靠的是"
    r"|走[^,。]{0,8}(?:路|條)|由[^,。]{0,10}驅動|被[^,。]{0,8}(?:壓住|擋住|抑制)"
    r"|\bbecause\b|\btherefore\b|\bthus\b|\bmeans\b|\bshows\b|\bproves\b|\bdrives\b"
    r"|\bresults in\b|\bdetermines\b|\bso that\b|\bvia\b|\bgoes (?:another|through)\b")

# 外部指涉物:具名細胞型(由資料裡實際出現的命名法寫成),或明講「教科書/文獻/論文」。
ENTITY = re.compile(
    r"\b(?:LC\d+|LPLC\d+|DNp\d+|DNa\d+|MDN|pIP\d+|PSI|TTMn?|DLMn?|DVMn?|MN\d+|AN\d+[A-Z]\d+"
    r"|KC|MBON|APL|T4|T5|Mi\d+|Tm\d+|ppk\d+|IR\d+[a-z]?|shakB|Shaking-B)\b"
    r"|教科書|文獻|論文|課本|\btextbook\b|\bliterature\b|\bpaper\b|巨纖維|\bgiant fib(?:er|re)\b")

# 數量陳述:把一個帶單位的數字掛到具名實體上,本身就是一個可查的宣稱,即使句子裡沒有推論詞。
# 這條是 2026-09-17 評估台跑出來才加的:原本只有「因果 + 實體」,
# 於是 unit-or-denominator(邊 vs 突觸、毫秒 vs 秒)與 model-as-biology(模型值講成果蠅生理值)
# 這兩整類變異體**在過濾器就死了**,下游再強也看不到。代價是卡片與字幕的候選從 14 句變成 64 句。
# ⚠️ 因為這一版是看著評估結果改的,那兩類的召回數字已經是 in-sample,
#    要當獨立量測必須另外寫一批沒看過這次修正的變異體。
QUANT = re.compile(r"\d[\d,.]*\s*(?:ms|毫秒|秒|s\b|Hz|赫茲|%|顆|條|個突觸|突觸|mV|毫伏|µm|微米|倍)")

# 句子切割:中文句號/問號/驚嘆號/分號,英文句點後接空白+大寫。粗但夠用。
SPLIT = re.compile(r"(?<=[。!?;])\s*|(?<=[.!?])\s+(?=[A-Z(])|\n+")


def sentences(text):
    for s in SPLIT.split(text or ""):
        s = re.sub(r"\s+", " ", s).strip(" -*>|")
        if len(s) >= 12:
            yield s


def is_candidate(s):
    """單一真相:要不要把這句揀進池子,只有這裡說了算。
    (checker_filter.py 曾經自己再寫一次 `CAUSAL and ENTITY`,過濾器加了 quant 觸發之後
     兩邊漂開,評估數字沒動而我差點以為是修正無效。)回傳 None 或 'causal'/'quant'。"""
    if not ENTITY.search(s):
        return None
    return "causal" if CAUSAL.search(s) else ("quant" if QUANT.search(s) else None)


def cid(*parts):
    return hashlib.sha1("|".join(parts).encode()).hexdigest()[:8]


def collect():
    rows = []

    def take(where, lang, text):
        for s in sentences(text):
            trig = is_candidate(s)
            if trig:
                rows.append((cid(where, lang, s), where, lang, trig, s))

    cards = json.loads((ROOT / "content/cards.json").read_text())["cards"]
    for c in cards:
        for layer in ("title", "kid", "more"):
            for lang in ("zh", "en"):
                take(f"card:{c['id']}/{layer}", lang, (c.get(layer) or {}).get(lang, ""))
        q = c.get("quiz")
        if q:
            for lang in ("zh", "en"):
                take(f"card:{c['id']}/quiz", lang, (q.get("q") or {}).get(lang, ""))
    for st in json.loads((ROOT / "content/stages.json").read_text())["stages"]:
        take(f"stage:{st['t']}", "zh", st.get("sub", ""))
        take(f"stage:{st['t']}", "en", st.get("sub_en", ""))
    promo = ROOT / "docs/promo_drafts.md"
    if promo.exists():
        for i, line in enumerate(promo.read_text(encoding="utf-8").splitlines(), 1):
            if line.startswith(("#", "|", "```")):
                continue
            take(f"promo:{i}", "zh" if re.search(r"[一-鿿]", line) else "en", line)
    return rows


def main():
    if "--self-test" in sys.argv:
        ok = []
        # 正例:有推論詞 + 有實體 → 要被揀出來
        pos = "教科書說翅膀要經過一顆轉手細胞(叫 PSI),但我們的模擬裡訊號走了另一條路。"
        ok.append(("正例 因果+實體", bool(CAUSAL.search(pos) and ENTITY.search(pos))))
        # 負例一:有實體沒推論詞(純描述)→ 不該進池子,否則池子等於全站
        ok.append(("負例 只有實體", not (CAUSAL.search("LC4 有 126 顆,LPLC2 有 185 顆。")
                                        and ENTITY.search("LC4 有 126 顆,LPLC2 有 185 顆。"))))
        # 負例二:有推論詞沒外部實體(純自家量測)→ 歸既有閘門管
        n2 = "因為抽樣是 1/2,所以畫面上只有 70,012 個點。"
        ok.append(("負例 只有因果", not (CAUSAL.search(n2) and ENTITY.search(n2))))
        # 負例三:太短的碎句不該成句
        ok.append(("負例 碎句", list(sentences("好。")) == []))
        # 正例二:英文側同樣要抓得到
        p2 = "The giant fiber drives the jump muscle nerve directly, so the wing signal goes another way."
        ok.append(("正例 英文", bool(CAUSAL.search(p2) and ENTITY.search(p2))))
        q = "巨纖維到跳躍肌的運動神經元之間有 2 個突觸。"
        ok.append(("正例 數量+實體(沒有因果詞也要揀)", bool(ENTITY.search(q) and QUANT.search(q))))
        nq = "這台裝置畫出其中 70,012 顆。"
        ok.append(("負例 數量但沒有具名實體", not (ENTITY.search(nq) and (CAUSAL.search(nq) or QUANT.search(nq)))))
        # id 穩定性:同輸入同 id,改一個字就換 id
        ok.append(("id 隨內容變", cid("a", "zh", pos) != cid("a", "zh", pos + "!") and
                   cid("a", "zh", pos) == cid("a", "zh", pos)))
        for name, good in ok:
            print(f"  {'✓' if good else '✗'} {name}")
        print("SELF-TEST", "PASS" if all(g for _, g in ok) else "FAIL")
        sys.exit(0 if all(g for _, g in ok) else 1)

    rows = collect()
    OUT.write_text("claim_id\twhere\tlang\ttrigger\tsentence\n" +
                   "".join("\t".join(r) + "\n" for r in rows), encoding="utf-8")
    by = {}
    for _, where, _, _, _ in rows:
        by[where.split(":")[0]] = by.get(where.split(":")[0], 0) + 1
    trig = {}
    for r in rows: trig[r[3]] = trig.get(r[3], 0) + 1
    print(f"候選 {len(rows)} 句 → {OUT.relative_to(ROOT)}(觸發:" +
          ", ".join(f"{k} {v}" for k, v in sorted(trig.items())) + ")")
    print("  來源分布:" + ", ".join(f"{k} {v}" for k, v in sorted(by.items())))
    if not rows:
        print("FAIL:一句都沒揀到,過濾器與內容脫鉤了"); sys.exit(1)


if __name__ == "__main__":
    main()
