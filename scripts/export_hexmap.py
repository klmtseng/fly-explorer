#!/usr/bin/env python3
"""匯出視葉的六角柱地圖,供「眼睛看到東西」的**注入示意**用。

每根柱子 = 複眼上一個小眼對應的腦內處理單元(右眼 892 / 左眼 879,見 verification_log)。
輸出每柱的:側別、六角座標、該柱所有有細胞體座標的柱狀神經元在 soma.bin 裡的索引、
以及「離該眼中心的正規化距離 d∈[0,1]」——逼近物體=從中心往外擴的環,前端用 d 決定點亮順序。

⚠️ 這是③注入層的資料:模型的視覺前端實測算不出逼近(LC4 僅 1.23Hz、LPLC2 為 0),
所以「依序點亮」是我們畫的示意,前端必須以洋紅渲染並標示,不得與真實放電(綠)混同。
"""
import json, pathlib, collections, statistics as st
import numpy as np
import pyarrow.feather as f

ROOT = pathlib.Path(__file__).resolve().parent.parent
ANN = ROOT.parent / "fly/data/body-annotations-male-cns-v1.0-minconf-0.5.feather"
OUT = ROOT / "public/data/hexmap.json"

soma_ids = np.fromfile(ROOT/"build-data/soma_ids.bin", dtype=np.int64)
pos = {int(v): i for i, v in enumerate(soma_ids)}
d = f.read_table(ANN, columns=['bodyId','status','assignedOlHex1','assignedOlHex2','somaSide']).to_pydict()

cols = collections.defaultdict(list)
for i in range(len(d['bodyId'])):
    if (d['status'][i] or '') != 'Traced': continue
    h1, h2, side = d['assignedOlHex1'][i], d['assignedOlHex2'][i], d['somaSide'][i]
    if h1 is None or h2 is None or side not in ('L', 'R'): continue
    si = pos.get(int(d['bodyId'][i]))
    if si is None: continue
    cols[(side, int(h1), int(h2))].append(si)

out = []
for side in ('L', 'R'):
    keys = [k for k in cols if k[0] == side]
    # 眼睛中心用**官方定義** hex=(18,19),不用中位數:
    # Reiser lab 補充碼 docs/coordinate-systems.md 原句 "We define the hex1 hex2 coordinates [18 19]
    # as our origin for P Q"(github.com/reiserlab/male-drosophila-visual-system-connectome-code)。
    # ⚠️ 「哪個方向是視野前方」只有第三方回歸推導且正負號無官方原句,不採用,標待確認。
    c1, c2 = 18.0, 19.0
    dmax = max(((k[1]-c1)**2 + (k[2]-c2)**2) ** .5 for k in keys) or 1.0
    for k in keys:
        dist = ((k[1]-c1)**2 + (k[2]-c2)**2) ** .5 / dmax
        out.append({"s": side, "h": [k[1], k[2]], "d": round(dist, 3), "i": cols[k]})
n_pts = sum(len(c["i"]) for c in out)
OUT.write_text(json.dumps({"cols": out,
    "note": "③注入示意用。d=離該眼中心的正規化距離,前端據此做由內向外的點亮序。柱狀神經元索引對應 soma.bin。"},
    ensure_ascii=False), encoding="utf-8")
print(f"柱 {len(out):,}(L {sum(1 for c in out if c['s']=='L')} / R {sum(1 for c in out if c['s']=='R')}),"
      f"含神經元 {n_pts:,} 顆 → {OUT.name} ({OUT.stat().st_size/1024:.0f} KB)")
