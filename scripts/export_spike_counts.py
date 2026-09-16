#!/usr/bin/env python3
"""即時放電計數器的資料(DESIGN.md R3):出貨情境 runs/build/escape.csv 每一幀(1 ms)結束時的**累計真實放電次數**。
輸出 public/data/scenarios/escape_spikes.json = {"dtMs":1,"cumulative":[...250 個整數],"total":N,"source":"runs/build/escape.csv"}
斷言:最後一個累計數 == csv 列數(trial 0)。這是 ● 我們量的數字,不是點雲亮點數(亮點含鈣衰減會重複計)。"""
import csv, json, sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts")); import build_scenario as B
rows = list(csv.DictReader(open(ROOT / "runs/build/escape.csv")))
rows = [r for r in rows if int(r["trial"]) == 0]
ts = [float(r["t"]) for r in rows]
if ts and max(ts) < 5: ts = [t * 1000 for t in ts]          # 秒 → 毫秒
n_frames = int(B.T_RUN / B.DT_MS)
cum = [0] * n_frames
for t in ts:
    f = min(n_frames - 1, int(t // B.DT_MS))
    cum[f] += 1
for i in range(1, n_frames): cum[i] += cum[i - 1]
assert cum[-1] == len(rows), (cum[-1], len(rows))
out = {"dtMs": B.DT_MS, "cumulative": cum, "total": len(rows), "source": "runs/build/escape.csv(trial 0)", "script": "scripts/export_spike_counts.py"}
(ROOT / "public/data/scenarios/escape_spikes.json").write_text(json.dumps(out))
print(f"frames={n_frames} total_spikes={len(rows)} at 14ms={cum[14]} at 30ms={cum[30]} at 249ms={cum[-1]}")
