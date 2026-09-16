#!/usr/bin/env python3
"""把一次模擬的放電序列壓成網頁可播的分幀資料。

亮度模型 = 鈣螢光物理:每次放電 +1,以 TAU 指數衰減。與 render_glow_test.py 同一套,
因為那就是真實活體成像看到的東西(見 content/cards.json 的 calcium-glow 卡)。

索引空間 = soma.bin 的順序(由 soma_ids.bin 對照)。**不在點雲裡的神經元會被丟掉,
並在輸出中報出丟了幾筆**——感覺神經元沒有細胞體座標,這是已知且必然的損失,
不可靜靜吞掉。

輸出格式(小端) FLYSCN02:
  header  magic"FLYSCN02" | uint32 n_frames | uint32 dt_ms×100 | uint32 n_points
  frames  每幀: uint32 count,接著 count × (varint Δindex, uint8 brightness)

索引存**差值**不存絕對值:同一幀內索引已排序,峰值 4,851 個活躍點散在 140,024 個位置裡,
平均差值約 29,varint 一個 byte 就夠。絕對值版每個索引固定 4 bytes,實測大 2.3 倍。
"""

def varint(v: int) -> bytes:
    """LEB128。前端解碼器在 src/scenario.ts,兩邊格式必須同步改。"""
    out = bytearray()
    while True:
        b = v & 0x7F
        v >>= 7
        out.append(b | (0x80 if v else 0))
        if not v: return bytes(out)
import subprocess, pathlib, csv, struct, json, sys, collections
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
FLY = ROOT.parent / "fly"
ENG, CSR = FLY/"engine/flysim", FLY/"data/mcns_w2"
ANN = FLY/"data/body-annotations-male-cns-v1.0-minconf-0.5.feather"
OUTDIR = ROOT/"public/data/scenarios"; OUTDIR.mkdir(parents=True, exist_ok=True)
WORK = ROOT/"runs/build"; WORK.mkdir(parents=True, exist_ok=True)

# 協定:全部取自 visual_pathway_test。⚠️ w_syn=0.179 **不是**「臨界點下方」——
# phase_sweep.json 顯示 0.179 配 25 顆隨機刺激會穩定引爆(六 seed 均值 ~60,000,CV 0.08)。
# 引爆與否取決於刺激集合,不是單一增益值。本情境的真正證據是:
# 這組 311 顆 LC4/LPLC2 脈衝 25ms 總放電僅 6,024,且同規模隨機對照的巨纖維為 0.00 Hz。
W_SYN, R_POI, T_RUN = 0.179, 150.0, 250.0
# 刺激只給前 25ms:逼近是一陣爆發不是持續驅動。跑滿全程的話被刺激的
# LC4/LPLC2 從頭亮到尾永遠不衰退,畫面上就看不出「訊號傳完後消退」。
T_STIM = 6.0
# 25ms → 3ms(2026-09-13):實測整條路徑 3-13ms 就傳完,25ms 的脈衝比傳遞還長,
# 訊號到肌肉時源頭還在被餵,畫面上全部同時亮。脈衝必須比傳遞短,才有「接力」。
DT_MS, TAU_MS = 1.0, 7.0
# dt=1ms:突觸延遲 1.8ms,幀距要比它小才看得到逐跳傳遞。
# tau=10ms:**這是顯示參數不是生理值**。真實 GCaMP 衰減是數百毫秒;
#   我們先前用 60ms,結果訊號只花 10-40ms 傳完,源頭還亮著終點就亮了
#   —— 畫面呈現的是「累積」而不是「流動」(使用者實機看出來的)。
#   縮到 10ms 讓每顆神經元閃一下就暗,才看得見波前在移動。
MIN_BRIGHT = 6                   # 0-255,低於此視為看不見,不寫進檔案

