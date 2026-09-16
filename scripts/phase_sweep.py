#!/usr/bin/env python3
"""掃 (w_syn × 刺激顆數) 的相圖,選一個可用的操作點。

判準不是絕對活動量,是**輸入輸出彈性** d(log 輸出)/d(log 刺激顆數):
  彈性 ≈ 1  → 輸出與輸入等比例,健康
  彈性 → 0  → 飽和,輸入再大也沒差,指標已被汙染
論文值 w_syn=0.275 在 k=25 以上彈性趨近 0,所以那裡量到的東西不是訊號傳遞。

刺激集合用固定亂數種子的隨機神經元,且**每個 k 都是前一個 k 的超集**
(巢狀取樣),這樣同一列的差異只來自「多加了哪些神經元」,不摻雜取樣變異。
"""
import subprocess, pathlib, random, json, math, time, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
FLY = ROOT.parent / "fly"
ENG, CSR = FLY/"engine/flysim", FLY/"data/mcns_w2"
R = ROOT/"runs/phase"; R.mkdir(parents=True, exist_ok=True)
CKPT = R/"phase.json"

KS = [10, 25, 50, 100, 250, 600, 1500, 4000]
WS = [0.275, 0.24, 0.21, 0.179, 0.15, 0.12, 0.09]
T_RUN, R_POI = 200.0, 100.0

ids = np.fromfile(str(CSR)+".ids", dtype=np.int64)
random.seed(20260912)
perm = random.sample(list(ids), max(KS))          # 巢狀:KS[i] 是 KS[i+1] 的子集
for k in KS:
    (R/f"stim_{k}.txt").write_text("\n".join(map(str, perm[:k])))

res = json.loads(CKPT.read_text()) if CKPT.exists() else {}
t0 = time.time()
for w in WS:
    for k in KS:
        key = f"{w}|{k}"
        if key in res: continue
        out = R/f"w{w}_k{k}.csv"
        p = subprocess.run([str(ENG), "--csr", str(CSR), "--stim-file", str(R/f"stim_{k}.txt"),
                            "--r-poi", str(R_POI), "--trials", "1", "--t-run", str(T_RUN),
                            "--seed", "42", "--w-syn", str(w), "--out", str(out)],
                           capture_output=True, text=True)
        if p.returncode != 0:
            print(f"  ✗ w={w} k={k} exit={p.returncode}", flush=True); res[key] = None
        else:
            res[key] = sum(1 for _ in open(out)) - 1
            out.unlink()                                   # CSV 很大,數完就刪
        CKPT.write_text(json.dumps(res))                   # 每格 checkpoint,中斷可續
    print(f"  w={w} 完成 ({time.time()-t0:.0f}s)", flush=True)

print(f"\n{'w_syn':>7s} {'gain':>5s} " + " ".join(f"{k:>8d}" for k in KS) + "   彈性(k=10→4000)")
print("-" * (14 + 9*len(KS) + 18))
table = []
for w in WS:
    v = [res.get(f"{w}|{k}") for k in KS]
    lo, hi = v[0], v[-1]
    el = (math.log(hi/lo) / math.log(KS[-1]/KS[0])) if (lo and hi) else float('nan')
    table.append({"w_syn": w, "gain": round(w/0.275, 2), "counts": v, "elasticity": round(el, 3)})
    print(f"{w:7.3f} {w/0.275:5.2f} " + " ".join(f"{(x if x is not None else -1):8,d}" for x in v) + f"   {el:6.3f}")

(ROOT/"public/data/phase_sweep.json").write_text(json.dumps(
    {"protocol": {"r_poi": R_POI, "t_run_ms": T_RUN, "trials": 1, "csr": "mcns_w2",
                  "stim": "巢狀隨機取樣 seed=20260912"},
     "ks": KS, "table": table}, ensure_ascii=False, indent=1), encoding="utf-8")
print("\n→ public/data/phase_sweep.json")
