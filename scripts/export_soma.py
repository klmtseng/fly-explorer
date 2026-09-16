#!/usr/bin/env python3
"""把 MaleCNS 的神經元細胞體座標匯出成前端可直接讀的二進位。

輸出 web/data/soma.bin:
  [0:4]   uint32  n
  [4:16]  float32 x3   量化的原點 (nm)
  [16:28] float32 x3   量化的刻度 (nm / 單位)
  [28:]   n × (int16 x, int16 y, int16 z, uint8 group, uint8 pad)

group 是 superclass 壓成的大類編碼,讓前端能按功能上色:
  0=其他/中間神經元  1=感覺(輸入)  2=運動(輸出)  3=下行(指令)  4=上行(回饋)  5=視葉內在

⚠️ 座標單位:標註檔沒寫單位。**推定為 8nm voxel**——由尺寸合理性反推
(z 軸跨距 134,531 × 8nm ≈ 1.08mm,果蠅腦+腹神經索確實約 1mm;
 x 軸 93,668 × 8nm ≈ 750µm,果蠅腦寬約 600-800µm,兩軸都吻合)。
**此推定未在論文原文核對,標待確認。** 對渲染無影響(只影響標尺文字),
因為三軸共用同一個 scale,形狀比例正確。

⚠️ 感覺神經元幾乎全部沒有細胞體座標(cb_sensory 0/4,868、vnc_sensory 2/6,365、
ol_sensory 28/4,114),**這不是資料缺漏是生物學**:昆蟲感覺神經元的細胞本體
長在觸角/眼睛/腳毛等周邊感覺器官,不在被掃描的中樞神經系統體積內,
只有軸突伸進來。所以點雲畫得出 140,024 顆,少掉的 25,098 顆幾乎全是感覺神經元。
"""
import json, pathlib, struct
import numpy as np
import pyarrow.feather as f

HERE = pathlib.Path(__file__).resolve().parent.parent
ANN = HERE.parent / "fly/data/body-annotations-male-cns-v1.0-minconf-0.5.feather"
OUT = HERE / "public/data/soma.bin"
META = HERE / "public/data/soma_meta.json"

d = f.read_table(ANN, columns=['bodyId','somaLocation','superclass','status','type']).to_pydict()
N = len(d['bodyId'])

def group_of(sc):
    sc = sc or ''
    if sc.endswith('motor') or 'efferent' in sc or 'endocrine' in sc: return 2
    if 'sensory' in sc:            return 1
    if sc == 'descending_neuron':  return 3
    if sc == 'ascending_neuron':   return 4
    if sc in ('ol_intrinsic', 'visual_projection', 'visual_centrifugal'): return 5   # 含 LC4/LPLC2
    return 0

rows = []
body_order = []      # 與 soma.bin 逐筆對齊的 bodyId,供放電資料換算索引用
for i in range(N):
    loc = d['somaLocation'][i]
    if loc is None or len(loc) != 3:            continue
    if (d['status'][i] or '') != 'Traced':      continue
    rows.append((loc[0], loc[1], loc[2], group_of(d['superclass'][i])))
    body_order.append(int(d['bodyId'][i]))

xyz = np.array([[r[0], r[1], r[2]] for r in rows], dtype=np.float64)
grp = np.array([r[3] for r in rows], dtype=np.uint8)
n = len(rows)

lo = xyz.min(axis=0); hi = xyz.max(axis=0)
# 用同一個 scale 讓三軸等比,不然腦會被拉變形
scale = (hi - lo).max() / 32000.0
origin = (lo + hi) / 2.0
q = np.rint((xyz - origin) / scale).astype(np.int16)

with open(OUT, 'wb') as fh:
    fh.write(struct.pack('<I', n))
    fh.write(struct.pack('<3f', *origin.astype(np.float32)))
    fh.write(struct.pack('<3f', *([scale] * 3)))
    buf = np.zeros((n, 5), dtype=np.uint8)
    qb = q.astype('<i2').tobytes()
    arr = np.frombuffer(qb, dtype=np.uint8).reshape(n, 6)
    out = np.concatenate([arr, grp.reshape(-1, 1), np.zeros((n, 1), np.uint8)], axis=1)
    fh.write(out.tobytes())

assert len(body_order) == n, "bodyId 順序與點數不符"
import numpy as _np
# 放 build-data/ 不放 public/:這是**建置期**用來把 body id 換算成點雲索引的對照表,
# 前端不需要它(分幀資料直接存索引)。放進 public 會讓部署多傳 1.1MB。
(HERE/"build-data").mkdir(exist_ok=True)
_np.array(body_order, dtype=_np.int64).tofile(HERE/"build-data/soma_ids.bin")

names = {0:'中間神經元',1:'感覺(輸入)',2:'運動(輸出)',3:'下行(指令)',4:'上行(回饋)',5:'視葉內在'}
counts = {names[k]: int((grp == k).sum()) for k in sorted(names)}
META.write_text(json.dumps({
    "n": n, "origin_voxel": origin.tolist(), "scale_voxel_per_unit": scale,
    "voxel_nm_assumed": 8, "voxel_nm_verified": False,
    "bbox_voxel": {"min": lo.tolist(), "max": hi.tolist()},
    "extent_um_assumed": ((hi - lo) * 8 / 1000.0).tolist(),
    "missing_note": "感覺神經元細胞本體在周邊器官,不在本體積內,故點雲不含它們",
    "groups": counts,
    "source": "MaleCNS v1.0 somaLocation, status=Traced. CC-BY 4.0, Berg et al. Cell 2026.",
}, ensure_ascii=False, indent=2), encoding='utf-8')

print(f"n = {n:,}")
ext_um = (hi - lo) * 8 / 1000.0   # 推定 8nm voxel
print(f"bbox (voxel)  min={lo.astype(int).tolist()}  max={hi.astype(int).tolist()}")
print(f"推定實際尺寸  {ext_um.round(1).tolist()} µm  (假設 8nm/voxel,待確認)")
print(f"  合理性檢查:果蠅腦寬約 600-800µm、腦+VNC 全長約 1mm")
print(f"量化刻度   {scale:.2f} voxel/unit")
for k, v in counts.items(): print(f"   {k:12s} {v:7,d}")
print(f"→ {OUT}  ({OUT.stat().st_size/1e6:.2f} MB)")
