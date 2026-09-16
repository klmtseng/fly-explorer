/* 巨纖維膜電壓計。
 *
 * 資料:public/data/scenarios/escape_trace.json,引擎每 0.1ms 的真實膜電壓(與放電資料同一次執行)。
 * 目的:讓看的人看到「閾值以下那段看不見的爬升」——畫面上的點只在放電時亮,
 * 但放電前電壓已經在爬;跨過 −45 mV 那一刻才是「突然」的來源。
 * 這是資料層(①/②),綠色。不做任何平滑或美化,原樣畫。
 */
export interface TraceData {
  dt_ms: number; rest_mv: number; threshold_mv: number;
  neurons: { id: number; label: string; v: number[] }[];
}
export interface Gauge { el: HTMLCanvasElement; draw(tMs: number): void; data: TraceData; setLang(l: 'zh' | 'en'): void; }

export async function loadGauge(url: string, host: HTMLElement): Promise<Gauge> {
  const data = await (await fetch(url)).json() as TraceData;
  const el = document.createElement('canvas');
  el.className = 'gauge';
  host.appendChild(el);
  const ctx = el.getContext('2d')!;
  let lang: 'zh' | 'en' = 'zh';
  const LB = { zh: ['靜息 −52 mV', '閾值 −45 mV', '巨纖維膜電壓'], en: ['rest −52 mV', 'threshold −45 mV', 'giant-fiber membrane voltage'] };
  const dpr = Math.min(window.devicePixelRatio || 1, 2);

  function draw(tMs: number) {
    const W = el.clientWidth, H = el.clientHeight;
    if (el.width !== W * dpr || el.height !== H * dpr) { el.width = W * dpr; el.height = H * dpr; }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, W, H);
    // 時間窗:前 14ms 放大看接力;之後看全程
    const zoom = tMs <= 14;
    const t0 = 0, t1 = zoom ? 14 : data.neurons[0].v.length * data.dt_ms;
    const vLo = data.rest_mv - 1.0, vHi = data.threshold_mv + 1.5;
    const padL = 8, padR = 8, padT = 22, padB = 18;   // padT 留一條標題帶,不跟閾值標籤擠
    const x = (t: number) => padL + (t - t0) / (t1 - t0) * (W - padL - padR);
    const y = (v: number) => padT + (vHi - v) / (vHi - vLo) * (H - padT - padB);

    ctx.font = '10px "IBM Plex Mono", monospace';
    // 靜息 / 閾值 參考線
    const GUIDES: [number, string, string][] = [[data.rest_mv, LB[lang][0], '#5c6b66'], [data.threshold_mv, LB[lang][1], '#C8A24A']];
    for (const [v, , col] of GUIDES) {
      ctx.strokeStyle = col; ctx.setLineDash([3, 3]); ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(padL, y(v)); ctx.lineTo(W - padR, y(v)); ctx.stroke();
      ctx.setLineDash([]);
    }
    // 軌跡(到目前時刻為止)
    const n = Math.max(0, Math.min(data.neurons[0].v.length, Math.floor(tMs / data.dt_ms) + 1));
    data.neurons.forEach((nr, k) => {
      ctx.strokeStyle = k === 0 ? '#8fe3a8' : '#4fc0cc'; ctx.lineWidth = 1.4; ctx.beginPath();
      let started = false;
      for (let i = 0; i < n; i++) {
        const t = i * data.dt_ms; if (t > t1) break;
        const px = x(t), py = y(Math.min(nr.v[i], vHi));
        if (!started) { ctx.moveTo(px, py); started = true; } else ctx.lineTo(px, py);
      }
      ctx.stroke();
      // 跨線點:v>閾值 的樣本畫成小圓 = 放電那一刻
      ctx.fillStyle = k === 0 ? '#8fe3a8' : '#4fc0cc';
      for (let i = 0; i < n; i++) {
        const t = i * data.dt_ms; if (t > t1) break;
        if (nr.v[i] > data.threshold_mv) { ctx.beginPath(); ctx.arc(x(t), y(vHi) + 2, 2.6, 0, Math.PI * 2); ctx.fill(); }
      }
    });
    // 游標
    if (tMs >= t0 && tMs <= t1) {
      ctx.strokeStyle = 'rgba(223,230,224,.55)'; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(x(tMs), padT - 4); ctx.lineTo(x(tMs), H - padB); ctx.stroke();
    }
    // 文字**最後畫**並墊深色底:實機回報 0-250ms 視窗裡開頭的放電尖峰正好落在左緣,把左邊的標籤蓋掉。
    // 電壓標籤靠右、時間範圍靠右下、標題在獨立的頂帶,三者互不相碰。
    const label = (txt: string, x: number, yy: number, col: string, align: CanvasTextAlign) => {
      ctx.textAlign = align; const w = ctx.measureText(txt).width;
      const x0 = align === 'right' ? x - w - 3 : x - 3;
      ctx.fillStyle = 'rgba(8,12,10,.82)'; ctx.fillRect(x0, yy - 9, w + 6, 12);
      ctx.fillStyle = col; ctx.fillText(txt, x, yy);
    };
    for (const [v, lab, col] of GUIDES) label(lab, W - padR - 2, y(v) - 3, col, 'right');
    label(zoom ? '0 – 14 ms' : `0 – ${t1.toFixed(0)} ms`, W - padR - 2, H - 5, '#96a29a', 'right');
    label(LB[lang][2], padL + 3, padT - 8, '#96a29a', 'left');
  }
  return { el, draw, data, setLang(l) { lang = l; } };
}