def build(name, stim_ids, seed=1):
    import pyarrow.feather as f
    ids = np.fromfile(ROOT/"build-data/soma_ids.bin", dtype=np.int64)
    pos = {int(v): i for i, v in enumerate(ids)}

    sf = WORK/f"{name}.stim"; sf.write_text("\n".join(map(str, stim_ids)))
    out = WORK/f"{name}.csv"
    # 膜電壓軌跡:同一次執行一起吐,才保證軌跡與出貨的放電資料來自同一個 seed/協定
    TRACE_IDS = [10001, 10010]          # 兩顆巨纖維 DNp01(左右各一)
    tf = WORK/f"{name}.trace_ids"; tf.write_text("\n".join(map(str, TRACE_IDS)))
    trace_csv = WORK/f"{name}.trace.csv"
    p = subprocess.run([str(ENG), "--csr", str(CSR), "--stim-file", str(sf),
                        "--r-poi", str(R_POI), "--trials", "1", "--t-run", str(T_RUN),
                        "--seed", str(seed), "--w-syn", str(W_SYN),
                        "--stim-ms", str(T_STIM), "--out", str(out),
                        "--trace-file", str(tf), "--trace-out", str(trace_csv)],
                       capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"引擎失敗 exit={p.returncode}: {p.stderr[:200]}")

    t_all, i_all, dropped = [], [], 0
    with open(out) as fh:
        rd = csv.reader(fh); next(rd)
        for row in rd:
            k = pos.get(int(row[2]))
            if k is None: dropped += 1; continue
            t_all.append(float(row[1]) * 1000.0); i_all.append(k)
    t_all = np.array(t_all, dtype=np.float32); i_all = np.array(i_all, dtype=np.int64)
    tot = len(t_all) + dropped
    print(f"  放電 {tot:,},可定位 {len(t_all):,},丟棄 {dropped:,} ({dropped/tot*100:.1f}%,無細胞體座標)")

    n_frames = int(T_RUN / DT_MS)
    n_pts = len(ids)
    blob = bytearray(b"FLYSCN02")
    blob += struct.pack("<III", n_frames, int(DT_MS*100), n_pts)
    peak_active = 0
    for fi in range(n_frames):
        t = (fi + 1) * DT_MS
        m = (t_all <= t) & (t_all > t - TAU_MS*5)
        lv = np.zeros(n_pts, dtype=np.float32)
        if m.any():
            np.add.at(lv, i_all[m], np.exp(-(t - t_all[m]) / TAU_MS))
        b = np.clip(np.log1p(lv * 2.0) / np.log1p(12.0) * 255.0, 0, 255).astype(np.uint8)
        sel = np.nonzero(b >= MIN_BRIGHT)[0]
        peak_active = max(peak_active, len(sel))
        blob += struct.pack("<I", len(sel))
        prev = 0
        chunk = bytearray()
        for idx in sel:                      # sel 由 np.nonzero 產生,已遞增
            chunk += varint(int(idx) - prev)
            chunk.append(int(b[idx]))
            prev = int(idx)
        blob += chunk
    # 軌跡 → JSON(2 顆 × 2,500 樣本,約 40KB)。標籤用側別而非 body id。
    import pyarrow.feather as _f
    _ann = _f.read_table(ANN, columns=['bodyId','somaSide']).to_pydict()
    _side = {int(b): (s or '?') for b, s in zip(_ann['bodyId'], _ann['somaSide'])}
    tr = {}
    with open(trace_csv) as fh:
        rd = csv.reader(fh); next(rd)
        for row in rd:
            tr.setdefault(int(row[2]), []).append(round(float(row[3]), 2))
    dt_trace = 0.1
    (OUTDIR/f"{name}_trace.json").write_text(json.dumps({
        "dt_ms": dt_trace, "rest_mv": -52.0, "threshold_mv": -45.0,
        "note": "巨纖維每 0.1ms 的膜電壓,引擎 --trace-out 直接輸出,與放電資料同一次執行。判閾值前記錄,故跨線瞬間會略高於 -45。",
        "neurons": [{"id": b, "label": f"巨纖維 {'右' if _side.get(b)=='R' else '左' if _side.get(b)=='L' else '?'}", "v": v}
                    for b, v in sorted(tr.items())]}, ensure_ascii=False), encoding="utf-8")
    print(f"  膜電壓軌跡 {len(tr)} 顆 × {len(next(iter(tr.values())))} 樣本 → {name}_trace.json")
    fp = OUTDIR/f"{name}.bin"; fp.write_bytes(blob)
    print(f"  {n_frames} 幀 × {DT_MS}ms,峰值活躍 {peak_active:,} 點 → {fp.name} {len(blob)/1e6:.2f} MB")
    return {"name": name, "frames": n_frames, "dt_ms": DT_MS, "tau_ms": TAU_MS,
            "peak_active": peak_active, "bytes": len(blob), "dropped_pct": round(dropped/tot*100, 1)}

if __name__ == "__main__":
    import pyarrow.feather as f
    d = f.read_table(ANN, columns=['bodyId','type','status']).to_pydict()
    tr = [i for i in range(len(d['bodyId'])) if (d['status'][i] or '') == 'Traced']
    lc = [int(d['bodyId'][i]) for i in tr if (d['type'][i] or '') in ("LC4", "LPLC2")]
    print(f"情境 escape:刺激 LC4+LPLC2 共 {len(lc)} 顆 (w_syn={W_SYN}, {R_POI}Hz, {T_RUN}ms)")
    meta = build("escape", lc)
    (OUTDIR/"index.json").write_text(json.dumps({"scenarios": [meta]}, ensure_ascii=False, indent=1), encoding="utf-8")
