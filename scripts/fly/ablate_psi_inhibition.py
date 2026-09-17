#!/usr/bin/env python3
"""消融測試:PSI 不放電,是被抑制壓住的嗎?(2026-09-18)

出貨情境裡 PSI(教科書說的巨纖維→翅膀中繼站)從頭到尾沒放電,而網站字幕寫「被抑制壓住」。
那是一句**因果宣稱**,而當時沒有任何實測撐著——只有「它最強的早期輸入是抑制性的」這個觀察。
2026-09-17 的科學宣稱稽核把它列為待驗,這支就是那個驗。

做法:複製一份 CSR,把**所有進 PSI 的抑制性邊**(權重 < 0)歸零,其餘一個位元都不動,
然後用與出貨情境**完全相同**的協定重跑,比較 PSI 有沒有放電。
反向檢查:改完之後 PSI 的抑制性入邊必須是 0,而其他神經元的權重陣列必須與原檔逐位元相同。

結果(2026-09-18,種子 1/2/3):
  基準        PSI 0/3 沒放電
  拿掉抑制    PSI 3/3 放電,首次 14.4 / 14.8 / 15.2 ms,各 2 次
  → 抑制確實是壓住 PSI 的原因,「被抑制壓住」這句成立。
  但同時:翅膀下壓肌的讀數**完全沒變**(種子 1 都是 15.7 ms、56 次),
  而且 PSI 就算放電也在 14 ms 之後,遠晚於巨纖維的 3.3 ms——
  所以即使解除抑制,這個模型裡的翅膀訊號仍然不是走教科書那條 GF→PSI→DLMn。
  更根本的限制在別處:連接組只記錄化學突觸,而文獻裡 GF→PSI 是電化學混合突觸,
  且電突觸才是果蠅巨纖維系統的主要型別(Augustin 2019, PMC6469880)。
  這個模型按建構就測不了那條路。

需要研究倉的引擎與 CSR(不公開),公開倉跑不動這支;結果寫在
docs/verification_log.md §PSI 抑制消融,卡片與字幕引用的是那一節。

用法:python3 scripts/fly/ablate_psi_inhibition.py [--seeds 1 2 3] [--keep]
"""
import argparse, collections, csv, json, pathlib, shutil, struct, subprocess, sys, tempfile

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
FLY = ROOT.parent / "fly"
ENG, CSR = FLY / "engine/flysim", FLY / "data/mcns_w2"
ANN = FLY / "data/body-annotations-male-cns-v1.0-minconf-0.5.feather"
STIM = ROOT / "runs/build/escape.stim"
W_SYN, R_POI, T_RUN, T_STIM = 0.179, 150.0, 250.0, 6.0     # 與出貨情境同一套協定
HEADER, MAGIC = 64, b"FLYCSR01"


def load_csr(prefix, mode="r"):
    head = open(f"{prefix}.csr", "rb").read(HEADER)
    if head[:8] != MAGIC:
        sys.exit(f"{prefix}.csr 不是 FLYCSR01 格式")
    n, e, _thr = struct.unpack("<qqi", head[8:28])
    off_col = HEADER + (n + 1) * 8
    col = np.memmap(f"{prefix}.csr", np.int32, "r", off_col, (e,))
    w = np.memmap(f"{prefix}.csr", np.int16, mode, off_col + e * 4, (e,))
    ids = np.fromfile(f"{prefix}.ids", dtype=np.int64)
    return n, e, col, w, ids


def types():
    import pyarrow.feather as pf
    d = pf.read_table(ANN, columns=["bodyId", "type"]).to_pydict()
    return {int(b): (t or "") for b, t in zip(d["bodyId"], d["type"])}


def group(t):
    return ("psi" if t == "PSI" else "gf" if t == "DNp01" else "jump" if t == "TTMn"
            else "wing" if t.startswith("DLMn") else None)


def readout(path, typ):
    first, cnt, tot = {}, collections.Counter(), 0
    with open(path) as fh:
        for r in csv.DictReader(fh):
            tot += 1
            g = group(typ.get(int(r["flywire_id"]), ""))
            if not g:
                continue
            t = float(r["t"]); cnt[g] += 1
            if g not in first or t < first[g]:
                first[g] = t
    scale = 1000.0 if first and max(first.values()) < 5 else 1.0
    return {"total": tot,
            **{g: {"first_ms": round(first[g] * scale, 2), "count": cnt[g]} if g in first else None
               for g in ("psi", "gf", "jump", "wing")}}


