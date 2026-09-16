#!/usr/bin/env python3
"""go/no-go:刺激一片視覺柱,訊號傳得到逼近偵測器與逃跑迴路嗎?

為什麼刺激「一片柱」而不是整類視覺神經元:把 4,107 顆光受器同時以 100Hz 驅動,
相當於整個視野被閃光燈蓋住,不是生理情境,而且實測會讓全腦引爆(見 verification_log)。
真實的逼近物體只覆蓋視野一部分 → 對應一群相鄰的六角柱。

**前情**:第三方 blendi 專案自承其 LIF 模型中 medulla 運動路徑靜默,
逼近訊號是解析畫上去的。本測試獨立驗證這一點。若我們也測到傳不過去,
視覺情境必須改設計,不可假裝它會自己浮現。

設計:
  受測組  = 一片相鄰六角柱裡的 lamina 單極細胞(L1/L2/L3/L5)
  對照 A  = 同數量、散佈全視葉的同類細胞(測「成片」是否必要)
  對照 B  = 同數量、全腦隨機神經元(測「是不是視覺細胞」是否必要)
  讀出    = LC4 / LPLC2 / DNp01 / TTMn / DLMn 各自的放電率
  統計    = 5 trials,報平均與標準差(臨界系統單次無意義,見 verification_log)
"""
import subprocess, pathlib, csv, collections, json, random, statistics as st, sys
import pyarrow.feather as f

ROOT = pathlib.Path(__file__).resolve().parent.parent
FLY = ROOT.parent / "fly"
ENG, CSR = FLY/"engine/flysim", FLY/"data/mcns_w2"
ANN = FLY/"data/body-annotations-male-cns-v1.0-minconf-0.5.feather"
R = ROOT/"runs/visual"; R.mkdir(parents=True, exist_ok=True)

W_SYN, R_POI, TRIALS, T_RUN = 0.179, 150.0, 5, 500.0   # 0.179 = blendi 校準值。⚠️ 不可稱「臨界點下方」,
                                                       # 引爆與否取決於刺激集合(見 phase_sweep.json 與 verification_log)
LAMINA = {"L1", "L2", "L3", "L5"}
PATCH_R = 4.5                                          # 六角座標半徑

d = f.read_table(ANN, columns=['bodyId','type','status','superclass','subclass',
                               'assignedOlHex1','assignedOlHex2','somaSide']).to_pydict()
N = len(d['bodyId'])
tr = [i for i in range(N) if (d['status'][i] or '') == 'Traced']

# 受測組:右側一片相鄰柱裡的 lamina 單極細胞
cand = [i for i in tr if (d['type'][i] or '') in LAMINA
        and d['assignedOlHex1'][i] is not None and (d['somaSide'][i] or '') == 'R']
h1 = [d['assignedOlHex1'][i] for i in cand]; h2 = [d['assignedOlHex2'][i] for i in cand]
c1, c2 = st.median(h1), st.median(h2)
patch = [i for i, a, b in zip(cand, h1, h2) if ((a-c1)**2 + (b-c2)**2) ** .5 <= PATCH_R]
ncols = len({(d['assignedOlHex1'][i], d['assignedOlHex2'][i]) for i in patch})
print(f"受測組:右眼中央半徑 {PATCH_R} 的柱片 → {ncols} 根柱、{len(patch)} 顆 lamina 細胞", flush=True)

random.seed(20260912)
scattered = random.sample([i for i in cand if i not in set(patch)], len(patch))
allcells = random.sample(tr, len(patch))

READ = {"LC4": "LC4 逼近偵測", "LPLC2": "LPLC2 逼近偵測", "DNp01": "巨纖維",
        "TTMn": "跳躍肌", "PSI": "PSI"}
read_ids = {k: {int(d['bodyId'][i]) for i in tr if (d['type'][i] or '') == k} for k in READ}
read_ids["DLMn"] = {int(d['bodyId'][i]) for i in tr if (d['type'][i] or '').startswith("DLMn")}
READ["DLMn"] = "翅膀下壓肌"

def run(name, ids):
    sf = R/f"stim_{name}.txt"; sf.write_text("\n".join(str(int(d['bodyId'][i])) for i in ids))
    per = collections.defaultdict(list)
    for seed in range(1, TRIALS+1):
        out = R/f"{name}_{seed}.csv"
        p = subprocess.run([str(ENG), "--csr", str(CSR), "--stim-file", str(sf),
                            "--r-poi", str(R_POI), "--trials", "1", "--t-run", str(T_RUN),
                            "--seed", str(seed), "--w-syn", str(W_SYN), "--out", str(out)],
                           capture_output=True, text=True)
        if p.returncode != 0:
            print(f"  ✗ {name} seed{seed} exit={p.returncode}"); return None
        cnt = collections.Counter(); tot = 0
        with open(out) as fh:
            rd = csv.reader(fh); next(rd)
            for row in rd:
                tot += 1; b = int(row[2])
                for k, s in read_ids.items():
                    if b in s: cnt[k] += 1
        for k in read_ids: per[k].append(cnt[k] / len(read_ids[k]) / (T_RUN/1000.0))
        per["_total"].append(tot)
        out.unlink()
    return per

results = {}
for name, ids, label in (("patch", patch, "受測:成片柱"),
                         ("scattered", scattered, "對照A:同數量散佈"),
                         ("random", allcells, "對照B:全腦隨機")):
    print(f"\n{label}({len(ids)} 顆刺激,{TRIALS} trials)", flush=True)
    per = run(name, ids)
    if per is None: continue
    results[name] = {k: [round(st.mean(v), 2), round(st.stdev(v) if len(v) > 1 else 0, 2)]
                     for k, v in per.items()}
    for k in list(READ) + ["DLMn"]:
        if k not in per: continue
        m, s = st.mean(per[k]), (st.stdev(per[k]) if len(per[k]) > 1 else 0)
        print(f"   {READ.get(k,k):16s} {m:8.2f} ± {s:6.2f} Hz   (n={len(read_ids[k])})", flush=True)
    print(f"   {'全腦總放電':16s} {st.mean(per['_total']):10,.0f}")

(ROOT/"public/data/visual_pathway.json").write_text(json.dumps(
    {"protocol": {"w_syn": W_SYN, "r_poi": R_POI, "trials": TRIALS, "t_run_ms": T_RUN,
                  "patch_radius": PATCH_R, "n_columns": ncols, "n_stim": len(patch)},
     "results": results}, ensure_ascii=False, indent=1), encoding="utf-8")
print("\n→ public/data/visual_pathway.json")
