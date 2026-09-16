#!/usr/bin/env python3
"""術語 lint:檢查「小朋友層」文案有沒有用到未解釋的專有名詞。

分三級:
  BAN    小朋友層絕對不該出現(該詞的概念要用白話講,名字留給進階層)
  GLOSS  可以出現,但**第一次**出現時必須當場給一句話解釋
  OK     日常詞,不管

設計理由:與其煩惱「要不要加連結」,不如先確認小朋友層根本不需要那些詞。
名詞應該是概念被理解之後才出現的東西,不是入口。

exit 0 = 通過;非 0 = 有 BAN 級違規或首次出現未宣告解釋。

`--self-test`:對暫存副本跑負向控制組(塞 BAN 詞 / 移除 glossed 宣告),
兩者都必須被擋下,證明閘門有鑑別力。這是 maintenance.md 要求的「迴歸案例落地」,
之前只在終端手動跑過,審查者指出 repo 裡一支都沒有(2026-09-13 P1)。
"""
import json, re, sys, pathlib, copy, subprocess, tempfile, os

ROOT = pathlib.Path(__file__).resolve().parent.parent
CARDS = pathlib.Path(os.environ.get("JARGON_CARDS", ROOT/"content/cards.json"))
STAGES = pathlib.Path(os.environ.get("JARGON_STAGES", ROOT/"content/stages.json"))
if "--self-test" in sys.argv:
    base = json.loads((ROOT/"content/cards.json").read_text(encoding="utf-8"))
    me = pathlib.Path(__file__).resolve()
    def run_variant(mutate, label):
        v = copy.deepcopy(base); mutate(v)
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump(v, fh, ensure_ascii=False); tmp = fh.name
        env = dict(os.environ, JARGON_CARDS=tmp)
        r = subprocess.run([sys.executable, str(me)], env=env, capture_output=True, text=True)
        os.unlink(tmp)
        ok = r.returncode != 0
        print(f"  {'✓' if ok else '✗'} {label}: exit {r.returncode}(預期非 0)")
        return ok
    def m_ban(v): v["cards"][0]["kid"]["zh"] += "這叫做 PWM。"
    def m_gloss(v):
        for c in v["cards"]:
            if c.get("glossed"): c.pop("glossed"); return
    r0 = subprocess.run([sys.executable, str(me)], capture_output=True, text=True)
    print(f"  {'✓' if r0.returncode == 0 else '✗'} 原始資料: exit {r0.returncode}(預期 0)")
    results = [r0.returncode == 0, run_variant(m_ban, "負向:小朋友層塞 BAN 詞"), run_variant(m_gloss, "負向:移除 glossed 宣告")]
    print("SELF-TEST", "PASS" if all(results) else "FAIL")
    sys.exit(0 if all(results) else 1)

D = json.loads(CARDS.read_text(encoding="utf-8"))
# 階段標籤(content/stages.json)也是小朋友會直接看到的文案,一併納入。
# 審查者抓到 STAGES 原本硬寫在 main.ts 裡含 BAN 級詞「軸突」而 lint 掃不到。
# 2026-09-15 冷審:stages 沒有 en 欄時英文側掃的是空字串=恆真;現在明講「未檢查」而不假裝 PASS。
for st in json.loads(STAGES.read_text(encoding="utf-8"))["stages"]:
    D["cards"].append({"id": f"stage@{st['t']}ms", "module": "B", "kid": {"zh": st["zh"] + " " + st["sub"], "en": st.get("en", "") + " " + st.get("sub_en", "")},
                       "more": {"zh": "", "en": ""}, "glossed": st.get("glossed", [])})
_missing_en = [st["t"] for st in json.loads(STAGES.read_text(encoding="utf-8"))["stages"] if not st.get("en")]
if _missing_en: print(f"⚠ 字幕 en 欄缺({len(_missing_en)} 段):英文側本次未檢查,不算 PASS(M2e 補英文後自動納入)")

