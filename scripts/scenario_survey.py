#!/usr/bin/env python3
"""情境可行性盤點:哪些感覺輸入在 MaleCNS 上真的有路徑通到運動輸出?

方法:在 w>=2 的 Traced 連接組上做 BFS,量每一類感覺神經元
①幾跳能碰到第一顆運動神經元 ②N 跳內能觸及多少運動神經元與多少身體部位。

**這是可達性不是模擬**:路徑存在不代表刺激下去真的會放電
(可能被抑制、可能訊號太弱)。可達性是必要條件不是充分條件——
過不了這關的情境一定做不出來,過了的還要實跑確認。
"""
import json, pathlib, collections, sys
import numpy as np
import pyarrow.feather as f

ROOT = pathlib.Path(__file__).resolve().parent.parent
FLY = ROOT.parent / "fly"
CSR = FLY / "data/mcns_w2"
ANN = FLY / "data/body-annotations-male-cns-v1.0-minconf-0.5.feather"
MAX_HOPS = 6

H = 64
b = np.memmap(str(CSR) + ".csr", dtype=np.uint8, mode="r")
n = int(np.frombuffer(b[8:16].tobytes(), dtype=np.int64)[0])
e = int(np.frombuffer(b[16:24].tobytes(), dtype=np.int64)[0])
o = H
row = np.frombuffer(b[o:o+(n+1)*8].tobytes(), dtype=np.int64); o += (n+1)*8
col = np.frombuffer(b[o:o+e*4].tobytes(), dtype=np.int32)
ids = np.fromfile(str(CSR) + ".ids", dtype=np.int64)
pos = {int(v): i for i, v in enumerate(ids)}
print(f"連接組 N={n:,} E={e:,}", flush=True)

d = f.read_table(ANN, columns=['bodyId','class','subclass','superclass','status']).to_pydict()
tr = [i for i in range(len(d['bodyId'])) if (d['status'][i] or '') == 'Traced']

MOTOR = {'fl':'前腳','ml':'中腳','hl':'後腳','wm':'翅膀','nm':'脖子',
         'hm':'平衡棒','ad':'腹部','pm':'口器'}
motor_idx, motor_part = {}, {}
for i in tr:
    if not (d['superclass'][i] or '').endswith('motor'): continue
    k = pos.get(int(d['bodyId'][i]))
    if k is None: continue
    part = MOTOR.get(d['subclass'][i] or '', '其他')
    motor_idx[k] = part
motor_set = np.zeros(n, dtype=bool)
for k in motor_idx: motor_set[k] = True
print(f"運動神經元在圖中 {motor_set.sum():,} 顆 / {len(set(motor_idx.values()))} 個部位\n", flush=True)

SENS = collections.defaultdict(list)
for i in tr:
    c = d['class'][i] or ''
    if 'sensory' not in (d['superclass'][i] or ''): continue
    k = pos.get(int(d['bodyId'][i]))
    if k is None: continue
    SENS[c or '(未標)'].append(k)

print(f"{'感覺類別':22s} {'總數':>6s} {'在圖中':>6s} {'首達跳數':>8s} {'6跳觸及運動元':>12s} {'部位':>6s}")
print("-" * 72)
rows = []
for cls, seeds in sorted(SENS.items(), key=lambda x: -len(x[1])):
    total = sum(1 for i in tr if (d['class'][i] or '(未標)') == cls and 'sensory' in (d['superclass'][i] or ''))
    if not seeds:
        print(f"{cls:22s} {total:6d} {0:6d} {'—':>8s} {'—':>12s} {'—':>6s}"); continue
    seen = np.zeros(n, dtype=bool)
    frontier = np.array(seeds, dtype=np.int64)
    seen[frontier] = True
    first_hit, hit = None, set()
    for hop in range(1, MAX_HOPS + 1):
        nxt = []
        for u in frontier:
            nxt.append(col[row[u]:row[u+1]])
        if not nxt: break
        cand = np.unique(np.concatenate(nxt)).astype(np.int64)
        cand = cand[~seen[cand]]
        if cand.size == 0: break
        seen[cand] = True
        m = cand[motor_set[cand]]
        if m.size and first_hit is None: first_hit = hop
        for k in m: hit.add(int(k))
        frontier = cand
    parts = {motor_idx[k] for k in hit}
    rows.append({"class": cls, "total": total, "in_graph": len(seeds),
                 "first_hop": first_hit, "motor_reached": len(hit), "parts": sorted(parts)})
    print(f"{cls:22s} {total:6d} {len(seeds):6d} {str(first_hit):>8s} {len(hit):12d} {len(parts):6d}", flush=True)

(ROOT/"public/data/scenario_survey.json").write_text(
    json.dumps({"max_hops": MAX_HOPS, "rows": rows}, ensure_ascii=False, indent=1), encoding="utf-8")
print("\n各類 6 跳內觸及的身體部位:")
for r in rows:
    if r["parts"]: print(f"   {r['class']:22s} {', '.join(r['parts'])}")
