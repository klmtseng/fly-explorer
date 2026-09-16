#!/usr/bin/env python3
"""追蹤:某族群首次放電時,是哪些上游在它之前已經放電?

動機:對抗審查抓到 DLMn(翅膀下壓肌)12.7ms 就放電,早於教科書中繼站 PSI(28.5ms),
而 GF→DLMn 直連為 0。畫連線之前必須知道第一波實際走哪條路,否則畫出來的線跟資料矛盾。

方法:對目標族群,從 CSR 取所有上游(含權重),對照 escape.csv 看哪些上游在
目標首次放電時刻之前已經放電。按 權重×放電數 排序 = 最可能的驅動者。

內建對照:TTMn 應顯示 DNp01(巨纖維)為主驅動者(直連 90 突觸,實測 13.7ms)。
若 TTMn 跑不出 DNp01,方法本身有問題,DLMn 的結果也不可信。
"""
import csv, pathlib, collections, sys
import numpy as np
import pyarrow.feather as f

ROOT = pathlib.Path(__file__).resolve().parent.parent
FLY = ROOT.parent / "fly"
CSR = FLY / "data/mcns_w2"
ANN = FLY / "data/body-annotations-male-cns-v1.0-minconf-0.5.feather"
SPK = ROOT / "runs/build/escape.csv"

H = 64
b = np.memmap(str(CSR) + ".csr", dtype=np.uint8, mode="r")
n = int(np.frombuffer(b[8:16].tobytes(), dtype=np.int64)[0])
e = int(np.frombuffer(b[16:24].tobytes(), dtype=np.int64)[0])
o = H
row = np.frombuffer(b[o:o+(n+1)*8].tobytes(), dtype=np.int64); o += (n+1)*8
col = np.frombuffer(b[o:o+e*4].tobytes(), dtype=np.int32);     o += e*4
w   = np.frombuffer(b[o:o+e*2].tobytes(), dtype=np.int16)
ids = np.fromfile(str(CSR) + ".ids", dtype=np.int64)
pos = {int(v): i for i, v in enumerate(ids)}

d = f.read_table(ANN, columns=['bodyId','type','status']).to_pydict()
typ = {int(d['bodyId'][i]): (d['type'][i] or '?') for i in range(len(d['bodyId']))}

# 反向索引:誰連到 target(CSR 是出邊,要掃全表一次)
src_of = np.repeat(np.arange(n, dtype=np.int64), np.diff(row))

first_spk, spikes = {}, collections.defaultdict(list)
with open(SPK) as fh:
    rd = csv.reader(fh); next(rd)
    for r in rd:
        bid = int(r[2]); t = float(r[1]) * 1000.0
        spikes[bid].append(t)
        if bid not in first_spk or t < first_spk[bid]: first_spk[bid] = t

def trace(label, pred, top=12):
    targets = [bid for bid, ty in typ.items() if pred(ty) and bid in pos]
    onset = min(first_spk[b] for b in targets if b in first_spk)
    print(f"\n=== {label}:{len(targets)} 顆,首次放電 {onset:.1f} ms ===")
    agg = collections.defaultdict(lambda: [0, 0, 0])   # 上游 → [權重和, onset 前放電數, 邊數]
    tset = {pos[b] for b in targets}
    mask = np.isin(col, list(tset))
    for src_i, dst_i, wt in zip(src_of[mask], col[mask], w[mask]):
        sb = int(ids[src_i])
        n_before = sum(1 for t in spikes.get(sb, []) if t < onset)
        a = agg[sb]; a[0] += int(wt); a[1] += n_before if a[2] == 0 else 0; a[2] += 1
    rows = [(sb, v[0], v[1], v[2]) for sb, v in agg.items() if v[1] > 0]
    rows.sort(key=lambda x: -abs(x[1]) * x[2])
    print(f"  上游共 {len(agg):,} 顆,其中在 {onset:.1f} ms 前已放電的 {len(rows):,} 顆。前 {top}(按 |權重|×放電數):")
    print(f"  {'type':16s} {'bodyId':>11s} {'權重和':>7s} {'onset前放電':>10s} {'首次放電':>8s}")
    for sb, wt, nb, ne in rows[:top]:
        print(f"  {typ.get(sb,'?'):16s} {sb:11d} {wt:+7d} {nb:10d} {first_spk[sb]:8.1f}")
    return rows

if len(sys.argv) > 1:
    # 用法:trace_drivers.py TYPE [TYPE ...]   (TYPE 可用 前綴* 表示 startswith)
    for arg in sys.argv[1:]:
        if arg.endswith("*"): trace(arg, (lambda p: lambda t: t.startswith(p))(arg[:-1]), top=8)
        else:                 trace(arg, (lambda a: lambda t: t == a)(arg), top=8)
    sys.exit(0)

ttm = trace("對照:跳躍肌 TTMn", lambda t: t == "TTMn")
top_ttm = {typ.get(r[0]) for r in ttm[:3]}
print("\n  對照判定:", "✅ DNp01 在前三名,方法可信" if "DNp01" in top_ttm else "❌ DNp01 不在前三,方法有問題")

dlm = trace("受測:翅膀下壓肌 DLMn", lambda t: t.startswith("DLMn"))