BAN = {
    "zh": ["PWM", "脈衝頻率調變", "速率編碼", "拓樸", "閾值", "膜電位", "軸突",
           "突觸後", "間隙連接", "連接組", "虛無模型", "出度", "入度", "指數衰減",
           "神經傳導物質", "可塑性", "retinotopic", "LoRA", "低通濾波"],
    "en": ["PWM", "pulse-frequency modulation", "rate coding", "topology", "threshold",
           "membrane potential", "axon", "postsynaptic", "gap junction", "connectome",
           "null model", "in-degree", "out-degree", "exponential decay",
           "neurotransmitter", "plasticity", "retinotopic", "LoRA", "low-pass"],
}
GLOSS = {
    "zh": ["神經元", "突觸", "赫茲", "毫秒", "微米", "多巴胺", "蘑菇體", "巨纖維", "細胞本體"],
    "en": ["neuron", "synapse", "hertz", "Hz", "millisecond", "dopamine",
           "mushroom body", "giant fiber", "cell body"],
}
# 「有沒有當場解釋」改成由作者在 cards.json 用 glossed 欄位**明確宣告**,
# 不再用正則猜。理由:第一版的正則是中文導向的,在英文上幾乎全是誤判
# (「giant fibers, the thickest...」明明解釋了卻判成沒解釋),
# 而放寬到能接受英文逗號又會寬到永遠通過。宣告式沒有這個兩難。

# 閱讀順序:按模組順序,模組內按 JSON 出現序。第一次出現才要求解釋,之後沿用不算錯。
MOD_ORDER = list(D["modules"].keys())
ordered = sorted(D["cards"], key=lambda c: (MOD_ORDER.index(c["module"]),
                                            [x["id"] for x in D["cards"]].index(c["id"])))

bans, needs, reused = [], [], []
first_seen = {}                      # (lang, term) -> card id
for c in ordered:
    for lang in ("zh", "en"):
        txt = c["kid"][lang]
        for w in BAN[lang]:
            if w.lower() in txt.lower():
                bans.append((c["id"], lang, w))
        for w in GLOSS[lang]:
            if w.lower() not in txt.lower():
                continue
            key = (lang, w)
            if key in first_seen:
                reused.append((c["id"], lang, w, first_seen[key]))
                continue
            first_seen[key] = c["id"]
            if w not in c.get("glossed", []):
                needs.append((c["id"], lang, w))

print(f"掃描 {len(D['cards'])} 張卡的小朋友層(中英各一份)\n")
print(f"【BAN】小朋友層不該出現的術語:{len(bans)} 處")
for cid, lang, w in bans:
    print(f"   ✗ {cid:22s} [{lang}] 「{w}」")
if not bans:
    print("   (無)")
print(f"\n【GLOSS】**第一次**出現卻沒在 glossed 宣告:{len(needs)} 處")
for cid, lang, w in needs:
    print(f"   ⚠ {cid:22s} [{lang}] 「{w}」  ← 首次出現,請當場解釋並加進該卡 glossed")
if not needs:
    print("   (無)")
print(f"\n【沿用】已在前面解釋過、後面直接使用:{len(reused)} 處 —— 這是對的,不該加標記")
for cid, lang, w, src in reused[:6]:
    print(f"   ✓ {cid:22s} [{lang}] 「{w}」  首次解釋於 {src}")
if len(reused) > 6: print(f"   … 另 {len(reused)-6} 處")

# 進階層對照:這些詞本來就該在進階層出現,這裡只是報數不判錯
adv = sum(1 for c in D["cards"] for lang in ("zh","en")
          for w in BAN[lang] if w.lower() in c["more"][lang].lower())
print(f"\n【對照】同樣這些術語在「想知道更多」層出現 {adv} 處 —— 那一層本來就該有,不算錯。")
sys.exit(1 if (bans or needs) else 0)
