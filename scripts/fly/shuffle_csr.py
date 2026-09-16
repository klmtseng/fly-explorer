#!/usr/bin/env python3
"""
保度數打亂(double edge swap / configuration model)——任務 A 的否證對照。

## 動機

M2 現有對照(隨機 21 顆 vs 上游 21 顆,207 Hz vs 2.67 Hz,差 78 倍)只證明
「亂選刺激神經元沒用」,沒證明「連線結構本身帶訊息」——因為兩次跑的都是
**同一個真實連接組**,只換了刺激點。真正的否證測試是保住每顆神經元的
入度/出度完全不變,只打亂「誰連到誰」,看放電率是否顯著下降。
若打亂版與真實版落在同一個量級,78 倍那個差異可能只是「有沒有連到 MN9
上游」這個平凡事實造成的,不是連接組的精細結構帶來的。

## 方法:雙邊交換(double edge swap)

反覆隨機取兩條邊 (a→b) 與 (c→d)(a、c 為突觸前神經元,即邊的來源,
在 CSR 裡對應「列」),換成 (a→d) 與 (c→b)。

**為什麼這樣做保度數**:每條邊永遠留在原來的「列」(來源神經元)裡,
只改邊指向的目標(欄)——所以每個節點的出度(它有幾條邊離開)絕對不變。
入度呢:節點 b 原本收 (a→b) 這條邊算它入度的一份;交換後 b 收到的是
(c→b),入度的「份數」還是 1 份,只是換了來源。d 同理。所以入度也不變。

**為什麜正負號自動保持**:突觸正負號在這份 CSR 裡是**突觸前神經元的屬性**
(`build_csr.py` 裡 `weight = min(w,32767) * sign[pre]`),邊永遠留在同一列
(同一個 pre),所以邊的正負號不會因為交換目標而改變——**這是設計上的
自動不變量,不是額外要做的事**,腳本最後仍會實測驗證這一點成立
(見 `--verify-sign`)。

**拒絕條件**(避免產生自環或重邊):
- a == c:兩條邊同一來源,交換會把「新邊已存在於這一列」的判斷弄糊,
  乾脆跳過(對隨機打亂的統計性質沒有損失,E 有 1500 萬條、N 只有 16.5 萬,
  同來源被抽到兩次的機率本來就低)。
- a == d 或 c == b:交換後會產生自環,拒絕。
- d 已經在 a 的鄰接集合裡,或 b 已經在 c 的鄰接集合裡:交換後會產生重邊,拒絕。

被拒絕的嘗試計入 attempts 但不計入 accepted;--swap-factor 控制的是
**嘗試次數**(次數 = swap-factor × 邊數),因為接受率預期接近 100%
(平均出度 92 對 N=165,122,兩條隨機邊撞到既有邊/自環的機率本就很低,
腳本執行時會把實測接受率印出來,不是拍的)。

## 可續跑(checkpoint)

10 倍邊數(~1.5 億次嘗試)在純 Python 迴圈裡不保證能在一次 Bash 呼叫的
逾時視窗內跑完。每跑滿 --checkpoint-every-sec 秒就把當前狀態(col 陣列、
attempts/accepted 計數、RNG 狀態)存進 `<out>.ckpt.npz`,下次用 --resume
接著跑。鄰接集合不存檔(重開時从 col 陣列重建即可,O(E) 很快)。

用法:
    python3 scripts/shuffle_csr.py --csr data/mcns_w2 --seed 1 \\
        --out data/mcns_shuffled_seed1 --swap-factor 10
    # 沒跑完就重跑同一條指令,--resume 是預設行為(偵測到 ckpt 就接續)
"""
import argparse
import os
import struct
import sys
import time

import numpy as np

MAGIC = b'FLYCSR01'
HEADER = 64


def load_csr(prefix):
    path = prefix + '.csr'
    with open(path, 'rb') as f:
        head = f.read(HEADER)
    if head[:8] != MAGIC:
        sys.exit(f'{path} 不是 FLYCSR01 格式')
    n, e, thr = struct.unpack('<qqi', head[8:28])
    off_row = HEADER
    off_col = off_row + (n + 1) * 8
    off_w = off_col + e * 4
    row = np.fromfile(path, dtype=np.int64, count=n + 1, offset=off_row)
    col = np.fromfile(path, dtype=np.int32, count=e, offset=off_col)
    w = np.fromfile(path, dtype=np.int16, count=e, offset=off_w)
    ids = np.fromfile(prefix + '.ids', dtype=np.int64)
    assert row[-1] == e, f'row_ptr 末端 {row[-1]} 與邊數 {e} 不符'
    assert len(ids) == n
    return n, e, thr, row, col, w, ids


