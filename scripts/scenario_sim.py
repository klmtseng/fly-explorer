#!/usr/bin/env python3
"""情境可行性:對每一類感覺輸入實跑 LIF 模擬,量真正到達運動神經元的訊號。

為什麼不用圖的可達性:實測過,這張圖平均出度 92,從 25 顆出發兩跳就觸及全圖,
十二類全部回報「815 顆運動神經元、9 個部位」——恆真,零鑑別力。
可達性是必要條件不是充分條件,要分辨強弱只能實跑。

短跑(1 trial × 300ms)只為排序與篩選;入選的情境再用完整協定重跑。
"""
import subprocess, pathlib, csv, collections, json, sys, time
import pyarrow.feather as f

ROOT = pathlib.Path(__file__).resolve().parent.parent
FLY = ROOT.parent / "fly"
ENG = FLY / "engine/flysim"
CSR = FLY / "data/mcns_w2"
ANN = FLY / "data/body-annotations-male-cns-v1.0-minconf-0.5.feather"
RUNS = ROOT / "runs/scenarios"; RUNS.mkdir(parents=True, exist_ok=True)
R_POI, TRIALS, T_RUN = 100.0, 1, 300.0

d = f.read_table(ANN, columns=['bodyId','class','subclass','superclass','status']).to_pydict()
tr = [i for i in range(len(d['bodyId'])) if (d['status'][i] or '') == 'Traced']
MOTOR = {'fl':'前腳','ml':'中腳','hl':'後腳','wm':'翅膀','nm':'脖子',
         'hm':'平衡棒','ad':'腹部','pm':'口器'}
motor = {int(d['bodyId'][i]): MOTOR.get(d['subclass'][i] or '', '其他')
         for i in tr if (d['superclass'][i] or '').endswith('motor')}

groups = collections.defaultdict(list)
for i in tr:
    if 'sensory' in (d['superclass'][i] or ''):
        groups[d['class'][i] or '(未標)'].append(int(d['bodyId'][i]))

rows = []
print(f"協定:{R_POI:.0f}Hz × {TRIALS} trial × {T_RUN:.0f}ms,csr=mcns_w2\n", flush=True)
print(f"{'感覺類別':24s} {'刺激':>5s} {'總放電':>9s} {'運動放電':>8s} {'運動元':>6s} 部位")
print("-" * 84)
for cls, ids in sorted(groups.items(), key=lambda x: -len(x[1])):
    sf = RUNS / f"stim_{cls}.txt"; sf.write_text("\n".join(map(str, ids)))
    out = RUNS / f"{cls}.csv"
    t0 = time.time()
    r = subprocess.run([str(ENG), "--csr", str(CSR), "--stim-file", str(sf),
                        "--r-poi", str(R_POI), "--trials", str(TRIALS),
                        "--t-run", str(T_RUN), "--seed", "42", "--out", str(out)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"{cls:24s} 引擎失敗 exit={r.returncode}: {r.stderr.strip()[:60]}"); continue
    tot = 0; mspk = collections.Counter(); mset = set()
    with open(out) as fh:
        rd = csv.reader(fh); next(rd)
        for row in rd:
            tot += 1
            b = int(row[2])
            if b in motor:
                mspk[motor[b]] += 1; mset.add(b)
    parts = sorted(mspk, key=lambda k: -mspk[k])
    top = ", ".join(f"{p}:{mspk[p]}" for p in parts[:4]) or "(無)"
    rows.append({"class": cls, "n_stim": len(ids), "total_spikes": tot,
                 "motor_spikes": sum(mspk.values()), "motor_neurons": len(mset),
                 "by_part": dict(mspk), "secs": round(time.time()-t0, 1)})
    print(f"{cls:24s} {len(ids):5d} {tot:9,d} {sum(mspk.values()):8,d} {len(mset):6d} {top}", flush=True)

(ROOT/"public/data/scenario_sim.json").write_text(
    json.dumps({"protocol": {"r_poi": R_POI, "trials": TRIALS, "t_run_ms": T_RUN, "csr": "mcns_w2"},
                "rows": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"\n→ public/data/scenario_sim.json")
