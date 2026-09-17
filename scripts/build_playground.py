#!/usr/bin/env python3
"""實驗台的資料:同一套協定下,換不同的刺激集合,真的各跑五次。

動機(使用者 2026-09-17):想讓人可以互動,而不是只看一段固定的重播。
做法選的是「每一格都是真跑出來的」那條路——使用者選條件,網站顯示那個條件實際量到的結果。
**不是**在瀏覽器裡即時模擬:出貨的連線檔只有興奮性邊,拿它即時算會一點就爆,
而且會推翻本站自己的發現(PSI 不放電是被抑制壓住的,見 docs/verification_log.md §PSI 抑制消融)。

協定與出貨情境完全相同(scripts/build_scenario.py):w_syn 0.179、150 Hz、刺激前 6 ms、跑 250 ms。
只有刺激集合在變。每個條件跑 **5 個亂數種子**,輸出中位數與最小/最大值——
單次跑不可採信是本專案付過學費的教訓(見 docs/verification_log.md §雙穩態)。

需要研究倉的引擎與 CSR(不公開)。公開倉的讀者拿不到原始資料,但輸出的
public/data/playground.json 帶著每一格的每一次原始數字,可以自己檢查我們有沒有亂算。

用法:python3 scripts/build_playground.py [--seeds 5] [--dry-run]
"""
import argparse, json, pathlib, subprocess, sys, csv, collections, statistics, time

ROOT = pathlib.Path(__file__).resolve().parent.parent
FLY = ROOT.parent / "fly"
ENG, CSR = FLY / "engine/flysim", FLY / "data/mcns_w2"
ANN = FLY / "data/body-annotations-male-cns-v1.0-minconf-0.5.feather"
WORK = ROOT / "runs/playground"; WORK.mkdir(parents=True, exist_ok=True)
OUT = ROOT / "public/data/playground.json"

W_SYN, R_POI, T_RUN, T_STIM = 0.179, 150.0, 250.0, 6.0   # 與出貨情境同一套協定

# 讀出的族群:與 scripts/verify_stages.py 同一套判定規則,兩邊必須一致
GROUPS = {
    "detect": lambda t: t in ("LC4", "LPLC2"),
    "gf":     lambda t: t == "DNp01",
    "jump":   lambda t: t == "TTMn",
    "wing":   lambda t: t.startswith("DLMn"),
    "psi":    lambda t: t == "PSI",
}


def load_types():
    import pyarrow.feather as f
    d = f.read_table(ANN, columns=["bodyId", "type"]).to_pydict()
    return {int(b): (t or "") for b, t in zip(d["bodyId"], d["type"])}


def run_one(stim_path, seed, tag):
    out = WORK / f"{tag}_s{seed}.csv"
    cmd = [str(ENG), "--csr", str(CSR), "--stim-file", str(stim_path), "--measure", "11498",
           "--r-poi", str(R_POI), "--trials", "1", "--t-run", str(T_RUN), "--seed", str(seed),
           "--stim-ms", str(T_STIM), "--w-syn", str(W_SYN), "--out", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"引擎失敗 {tag} seed={seed}:{r.stderr[-400:]}")
    return out


