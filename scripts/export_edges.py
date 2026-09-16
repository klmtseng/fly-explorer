#!/usr/bin/env python3
"""抽出逃跑路徑各族群之間的**真實連線**,供前端畫線。

族群清單來自 trace_drivers.py 的實測追蹤(不是教科書):
LC4/LPLC2 → {DNp01,02,03,04,06,11,103} → {AN19B001, PSI} → {TTMn, DLMn, DVMn}。

輸出 public/data/escape_edges.json:
  nodes: [{i: soma索引, t: type, s: stage}]   ← 只含有細胞體座標的
  edges: [[from_node, to_node, weight]]       ← 兩端都在 nodes 裡的邊,weight 帶正負號
連線是連接組裡真實存在的(資料);前端把它畫成直線是示意(我們畫的),
規範見 docs/visual_provenance.md 的混合情況。
"""
import json, pathlib, collections
import numpy as np
import pyarrow.feather as f

ROOT = pathlib.Path(__file__).resolve().parent.parent
FLY = ROOT.parent / "fly"
CSR = FLY / "data/mcns_w2"
ANN = FLY / "data/body-annotations-male-cns-v1.0-minconf-0.5.feather"
OUT = ROOT / "public/data/escape_edges.json"

STAGE_OF = {}
for t in ("LC4", "LPLC2"): STAGE_OF[t] = "detect"
for t in ("DNp01","DNp02","DNp03","DNp04","DNp06","DNp11","DNp103"): STAGE_OF[t] = "descend"
for t in ("AN19B001", "PSI"): STAGE_OF[t] = "premotor"
for t in ("TTMn",): STAGE_OF[t] = "jump"
def stage_of(ty):
    if ty in STAGE_OF: return STAGE_OF[ty]
    if ty.startswith("DLMn") or ty.startswith("DVMn"): return "wing"
    return None

H = 64
b = np.memmap(str(CSR)+".csr", dtype=np.uint8, mode="r")
n = int(np.frombuffer(b[8:16].tobytes(), dtype=np.int64)[0]); e = int(np.frombuffer(b[16:24].tobytes(), dtype=np.int64)[0])
o = H
row = np.frombuffer(b[o:o+(n+1)*8].tobytes(), dtype=np.int64); o += (n+1)*8
col = np.frombuffer(b[o:o+e*4].tobytes(), dtype=np.int32); o += e*4
w   = np.frombuffer(b[o:o+e*2].tobytes(), dtype=np.int16)
csr_ids = np.fromfile(str(CSR)+".ids", dtype=np.int64)

soma_ids = np.fromfile(ROOT/"build-data/soma_ids.bin", dtype=np.int64)
soma_pos = {int(v): i for i, v in enumerate(soma_ids)}

d = f.read_table(ANN, columns=['bodyId','type','status']).to_pydict()
members = {}   # bodyId -> (type, stage)
for i in range(len(d['bodyId'])):
    if (d['status'][i] or '') != 'Traced': continue
    st = stage_of(d['type'][i] or '')
    if st: members[int(d['bodyId'][i])] = (d['type'][i], st)

nodes, node_idx, missing = [], {}, collections.Counter()
for bid, (ty, st) in members.items():
    si = soma_pos.get(bid)
    if si is None: missing[ty] += 1; continue
    node_idx[bid] = len(nodes); nodes.append({"i": si, "t": ty, "s": st, "b": bid})

# 只留**順著階段往前**的邊:偵測器層內部有 14,691 條互連(LC4↔LPLC2),那是局部處理不是傳遞路徑,
# 畫出來會把真正的傳導線糊掉。階段順序 = 訊號方向;同層與逆向邊不畫(資料仍在連接組裡,只是不渲染)。
ORDER = {"detect": 0, "descend": 1, "premotor": 2, "jump": 3, "wing": 3}
csr_idx = {int(v): i for i, v in enumerate(csr_ids)}
edges = []
by_pair = collections.Counter()
for bid_src in node_idx:
    ci = csr_idx.get(bid_src)
    if ci is None: continue
    for k in range(row[ci], row[ci+1]):
        bid_dst = int(csr_ids[col[k]])
        if bid_dst in node_idx and ORDER[members[bid_dst][1]] > ORDER[members[bid_src][1]]:
            edges.append([node_idx[bid_src], node_idx[bid_dst], int(w[k])])
            by_pair[(members[bid_src][1], members[bid_dst][1])] += 1

OUT.write_text(json.dumps({"nodes": nodes, "edges": edges,
    "note": "連線=連接組真實邊(mcns_w2, w>=2);直線形狀為示意。族群清單來自 trace_drivers.py 實測。"},
    ensure_ascii=False), encoding="utf-8")
print(f"節點 {len(nodes)} 顆,邊 {len(edges):,} 條 → {OUT.name} ({OUT.stat().st_size/1024:.0f} KB)")
if missing: print("  無細胞體座標而略過:", dict(missing))
print("  各段連線數:")
for (a, c), v in sorted(by_pair.items(), key=lambda x: -x[1])[:10]:
    print(f"    {a:9s} → {c:9s} {v:6,d}")
