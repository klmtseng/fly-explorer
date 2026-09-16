/* 情境播放資料的解碼器。
 *
 * 格式 FLYSCN02,由 scripts/build_scenario.py 產生,**兩邊必須同步改**:
 *   magic "FLYSCN02" | uint32 n_frames | uint32 dt_ms×100 | uint32 n_points
 *   每幀: uint32 count,接著 count × (varint Δindex, uint8 brightness)
 *
 * 索引存差值:同幀內已排序,平均差值約 29,varint 一個 byte 就夠。
 * Python 端有往返驗證(scripts/verify_scenario.py),逐點比對且含負向控制組。
 */

export interface Scenario {
  nFrames: number;
  dtMs: number;
  nPoints: number;
  /** 各幀在 idx/bri 裡的起訖 */
  offsets: Uint32Array;   // 長度 nFrames+1
  idx: Uint32Array;
  bri: Uint8Array;
  durationMs: number;
}

export async function loadScenario(url: string): Promise<Scenario> {
  // 與 soma 同樣的退路:Artifact 平台只服務標準 web 媒體型別,.bin 發不上去
  let buf: ArrayBuffer;
  const r = await fetch(url);
  if (r.ok) buf = await r.arrayBuffer();
  else {
    const rj = await fetch(url.replace(/\.bin$/, '.json'));
    if (!rj.ok) throw new Error(`讀不到 ${url} 也讀不到其 .json 版`);
    const { b64 } = await rj.json() as { b64: string };
    const bin = atob(b64);
    const a = new Uint8Array(bin.length);
    for (let i = 0; i < bin.length; i++) a[i] = bin.charCodeAt(i);
    buf = a.buffer;
  }
  const u8 = new Uint8Array(buf);
  const dv = new DataView(buf);

  const magic = String.fromCharCode(...u8.subarray(0, 8));
  if (magic !== 'FLYSCN02') throw new Error(`情境檔格式不符:${magic}`);

  const nFrames = dv.getUint32(8, true);
  const dtMs = dv.getUint32(12, true) / 100;
  const nPoints = dv.getUint32(16, true);

  // 先掃一遍數總量,才能一次配置正確大小的 typed array
  let o = 20, total = 0;
  const counts = new Uint32Array(nFrames);
  {
    let p = o;
    for (let f = 0; f < nFrames; f++) {
      const c = dv.getUint32(p, true); p += 4;
      counts[f] = c; total += c;
      for (let k = 0; k < c; k++) {
        while (u8[p] & 0x80) p++;       // 跳過 varint 的接續位元組
        p++;                             // varint 末位元組
        p++;                             // brightness
      }
    }
    if (p !== u8.length) throw new Error(`情境檔長度不符:掃到 ${p} / 全長 ${u8.length}`);
  }

  const offsets = new Uint32Array(nFrames + 1);
  const idx = new Uint32Array(total);
  const bri = new Uint8Array(total);

  let w = 0;
  for (let f = 0; f < nFrames; f++) {
    offsets[f] = w;
    const c = dv.getUint32(o, true); o += 4;
    let prev = 0;
    for (let k = 0; k < c; k++) {
      let shift = 0, v = 0, byte = 0;
      do { byte = u8[o++]; v |= (byte & 0x7f) << shift; shift += 7; } while (byte & 0x80);
      prev += v;
      idx[w] = prev;
      bri[w] = u8[o++];
      w++;
    }
  }
  offsets[nFrames] = w;

  return { nFrames, dtMs, nPoints, offsets, idx, bri, durationMs: nFrames * dtMs };
}

/** 把第 f 幀寫進亮度陣列(先清零)。回傳實際畫出來的點數。
 *
 * `stride` 是點雲的抽樣間隔(手機模式 >1)。情境檔存的是**原始**索引,
 * 抽樣後必須換算,否則會亮到完全不相干的神經元——而那種錯用眼睛看不出來。
 * 換算不到的點(原始索引不是 stride 的倍數)會被丟掉,回傳值會少於該幀總數。 */
export function applyFrame(s: Scenario, f: number, out: Float32Array, stride = 1,
                           watch?: Map<number, number>, watchOut?: Float32Array): number {
  out.fill(0);
  if (watchOut) watchOut.fill(0);   // watch: 原始索引 → 節點序號;不受 stride 影響,永遠全解析度
  if (f < 0 || f >= s.nFrames) return 0;
  const a = s.offsets[f], b = s.offsets[f + 1];
  if (watch && watchOut) {
    for (let k = a; k < b; k++) { const j = watch.get(s.idx[k]); if (j !== undefined) watchOut[j] = s.bri[k] / 255; }
  }
  if (stride === 1) {
    for (let k = a; k < b; k++) out[s.idx[k]] = s.bri[k] / 255;
    return b - a;
  }
  let drawn = 0;
  for (let k = a; k < b; k++) {
    const o = s.idx[k];
    if (o % stride) continue;
    const j = o / stride;
    if (j < out.length) { out[j] = s.bri[k] / 255; drawn++; }
  }
  return drawn;
}
