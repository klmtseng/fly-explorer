#!/usr/bin/env python3
"""光暈渲染測試:把真實放電資料畫成鈣成像式的螢光畫面。

亮度模型模仿 GCaMP 鈣螢光:每次放電讓該神經元的值 +1,之後以指數衰減。
這不是任意的美術選擇——真實神經科學的活體成像就是這個物理過程,
所以「亮度 = 近期放電密度」在科學上是誠實的表示法。

用途:在投入做 Three.js 之前,先用靜態圖確認美學方向。
"""
import csv, collections, pathlib, sys
import numpy as np
import pyarrow.feather as f
from PIL import Image

import os
ROOT = pathlib.Path(__file__).resolve().parent.parent
FLY = pathlib.Path(os.environ.get("FLY_REPO", ROOT.parent / "fly"))   # 研究倉(不公開);沒有時此腳本跑不了,見 scripts/fly/README.md
OUT = ROOT / "scratch"
TAU_MS = 80.0            # 螢光衰減時間常數
W, H = 1280, 760
FRAMES_MS = [40, 120, 300, 700]   # 要畫哪幾個時刻

ann = f.read_table(FLY/"data/body-annotations-male-cns-v1.0-minconf-0.5.feather",
                   columns=['bodyId','somaLocation','status','superclass']).to_pydict()
pos, grp = {}, {}
for i in range(len(ann['bodyId'])):
    loc = ann['somaLocation'][i]
    if loc is None or (ann['status'][i] or '') != 'Traced': continue
    pos[ann['bodyId'][i]] = loc
    sc = ann['superclass'][i] or ''
    grp[ann['bodyId'][i]] = 2 if sc.endswith('motor') else (3 if sc=='descending_neuron' else 0)

# 只取 trial 0
spikes = []
with open(FLY/"runs/engine/taskA_real.csv") as fh:
    r = csv.reader(fh); next(r)
    for row in r:
        if row[0] != '0': continue
        b = int(row[2])
        if b in pos: spikes.append((float(row[1])*1000.0, b))
spikes.sort()
print(f"trial 0 可定位放電 {len(spikes):,}")

P = np.array([pos[b] for b in pos], dtype=np.float32)
idx = {b: k for k, b in enumerate(pos)}
G = np.array([grp[b] for b in pos], dtype=np.uint8)

# 背側視角 (x, y)
u, v = P[:,0], P[:,1]
pad = 40
su = (u - u.min()) / (u.max()-u.min()) * (W-2*pad) + pad
sv = (v - v.min()) / (v.max()-v.min()) * (H-2*pad) + pad
su = su.astype(np.int32); sv = sv.astype(np.int32)

# 高斯核
K = 9; ax = np.arange(K) - K//2
ker = np.exp(-(ax[:,None]**2 + ax[None,:]**2) / (2*2.0**2)).astype(np.float32)

def splat(canvas, xs, ys, amps):
    h, w = canvas.shape
    for x, y, a in zip(xs, ys, amps):
        x0, y0 = x-K//2, y-K//2
        if x0 < 0 or y0 < 0 or x0+K > w or y0+K > h: continue
        canvas[y0:y0+K, x0:x0+K] += ker * a

# 逐時刻算亮度(向量化:純 Python 迴圈在 70 萬筆上跑不完)
st = np.array([t for t, _ in spikes], dtype=np.float32)
sidx = np.array([idx[b] for _, b in spikes], dtype=np.int32)

imgs = []
for t_ms in FRAMES_MS:
    m = (st <= t_ms) & (st > t_ms - TAU_MS*5)
    lv = np.zeros(len(pos), dtype=np.float32)
    np.add.at(lv, sidx[m], np.exp(-(t_ms - st[m]) / TAU_MS))
    canvas = np.zeros((H, W), dtype=np.float32)
    base = np.zeros((H, W), dtype=np.float32)
    splat(base, su, sv, np.full(len(pos), 0.020, np.float32))
    act = lv > 0.01
    splat(canvas, su[act], sv[act], np.clip(lv[act], 0, 6))
    imgs.append((t_ms, base, canvas, lv, act))
    print(f"  t={t_ms:4d}ms  活躍 {int(act.sum()):6,d} 顆  最亮 {lv.max():.1f}", flush=True)

def colorize(base, glow, palette, norm):
    # 用分位數而非固定常數正規化——固定常數在活動量變化大時必然過曝
    g = np.log1p(glow / max(norm, 1e-6) * 6.0) / np.log1p(6.0)
    g = np.clip(g, 0, 1) ** 1.25
    b = np.clip(base*1.5, 0, 1)
    img = np.zeros((H, W, 3), np.float32)
    for c in range(3):
        img[:,:,c] = b*palette['base'][c] + g*palette['hot'][c] + (g**3)*palette['core'][c]
    return Image.fromarray((np.clip(img,0,1)*255).astype(np.uint8))

PAL = {
  'gcamp': {'base': (0.10,0.16,0.15), 'hot': (0.15,0.95,0.45), 'core': (0.7,1.0,0.8)},
  'amber': {'base': (0.13,0.13,0.14), 'hot': (0.95,0.55,0.12), 'core': (1.0,0.92,0.7)},
}
# 全部幀共用同一個正規化值,才看得出「活動在增加」
NORM = float(np.percentile(np.concatenate([c[c > 0] for (_, _, c, _, _) in imgs]), 99.0))
print(f"共用正規化 (99 百分位) = {NORM:.2f}")

TW, TH = W//2, H//2
for name, pal in PAL.items():
    tiles = [colorize(b, c, pal, NORM) for (_, b, c, _, _) in imgs]
    sheet = Image.new('RGB', (TW*2, TH*2), (0, 0, 0))
    for k, im in enumerate(tiles):
        sheet.paste(im.resize((TW, TH)), ((k % 2)*TW, (k // 2)*TH))
    sheet.save(OUT/f"glow_{name}.png")
    print(f"→ {OUT}/glow_{name}.png  ({sheet.size[0]}x{sheet.size[1]})")