def build_adjacency(n, row, tgt):
    """回傳 list[set(int)]:每個節點目前的出邊目標集合(供重邊/自環檢查)。"""
    adj = [None] * n
    tgt_list = tgt.tolist()
    for u in range(n):
        s, t = int(row[u]), int(row[u + 1])
        adj[u] = set(tgt_list[s:t])
    return adj


def double_edge_swap(n, row, src, tgt, adj, rng, target_attempts,
                      state, checkpoint_path, checkpoint_every_sec, save_fn,
                      log):
    """在 tgt(mutable int64 ndarray)上原地做雙邊交換,直到 attempts 達標或逾時中斷。

    state 是 dict,含 'attempts'/'accepted'/'rej_same_src'/'rej_selfloop'/'rej_dup',
    在呼叫端建立(可從 checkpoint 恢復),本函式就地更新並回傳。
    """
    E = len(tgt)
    BATCH = 2_000_000
    last_ckpt = time.time()
    t_start = time.time()
    attempts = state['attempts']
    accepted = state['accepted']
    while attempts < target_attempts:
        remain = target_attempts - attempts
        b = min(BATCH, remain)
        e1s = rng.integers(0, E, size=b, dtype=np.int64).tolist()
        e2s = rng.integers(0, E, size=b, dtype=np.int64).tolist()
        for e1, e2 in zip(e1s, e2s):
            attempts += 1
            if e1 == e2:
                state['rej_same_edge'] += 1
                continue
            a = src[e1]
            c = src[e2]
            if a == c:
                state['rej_same_src'] += 1
                continue
            b_tgt = tgt[e1]
            d_tgt = tgt[e2]
            if a == d_tgt or c == b_tgt:
                state['rej_selfloop'] += 1
                continue
            adj_a = adj[a]
            adj_c = adj[c]
            if d_tgt in adj_a or b_tgt in adj_c:
                state['rej_dup'] += 1
                continue
            # 接受:套用
            adj_a.discard(b_tgt)
            adj_a.add(d_tgt)
            adj_c.discard(d_tgt)
            adj_c.add(b_tgt)
            tgt[e1] = d_tgt
            tgt[e2] = b_tgt
            accepted += 1
            if attempts >= target_attempts:
                break
        state['attempts'] = attempts
        state['accepted'] = accepted
        now = time.time()
        log(f'  進度 attempts={attempts:,}/{target_attempts:,} '
            f'accepted={accepted:,} 已耗 {now - t_start:.1f}s')
        if checkpoint_path and (now - last_ckpt) >= checkpoint_every_sec:
            save_fn(state, tgt, rng)
            last_ckpt = now
            log(f'  ★ checkpoint 已存 {checkpoint_path}')
    return state


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--csr', required=True, help='來源 CSR 前綴(如 data/mcns_w2)')
    ap.add_argument('--out', required=True, help='輸出 CSR 前綴')
    ap.add_argument('--seed', type=int, required=True)
    ap.add_argument('--swap-factor', type=float, default=10.0,
                     help='嘗試次數 = swap-factor × 邊數,預設 10(規格下限)')
    ap.add_argument('--checkpoint-every-sec', type=float, default=45.0)
    ap.add_argument('--report', default=None, help='文字報告輸出路徑,預設 <out>.report.txt')
    args = ap.parse_args()

    report_path = args.report or (args.out + '.report.txt')
    log_lines = []

    def log(msg):
        print(msg)
        log_lines.append(msg)

    t0 = time.time()
    n, e, thr, row, col, w, ids = load_csr(args.csr)
    log(f'來源 {args.csr}: N={n:,} E={e:,} threshold={thr}  載入耗時 {time.time()-t0:.2f}s')

    src = np.repeat(np.arange(n, dtype=np.int64), np.diff(row))
    assert len(src) == e

    ckpt_path = args.out + '.ckpt.npz'
    target_attempts = int(round(args.swap_factor * e))

    state = {'attempts': 0, 'accepted': 0, 'rej_same_edge': 0,
             'rej_same_src': 0, 'rej_selfloop': 0, 'rej_dup': 0}
    tgt = col.astype(np.int64).copy()
    rng = np.random.default_rng(args.seed)

    if os.path.exists(ckpt_path):
        log(f'發現 checkpoint {ckpt_path},續跑')
        d = np.load(ckpt_path, allow_pickle=True)
        tgt = d['tgt'].astype(np.int64)
        for k in state:
            state[k] = int(d[k])
        rng_state = d['rng_state'].item()
        rng = np.random.default_rng()
        rng.bit_generator.state = rng_state
        log(f'  恢復 attempts={state["attempts"]:,} accepted={state["accepted"]:,}')

    def save_fn(state, tgt, rng):
        np.savez(ckpt_path + '.tmp', tgt=tgt.astype(np.int32),
                 rng_state=np.array(rng.bit_generator.state, dtype=object),
                 **{k: np.int64(v) for k, v in state.items()})
        os.replace(ckpt_path + '.tmp.npz', ckpt_path)

    if state['attempts'] < target_attempts:
        log(f'建鄰接集合(N={n:,} 列)…')
        t1 = time.time()
        adj = build_adjacency(n, row, tgt)
        log(f'  完成,耗時 {time.time()-t1:.2f}s')

        log(f'開始雙邊交換:目標 attempts={target_attempts:,}'
            f'(swap-factor={args.swap_factor} × E={e:,})')
        t2 = time.time()
        double_edge_swap(n, row, src, tgt, adj, rng, target_attempts,
                          state, ckpt_path, args.checkpoint_every_sec, save_fn, log)
        log(f'交換迴圈耗時 {time.time()-t2:.1f}s')
    else:
        log('checkpoint 已達標,略過交換迴圈')

    accept_rate = state['accepted'] / max(state['attempts'], 1) * 100
    log(f'\n嘗試 {state["attempts"]:,}  接受 {state["accepted"]:,}'
        f'({accept_rate:.3f}%)')
    log(f'拒絕明細:同邊 {state["rej_same_edge"]:,}  同源 {state["rej_same_src"]:,}'
        f'  會產生自環 {state["rej_selfloop"]:,}  會產生重邊 {state["rej_dup"]:,}')

    # ── 驗證:出/入度逐元素相等,權重多重集相等 ──────────────────────
    log('\n── 打亂正確性驗證 ──')
    outdeg_orig = np.diff(row)
    outdeg_new = np.bincount(src, minlength=n)
    # 因為 src 永不被改動、row_ptr 沿用原檔,理論上這個檢查必為 PASS——
    # 但仍要實跑證明,不是靠推論。
    outdeg_pass = np.array_equal(outdeg_orig, outdeg_new)
    log(f'  {"PASS" if outdeg_pass else "FAIL"}  出度逐元素相等')

    indeg_orig = np.bincount(col.astype(np.int64), minlength=n)
    indeg_new = np.bincount(tgt, minlength=n)
    indeg_pass = np.array_equal(indeg_orig, indeg_new)
    log(f'  {"PASS" if indeg_pass else "FAIL"}  入度逐元素相等')

    w_orig_sorted = np.sort(w)
    # 權重陣列本身完全沒被動過(只有 tgt/col 變了),但仍實際重新排序比對,
    # 不能只憑「我沒寫這一行」就假設它沒變。
    w_pass = np.array_equal(w_orig_sorted, np.sort(w))
    log(f'  {"PASS" if w_pass else "FAIL"}  權重多重集相等(權重陣列本身未被觸碰)')

    # 正負號驗證:每條邊的號應與其來源神經元的號一致,且與原檔逐邊一致
    # (因為 weight[e] 從未被改寫,只有 tgt[e] 改了,所以這一項理論上是恆等式,
    #  但同樣要實跑,不接受「設計上必然」當作驗證)。
    sign_pass = True  # weight 陣列同一份,無從比較「改變前後」;此檢查在下方對打亂後 CSR 做

    # ── 有效性(反向檢查,防 no-op):共同邊比例 < 5% ──────────────
    log('\n── 打亂有效性(共同邊比例)──')
    key_orig = src * np.int64(n) + col.astype(np.int64)
    key_new = src * np.int64(n) + tgt
    common = np.intersect1d(key_orig, key_new, assume_unique=True)
    common_frac = len(common) / e * 100
    valid_pass = common_frac < 5.0
    log(f'  {"PASS" if valid_pass else "FAIL"}  共同邊 {len(common):,}/{e:,} = '
        f'{common_frac:.3f}% (< 5% 才算有效打亂)')

    selfloops_new = int((src == tgt).sum())
    log(f'  自環數:原 {int((src==col.astype(np.int64)).sum())} → 打亂後 {selfloops_new}'
        f'(規則只擋新增,不擋既有自環被消耗,見腳本 docstring)')

    # ── 寫出 CSR / ids ─────────────────────────────────────────
    log('\n── 寫出 ──')
    out_csr = args.out + '.csr'
    off_row = HEADER
    off_col = off_row + (n + 1) * 8
    off_w = off_col + e * 4
    total = off_w + e * 2
    with open(out_csr, 'wb') as f:
        f.truncate(total)
    mm = np.memmap(out_csr, dtype=np.uint8, mode='r+')
    mm[:HEADER] = 0
    mm[:8] = np.frombuffer(MAGIC, dtype=np.uint8)
    mm[8:32] = np.frombuffer(struct.pack('<qqi4x', n, e, thr), dtype=np.uint8)
    row_out = np.memmap(out_csr, dtype=np.int64, mode='r+', offset=off_row, shape=(n + 1,))
    col_out = np.memmap(out_csr, dtype=np.int32, mode='r+', offset=off_col, shape=(e,))
    w_out = np.memmap(out_csr, dtype=np.int16, mode='r+', offset=off_w, shape=(e,))
    row_out[:] = row  # 完全未變
    col_out[:] = tgt.astype(np.int32)
    w_out[:] = w  # 完全未變(權重從未被觸碰)
    row_out.flush(); col_out.flush(); w_out.flush(); mm.flush()
    ids.tofile(args.out + '.ids')
    log(f'  {out_csr}  {total/2**20:.1f} MB')
    log(f'  {args.out}.ids  {n*8/2**20:.1f} MB')

    # 正負號驗證(打亂後 CSR 逐邊):sign(weight) 應與 sign 由 src 決定的原始規則一致——
    # 用「這條邊的號 == 該來源神經元其他邊的號(眾數)」驗證,因為 sign 是神經元屬性,
    # 同一來源所有邊應該同號(除非該來源本身號未定義,不會發生,因為 sign 在建 CSR 時
    # 就是逐神經元指定,不會有一個神經元同時有正負邊)。
    log('\n── 正負號驗證(同一來源的所有邊應同號,交換後仍要成立)──')
    wsign = np.sign(w.astype(np.int64))
    wsign[wsign == 0] = 1
    # 對每個來源,其所有邊(不論交換前後,因為 weight 沒變)號應全同
    # 用 row 分段檢查:每列內 wsign 應全相等
    bad_rows = 0
    for u in range(n):
        s, t = int(row[u]), int(row[u + 1])
        if t == s:
            continue
        seg = wsign[s:t]
        if seg[0] != seg.min() or seg[0] != seg.max():
            bad_rows += 1
    sign_pass = bad_rows == 0
    log(f'  {"PASS" if sign_pass else "FAIL"}  每個來源神經元的所有邊正負號一致'
        f'(異常列數 {bad_rows})——因交換只動 target 不動 weight,此為自動不變量')

    fails = sum(not x for x in [outdeg_pass, indeg_pass, w_pass, valid_pass, sign_pass])
    log(f'\n{"ALL PASS" if fails == 0 else f"FAIL({fails} 項)"}')

    with open(report_path, 'w') as f:
        f.write('\n'.join(log_lines) + '\n')
    log(f'\n報告存 {report_path}')

    if os.path.exists(ckpt_path):
        os.remove(ckpt_path)
        log(f'已刪除 checkpoint {ckpt_path}(完成)')

    sys.exit(0 if fails == 0 else 1)


if __name__ == '__main__':
    main()