def readouts(csv_path, grp, stim_set):
    """每個族群的首次放電時刻(ms)與放電次數,外加總放電數與**下游**放電數。

    下游 = 總放電扣掉被直接刺激的那些神經元自己的放電。冷審 2026-09-17 指出:
    只報總數會讓對照組「贏過」低劑量的真條件(隨機 311 顆 346 次 vs 39 顆偵測器 160 次),
    因為前者的數字幾乎全是被注入者自己在響。下游才是「訊號有沒有傳出去」。"""
    first, count, total, own = {}, collections.Counter(), 0, 0
    with open(csv_path) as fh:
        for row in csv.DictReader(fh):
            total += 1
            bid = int(row["flywire_id"])
            if bid in stim_set: own += 1
            g = grp.get(bid)
            if not g:
                continue
            t = float(row["t"])
            count[g] += 1
            if g not in first or t < first[g]:
                first[g] = t
    scale = 1000.0 if first and max(first.values()) < 5 else 1.0   # 秒 → 毫秒
    return {"total_spikes": total, "stim_spikes": own, "downstream_spikes": total - own,
            "first_ms": {g: round(first[g] * scale, 2) for g in first},
            "count": {g: count[g] for g in count}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    if not ENG.exists():
        sys.exit(f"找不到引擎 {ENG}(研究倉不公開;公開倉無法重跑這支)")

    import numpy as np
    types = load_types()
    base = [int(x) for x in (ROOT / "runs/build/escape.stim").read_text().split()]
    lc4 = [i for i in base if types.get(i) == "LC4"]
    lplc2 = [i for i in base if types.get(i) == "LPLC2"]
    all_ids = np.fromfile(FLY / "data/mcns_w2.ids", dtype=np.int64).tolist()   # 二進位 int64,不是文字檔
    print(f"基準刺激 {len(base)} 顆:LC4 {len(lc4)} + LPLC2 {len(lplc2)};CSR 神經元 {len(all_ids)}")

    # 條件:固定集合 + 每個種子重抽的集合(後者的離散度正是「挑哪些偵測器」造成的)
    fixed = {
        "both":  ("兩種偵測器全上(出貨情境)", "Both detector types (the shipped scenario)", base),
        "lc4":   ("只刺激 LC4", "LC4 only", lc4),
        "lplc2": ("只刺激 LPLC2", "LPLC2 only", lplc2),
    }
    resampled = {
        "dose_155": ("隨機挑 155 顆偵測器", "155 detectors, picked at random", 155, "detectors"),
        "dose_78":  ("隨機挑 78 顆偵測器", "78 detectors, picked at random", 78, "detectors"),
        "dose_39":  ("隨機挑 39 顆偵測器", "39 detectors, picked at random", 39, "detectors"),
        "dose_16":  ("隨機挑 16 顆偵測器", "16 detectors, picked at random", 16, "detectors"),
        "rand_311": ("同樣數量的隨機神經元(311)", "311 random neurons, same count as the real set", 311, "anywhere"),
        "rand_126": ("同樣數量的隨機神經元(126)", "126 random neurons, matching the LC4 count", 126, "anywhere"),
    }
    grp = {}
    for bid, t in types.items():
        for g, pred in GROUPS.items():
            if pred(t):
                grp[bid] = g

    conditions = []
    t0 = time.time()
    for key, (zh, en, ids) in fixed.items():
        runs = []
        for s in range(1, a.seeds + 1):
            p = WORK / f"{key}.stim"; p.write_text("\n".join(str(i) for i in ids) + "\n")
            if a.dry_run: continue
            runs.append(readouts(run_one(p, s, key), grp, set(ids)))
        conditions.append({"key": key, "zh": zh, "en": en, "n_stim": len(ids), "resampled": False, "runs": runs})
        print(f"  {key:9} n={len(ids):4}  {len(runs)} 次")
    for key, (zh, en, n, pool) in resampled.items():
        runs = []
        for s in range(1, a.seeds + 1):
            rng = np.random.RandomState(1000 + s)
            src = base if pool == "detectors" else all_ids
            ids = sorted(rng.choice(src, size=n, replace=False).tolist())
            p = WORK / f"{key}_s{s}.stim"; p.write_text("\n".join(str(i) for i in ids) + "\n")
            if a.dry_run: continue
            runs.append(readouts(run_one(p, s, key), grp, set(ids)))
        conditions.append({"key": key, "zh": zh, "en": en, "n_stim": n, "resampled": True, "pool": pool, "runs": runs})
        print(f"  {key:9} n={n:4}  {len(runs)} 次")

    def summarise(c):
        """中位數 + 最小/最大。首次放電只在真的放電的那幾次裡算,並記錄幾次有放電。"""
        out = {}
        tot = [r["total_spikes"] for r in c["runs"]]
        out["total_spikes"] = {"median": int(statistics.median(tot)), "min": min(tot), "max": max(tot)}
        for fld in ("stim_spikes", "downstream_spikes"):
            v = [r[fld] for r in c["runs"]]
            out[fld] = {"median": int(statistics.median(v)), "min": min(v), "max": max(v)}
        for g in GROUPS:
            firsts = [r["first_ms"][g] for r in c["runs"] if g in r["first_ms"]]
            counts = [r["count"].get(g, 0) for r in c["runs"]]
            out[g] = {"fired_in": len(firsts), "of": len(c["runs"]),
                      "first_ms": {"median": round(statistics.median(firsts), 2), "min": min(firsts), "max": max(firsts)} if firsts else None,
                      "count": {"median": int(statistics.median(counts)), "min": min(counts), "max": max(counts)}}
        return out

    if not a.dry_run:
        for c in conditions:
            c["summary"] = summarise(c)

    # ---- 600 ms 探測:支撐「模型不會自己停」的那兩個數字原本是單次跑(冷審 2026-09-17 P1-4)----
    probe = []
    if not a.dry_run:
        sf = WORK / "probe600.stim"; sf.write_text("\n".join(str(i) for i in base) + "\n")
        for sd in range(1, a.seeds + 1):
            out = WORK / f"probe600_s{sd}.csv"
            cmd = [str(ENG), "--csr", str(CSR), "--stim-file", str(sf), "--measure", "11498",
                   "--r-poi", str(R_POI), "--trials", "1", "--t-run", "600", "--seed", str(sd),
                   "--stim-ms", str(T_STIM), "--w-syn", str(W_SYN), "--out", str(out)]
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode != 0: sys.exit(f"600ms 探測失敗 seed={sd}")
            last_all, last_wing = 0.0, 0.0
            with open(out) as fh:
                for row in csv.DictReader(fh):
                    t = float(row["t"]); g = grp.get(int(row["flywire_id"]))
                    last_all = max(last_all, t)
                    if g == "wing": last_wing = max(last_wing, t)
            sc = 1000.0 if last_all < 5 else 1.0
            probe.append({"seed": sd, "last_spike_ms": round(last_all * sc, 1), "last_wing_ms": round(last_wing * sc, 1)})
        print(f"  probe600  {len(probe)} 次;最後放電 {min(p['last_spike_ms'] for p in probe)}–{max(p['last_spike_ms'] for p in probe)} ms")
    data = {
        "note": f"實驗台:同一套協定換刺激集合,每格真跑 {a.seeds} 次。每一格的每一次原始數字都在 runs 欄裡,可自行檢查。",
        "protocol": {"w_syn_mv": W_SYN, "r_poi_hz": R_POI, "t_run_ms": T_RUN, "stim_ms": T_STIM,
                     "csr": "mcns_w2", "engine": "flysim (LIF, 化學突觸, 無可塑性)", "seeds": a.seeds,
                     "same_as": "public/data/scenarios/escape.bin 的協定完全相同"},
        "groups": {"detect": "逼近偵測器 LC4+LPLC2", "gf": "巨纖維 DNp01", "jump": "跳躍肌運動神經元 TTMn",
                   "wing": "翅膀下壓肌運動神經元 DLMn", "psi": "教科書中繼 PSI"},
        "probe_600": {"note": "同一組刺激跑滿 600 ms,看模型會不會自己停;每次記全腦最後一次放電與翅膀肌最後一次放電",
                      "runs": probe,
                      "summary": ({"last_spike_ms": {"median": statistics.median([p["last_spike_ms"] for p in probe]),
                                                     "min": min(p["last_spike_ms"] for p in probe), "max": max(p["last_spike_ms"] for p in probe)},
                                   "last_wing_ms": {"median": statistics.median([p["last_wing_ms"] for p in probe]),
                                                    "min": min(p["last_wing_ms"] for p in probe), "max": max(p["last_wing_ms"] for p in probe)},
                                   "stopped_early": sum(1 for p in probe if p["last_spike_ms"] < 590), "of": len(probe)} if probe else None)},
        "conditions": conditions,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print(f"→ {OUT}  ({OUT.stat().st_size/1024:.0f} KB, {time.time()-t0:.0f} 秒)")


if __name__ == "__main__":
    main()
