#!/usr/bin/env python3
"""往返驗證:解碼 escape.bin,確認與重新計算的亮度逐點相同。

為什麼需要:編碼錯誤(varint 少一個 byte、差值累加錯)會讓**錯的神經元亮起來**,
而那種錯用眼睛看不出來——畫面照樣很漂亮,只是意義全錯。
所以必須用機器逐點比對,不能靠目視。

exit 0 = 通過。
"""
import struct, sys, pathlib, csv, subprocess
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
import os
BIN = pathlib.Path(os.environ.get("VERIFY_BIN", ROOT/"public/data/scenarios/escape.bin"))
CSV = ROOT/"runs/build/escape.csv"
IDS = ROOT/"build-data/soma_ids.bin"
# 常數改由 build_scenario 匯入,兩支不再各自複製一份(審查 P3:會失步)
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location('build_scenario', ROOT/'scripts/build_scenario.py')
_bs = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_bs)
DT_MS, TAU_MS, MIN_BRIGHT = _bs.DT_MS, _bs.TAU_MS, _bs.MIN_BRIGHT

if "--self-test" in sys.argv:
    import tempfile, subprocess
    good = (ROOT/"public/data/scenarios/escape.bin").read_bytes()
    me = pathlib.Path(__file__).resolve()
    def run_variant(mut, label):
        b = bytearray(good); mut(b)
        with tempfile.NamedTemporaryFile("wb", suffix=".bin", delete=False) as fh:
            fh.write(b); tmp = fh.name
        r = subprocess.run([sys.executable, str(me)], env=dict(os.environ, VERIFY_BIN=tmp), capture_output=True, text=True)
        os.unlink(tmp); ok = r.returncode != 0
        print(f"  {'✓' if ok else '✗'} {label}: exit {r.returncode}(預期非 0)"); return ok
    r0 = subprocess.run([sys.executable, str(me)], capture_output=True, text=True)
    print(f"  {'✓' if r0.returncode == 0 else '✗'} 原始檔: exit {r0.returncode}(預期 0)")
    mid = len(good) // 2
    res = [r0.returncode == 0,
           run_variant(lambda b: b.__setitem__(mid, b[mid] ^ 0x3F), "負向:翻一個 byte"),
           run_variant(lambda b: b.__delitem__(mid), "負向:刪一個 byte"),
           run_variant(lambda b: b.__delitem__(slice(-1, None)), "負向:截掉最後一個 byte"),
           run_variant(lambda b: b.append(0), "負向:多補一個 byte")]
    print("SELF-TEST", "PASS" if all(res) else "FAIL"); sys.exit(0 if all(res) else 1)

raw = BIN.read_bytes()
assert raw[:8] == b"FLYSCN02", f"magic 不符: {raw[:8]!r}"
n_frames, dt100, n_pts = struct.unpack_from("<III", raw, 8)
print(f"header: {n_frames} 幀, dt={dt100/100}ms, {n_pts:,} 點")

# --- 解碼 ---
o = 20
decoded = []
for fi in range(n_frames):
    cnt, = struct.unpack_from("<I", raw, o); o += 4
    idxs = np.empty(cnt, dtype=np.int64); bri = np.empty(cnt, dtype=np.uint8)
    prev = 0
    for k in range(cnt):
        shift = 0; v = 0
        while True:
            if o >= len(raw):
                sys.exit(f"❌ 幀 {fi} 第 {k} 筆:varint 讀到檔尾就截斷了"
                         f"(已讀 {o} bytes / 全長 {len(raw)})——檔案不完整或格式不符")
            byte = raw[o]; o += 1
            v |= (byte & 0x7F) << shift
            if not (byte & 0x80): break
            shift += 7
        prev += v
        if o >= len(raw):
            sys.exit(f"❌ 幀 {fi} 第 {k} 筆:亮度 byte 讀到檔尾就截斷了(已讀 {o} / 全長 {len(raw)})")
        idxs[k] = prev; bri[k] = raw[o]; o += 1
    decoded.append((idxs, bri))
if o != len(raw):
    sys.exit(f"❌ 解碼後剩 {len(raw)-o} bytes 未消耗——格式不一致")
print(f"解碼完成,位元組全數消耗 ✓")

# --- 從原始 CSV 重算 ---
ids = np.fromfile(IDS, dtype=np.int64)
pos = {int(v): i for i, v in enumerate(ids)}
t_all, i_all = [], []
with open(CSV) as fh:
    rd = csv.reader(fh); next(rd)
    for row in rd:
        k = pos.get(int(row[2]))
        if k is not None: t_all.append(float(row[1])*1000.0); i_all.append(k)
t_all = np.array(t_all, dtype=np.float32); i_all = np.array(i_all, dtype=np.int64)

bad = 0
for fi in range(n_frames):
    t = (fi+1)*DT_MS
    m = (t_all <= t) & (t_all > t - TAU_MS*5)
    lv = np.zeros(len(ids), dtype=np.float32)
    if m.any(): np.add.at(lv, i_all[m], np.exp(-(t - t_all[m])/TAU_MS))
    b = np.clip(np.log1p(lv*2.0)/np.log1p(12.0)*255.0, 0, 255).astype(np.uint8)
    exp_i = np.nonzero(b >= MIN_BRIGHT)[0]
    got_i, got_b = decoded[fi]
    if not np.array_equal(exp_i, got_i):
        print(f"  ✗ 幀 {fi}: 索引不符(預期 {len(exp_i)} 個,得到 {len(got_i)} 個)"); bad += 1
    elif not np.array_equal(b[exp_i], got_b):
        d = np.nonzero(b[exp_i] != got_b)[0]
        print(f"  ✗ 幀 {fi}: {len(d)} 個亮度不符"); bad += 1

if bad:
    print(f"\n❌ {bad}/{n_frames} 幀不符"); sys.exit(1)
tot = sum(len(i) for i, _ in decoded)
print(f"✅ {n_frames} 幀、合計 {tot:,} 個亮點,索引與亮度**逐點完全相同**")