def run(prefix, seed, out):
    cmd = [str(ENG), "--csr", str(prefix), "--stim-file", str(STIM), "--r-poi", str(R_POI),
           "--trials", "1", "--t-run", str(T_RUN), "--seed", str(seed), "--w-syn", str(W_SYN),
           "--stim-ms", str(T_STIM), "--out", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"引擎失敗 seed={seed}:{r.stderr[-300:]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3])
    ap.add_argument("--keep", action="store_true", help="保留消融過的 CSR(93 MB)")
    a = ap.parse_args()
    for p in (ENG, pathlib.Path(f"{CSR}.csr"), ANN, STIM):
        if not p.exists():
            sys.exit(f"缺 {p}(這支需要研究倉,公開倉跑不動)")

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="psi_abl_"))
    abl = tmp / "psi_noinhib"
    shutil.copy(f"{CSR}.csr", f"{abl}.csr"); shutil.copy(f"{CSR}.ids", f"{abl}.ids")

    typ = types()
    psi_ids = sorted(b for b, t in typ.items() if t == "PSI")
    n, e, col, w, ids = load_csr(str(abl), "r+")
    dense = [int(np.searchsorted(ids, p)) for p in psi_ids]
    if any(ids[d] != p for d, p in zip(dense, psi_ids)):
        sys.exit("PSI 的 body id 不在 CSR 的 ids 裡")
    into_psi = np.isin(np.asarray(col), dense)
    mask = into_psi & (np.asarray(w) < 0)
    n_cut, w_cut = int(mask.sum()), int(np.asarray(w)[mask].sum())
    w[mask] = 0; w.flush()

    # 反向檢查:PSI 的抑制性入邊必須歸零,其他神經元必須逐位元不變
    _, _, _, w_new, _ = load_csr(str(abl))
    _, _, _, w_old, _ = load_csr(str(CSR))
    left = int((into_psi & (np.asarray(w_new) < 0)).sum())
    other = ~into_psi
    untouched = np.array_equal(np.asarray(w_old)[other], np.asarray(w_new)[other])
    print(f"PSI = {psi_ids}(dense {dense});切掉 {n_cut} 條抑制性入邊,權重和 {w_cut}")
    print(f"反向檢查:PSI 殘留抑制性入邊 {left}(須 0);其他神經元權重未變 {untouched}(須 True)")
    if left or not untouched:
        sys.exit("反向檢查沒過,消融做壞了")

    rows = []
    for seed in a.seeds:
        base = tmp / f"base_s{seed}.csv"; cut = tmp / f"cut_s{seed}.csv"
        run(str(CSR), seed, base); run(str(abl), seed, cut)
        rows.append({"seed": seed, "baseline": readout(base, typ), "no_psi_inhibition": readout(cut, typ)})
        b, c = rows[-1]["baseline"], rows[-1]["no_psi_inhibition"]
        f = lambda d, g: f"{d[g]['first_ms']}ms×{d[g]['count']}" if d[g] else "沒放電"
        print(f"  seed {seed}: PSI {f(b,'psi'):>12s} → {f(c,'psi'):<12s} | "
              f"翅膀 {f(b,'wing')} → {f(c,'wing')} | 巨纖維 {f(b,'gf')} → {f(c,'gf')}")

    fired = sum(1 for r in rows if r["no_psi_inhibition"]["psi"])
    base_fired = sum(1 for r in rows if r["baseline"]["psi"])
    out = ROOT / "runs/build/psi_ablation.json"
    out.write_text(json.dumps({
        "protocol": {"w_syn": W_SYN, "r_poi_hz": R_POI, "t_run_ms": T_RUN, "stim_ms": T_STIM,
                     "stim": "runs/build/escape.stim", "seeds": a.seeds},
        "ablation": {"psi_body_ids": psi_ids, "inhibitory_edges_zeroed": n_cut, "weight_sum": w_cut},
        "result": {"psi_fired_baseline": f"{base_fired}/{len(rows)}",
                   "psi_fired_without_inhibition": f"{fired}/{len(rows)}"},
        "runs": rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"基準 PSI 放電 {base_fired}/{len(rows)};拿掉抑制後 {fired}/{len(rows)} → {out.relative_to(ROOT)}")
    if not a.keep:
        shutil.rmtree(tmp, ignore_errors=True)
    else:
        print(f"消融後的 CSR 保留在 {abl}")


if __name__ == "__main__":
    main()
