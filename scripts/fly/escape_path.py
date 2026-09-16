#!/usr/bin/env python3
"""量「看見逼近 → 翅膀/腿肌肉」這條逃跑路徑的實際連線強度。

回答:這是不是一條直通線?中間隔幾跳?每一跳多粗?
全部由權重表實測,不引用文獻數字。
"""
import json, collections, pathlib
import numpy as np, pyarrow as pa, pyarrow.feather as f

import os
ROOT = pathlib.Path(os.environ.get("FLY_REPO", pathlib.Path(__file__).resolve().parents[2].parent / "fly"))   # 研究倉根目錄(含 data/ 原始資料);複製到公開倉後改由環境變數指定
W = ROOT/"data/connectome-weights-male-cns-v1.0-minconf-0.5.feather"
G = json.loads(pathlib.Path('/tmp/esc.json').read_text())
S = {k: np.sort(np.array(v, dtype=np.int64)) for k, v in G.items()}

# 要量的每一跳
HOPS = [('lc4','gf'), ('lplc2','gf'), ('gf','ttm'), ('gf','psi'),
        ('gf','dlm'), ('psi','dlm'), ('gf','dvm'), ('psi','dvm'),
        ('ttm','gf'), ('lc4','lplc2')]
acc = {h: [0, 0] for h in HOPS}

src = pa.memory_map(str(W), 'r'); rd = pa.ipc.open_file(src)
for b in range(rd.num_record_batches):
    rb = rd.get_batch(b)
    pre = rb.column('body_pre').to_numpy(zero_copy_only=False)
    post = rb.column('body_post').to_numpy(zero_copy_only=False)
    w = rb.column('weight').to_numpy(zero_copy_only=False)
    memo = {}
    for a, c in HOPS:
        if a not in memo: memo[a] = np.isin(pre, S[a])
        ma = memo[a]
        if not ma.any(): continue
        mc = np.isin(post[ma], S[c])
        if not mc.any(): continue
        acc[(a, c)][0] += int(mc.sum()); acc[(a, c)][1] += int(w[ma][mc].sum())
    if (b+1) % 400 == 0: print(f"  batch {b+1}/{rd.num_record_batches}", flush=True)

NAME = {'lc4':'LC4','lplc2':'LPLC2','gf':'巨纖維 DNp01','ttm':'TTMn 跳躍肌',
        'psi':'PSI','dlm':'DLMn 翅膀下壓','dvm':'DVMn 翅膀上舉'}
print(f"\n{'連線':34s} {'邊數':>6s} {'突觸':>8s}")
for h in HOPS:
    e, s = acc[h]
    mark = '  ←直連!' if (h[0] in ('gf',) and e) else ''
    print(f"{NAME[h[0]]+' → '+NAME[h[1]]:34s} {e:6d} {s:8,d}{mark}")
