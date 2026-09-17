#!/usr/bin/env python3
"""字幕時間點閘門(validity-audit 2026-09-15 冷審 P2:原本沒有任何機器檢查擋字幕時間漂移)。
規則:content/stages.json 每段(t>=0)文字裡出現的「N ms」,必須等於某一族群在出貨 runs/build/escape.csv 的
首次放電時刻(±0.05 ms),或 build_scenario 的協定常數(T_STIM、T_RUN)、或 verification_log 記錄的探測值 600。
另:字幕說「PSI 沒放電」時,PSI 在 escape.csv 必須真的是 0 次。
--self-test:把一個字幕數字改掉、把 PSI 假造一次放電,兩個負向都必須 exit 非 0。
族群由標註檔 type 判定(與 scripts/export_edges.py 同一套規則)。"""
import json, re, sys, csv, pathlib, collections
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import os
FLY = ROOT.parent / "fly"
ANN = pathlib.Path(os.environ.get("FLY_ANN", FLY / "data/body-annotations-male-cns-v1.0-minconf-0.5.feather"))
CACHE = ROOT / "runs/build/escape_groups.json"   # bodyId→族群的快取:公開倉沒有 14 MB 標註檔也能跑;標註檔在時重建並比對
CSV = ROOT / "runs/build/escape.csv"
GROUPS = {"detect": lambda t: t in ("LC4", "LPLC2"), "gf": lambda t: t == "DNp01", "jump": lambda t: t == "TTMn",
          "wing": lambda t: t.startswith("DLMn"), "psi": lambda t: t == "PSI", "AN19B001": lambda t: t == "AN19B001",
          "DNp03": lambda t: t == "DNp03"}

ENGINE_CONST = {1.8: "突觸延遲 t_dly(Shiu 2024;研究倉引擎預設)"}   # 字幕會提到的模型常數,逐一列明出處
PROBE_CONST = {599.9: "600ms 探測 20 次:全腦最後放電上端 599.9(verification_log §頭條毫秒數的跑次離散)",
               562.1: "600ms 探測 20 次:翅膀肌最後放電下端 562.1(同上)",
               600.0: "600ms 探測 20 次:每一次都跑到我們切斷為止,全腦最後放電 599.2–599.9(verification_log §模型不會自己停)",
               562.0: "600ms 探測:翅膀肌神經最後放電 562.2(同上)"}          # 不在 escape.csv 裡的另一次跑,出處同一節

LOG = (ROOT / "docs/verification_log.md").read_text()
def _const_recorded(v, label):
    """允許常數不是白名單:每個常數的數字字串必須真的出現在 verification_log(熱審 2026-09-15:純字面量字典可無限加)"""
    needles = {1.8: ["1.8 ms", "1.8ms"], 600.0: ["599.8", "600 ms", "600ms"], 562.0: ["562.2"], 599.9: ["599.9"], 562.1: ["562.1"]}.get(v, [str(v)])
    return any(n in LOG for n in needles)
for _v, _l in list(ENGINE_CONST.items()) + list(PROBE_CONST.items()):
    assert _const_recorded(_v, _l), f"常數 {_v}({_l})在 verification_log 找不到記錄,不准進允許表"

def first_spikes(csv_path=CSV):
    grp = {}
    if ANN.exists():
        import pyarrow.feather as f
        d = f.read_table(ANN, columns=["bodyId", "type"]).to_pydict()
        for b, t in zip(d["bodyId"], d["type"]):
            t = t or ""
            for g, pred in GROUPS.items():
                if pred(t): grp[int(b)] = g
        if CACHE.exists():
            cached = {int(k): v for k, v in json.loads(CACHE.read_text()).items()}
            assert cached == grp, "runs/build/escape_groups.json 與標註檔不一致,請重生"
        else:
            CACHE.write_text(json.dumps({str(k): v for k, v in sorted(grp.items())}, indent=0) + "\n")
    else:
        assert CACHE.exists(), f"標註檔 {ANN} 與快取 {CACHE} 都不在,無法判族群"
        grp = {int(k): v for k, v in json.loads(CACHE.read_text()).items()}
    first, last, count = {}, {}, collections.Counter()
    with open(csv_path) as fh:
        r = csv.DictReader(fh)
        for row in r:
            g = grp.get(int(row["flywire_id"]))
            if not g: continue
            t = float(row["t"]); count[g] += 1
            if g not in first or t < first[g]: first[g] = t
            if g not in last or t > last[g]: last[g] = t
    if first and max(last.values()) < 5:   # 秒 → 毫秒
        first = {k: v * 1000 for k, v in first.items()}; last = {k: v * 1000 for k, v in last.items()}
    first_spikes.last = last
    return first, count

def check(stages, first, count, verbose=True):
    import build_scenario as B
    allowed = {round(v, 1): g for g, v in first.items()}
    allowed.update({B.T_STIM: "T_STIM(刺激長度)", B.T_RUN: "T_RUN(播放長度)"}); allowed.update(PROBE_CONST)
    allowed.update(ENGINE_CONST)
    import math
    for g, v in getattr(first_spikes, "last", {}).items():          # 「X ms 前全部安靜」型:末次放電(或其進位)
        allowed.setdefault(round(v, 1), f"{g} 末次放電"); allowed.setdefault(float(math.ceil(v)), f"{g} 末次放電進位")
    bad = []
    for s in stages:
        if s["t"] < 0: continue
        text = s["zh"] + s.get("sub", "") + " " + s.get("en", "") + " " + s.get("sub_en", "")   # 兩種語言的數字都得對得上
        for m in re.finditer(r"(\d+(?:\.\d+)?)\s*ms", text):
            v = round(float(m.group(1)), 1)
            hit = next((g for a, g in allowed.items() if abs(a - v) <= 0.05), None)
            if verbose: print(f"  stage@{s['t']:>4} {v:6.1f} ms → {hit or '❌ 找不到對應'}")
            if not hit: bad.append((s["t"], v))
        if "PSI" in text and "沒放電" in text and count.get("psi", 0) != 0:
            bad.append((s["t"], f"PSI 說沒放電但 csv 有 {count['psi']} 次"))
    return bad

if __name__ == "__main__":
    stages = json.loads((ROOT / "content/stages.json").read_text())["stages"]
    first, count = first_spikes()
    print("首次放電(ms):", {g: round(v, 1) for g, v in sorted(first.items(), key=lambda x: x[1])}, "| 放電數:", dict(count))
    if "--self-test" in sys.argv:
        ok = True
        base = check(stages, first, count, verbose=False); print("基線:", "PASS" if not base else base); ok &= not base
        s2 = json.loads(json.dumps(stages)); s2[[i for i, s in enumerate(s2) if s["t"] >= 0][0]]["sub"] += " 99.9 ms"
        b = check(s2, first, count, verbose=False); print("負向 改數字:", "擋住 ✓" if b else "沒擋住 ✗"); ok &= bool(b)
        c2 = dict(count); c2["psi"] = 1
        b = check(stages, first, c2, verbose=False); print("負向 PSI 假放電:", "擋住 ✓" if b else "沒擋住 ✗"); ok &= bool(b)
        print("SELF-TEST", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
    bad = check(stages, first, count)
    print("RESULT:", "PASS" if not bad else f"FAIL {bad}"); sys.exit(1 if bad else 0)
