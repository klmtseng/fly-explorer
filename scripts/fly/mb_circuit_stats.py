#!/usr/bin/env python3
"""蘑菇體(MB)學習迴路在 MaleCNS 裡的規模盤點。

回答「這個模型能不能學習」的可執行版本:果蠅的聯想學習發生在 KC->MBON 突觸,
由 DAN(PAM 獎賞 / PPL 懲罰)按區室閘控。本腳本數出這些族群與其間的邊,
得到「若要加可塑性,可訓練參數有幾個」的確切數字。

批次讀 feather(152M 列全載會 OOM,見 count_edges.py 註解)。
"""
import sys, re, collections
import pyarrow as pa
import pyarrow.feather as f
import numpy as np

import os
DATA = os.environ.get("MALECNS_DATA", "data")   # MaleCNS 原始 feather 所在目錄(研究倉 data/;公開倉不含)
ANN = f"{DATA}/body-annotations-male-cns-v1.0-minconf-0.5.feather"
W   = f"{DATA}/connectome-weights-male-cns-v1.0-minconf-0.5.feather"

ann = f.read_table(ANN, columns=['bodyId', 'type', 'status']).to_pydict()
bid = np.array(ann['bodyId'], dtype=np.int64)
ty  = [x or '' for x in ann['type']]
st  = [x or '' for x in ann['status']]

GROUPS = {
    'KC':   re.compile(r'^KC'),
    'MBON': re.compile(r'^MBON'),
    'PAM':  re.compile(r'^PAM'),
    # ⚠️ 只取 PPL1 群:PPL2(PPL201-204,8顆)不投射到蘑菇體,與學習迴路無關。
    # 2026-09-12 修:原本寫 ^PPL 把兩群加在一起報成 24,文獻對照才抓到。
    'PPL1': re.compile(r'^PPL1'),
    'PPL2': re.compile(r'^PPL2'),
    'APL':  re.compile(r'^APL'),
}
sets = {}
for name, rx in GROUPS.items():
    sel = np.array([i for i in range(len(ty)) if st[i] == 'Traced' and rx.match(ty[i])], dtype=np.int64)
    sets[name] = np.sort(bid[sel])
    print(f"{name:5s} {len(sel):6d} 顆", flush=True)

# 逐批掃邊表,只留兩端都在 MB 相關族群裡的邊
pairs = [('KC','MBON'), ('PAM','KC'), ('PAM','MBON'),
         ('PPL1','KC'), ('PPL1','MBON'), ('PPL2','KC'), ('PPL2','MBON'),
         ('APL','KC'), ('KC','APL'), ('MBON','PAM'), ('MBON','PPL1')]
acc = {p: [0, 0] for p in pairs}   # [邊數, 權重和]

src = pa.memory_map(W, 'r')
reader = pa.ipc.open_file(src)
nb = reader.num_record_batches
print(f"\n掃 {nb} 個 batch ...", flush=True)
for b in range(nb):
    rb = reader.get_batch(b)
    pre = rb.column('body_pre').to_numpy(zero_copy_only=False)
    post = rb.column('body_post').to_numpy(zero_copy_only=False)
    w = rb.column('weight').to_numpy(zero_copy_only=False)
    memo = {}
    for a, c in pairs:
        if a not in memo:
            memo[a] = np.isin(pre, sets[a], assume_unique=False)
        ma = memo[a]
        if not ma.any():
            continue
        mc = np.isin(post[ma], sets[c], assume_unique=False)
        if not mc.any():
            continue
        acc[(a, c)][0] += int(mc.sum())
        acc[(a, c)][1] += int(w[ma][mc].sum())
    if (b + 1) % 5 == 0 or b == nb - 1:
        print(f"  batch {b+1}/{nb}", flush=True)

print("\n=== MB 迴路連線 ===")
print(f"{'連線':16s} {'邊數':>10s} {'突觸(PSD)':>12s} {'平均權重':>9s}")
for p in pairs:
    e, s = acc[p]
    avg = s / e if e else 0
    print(f"{p[0]+' -> '+p[1]:16s} {e:10,d} {s:12,d} {avg:9.1f}")
