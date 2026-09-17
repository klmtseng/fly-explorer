/* 實驗台:同一顆腦、同一套協定,只換「刺激哪些神經元」。
 *
 * 每一格都是**真的各跑過 N 次**的結果(N 由 protocol.seeds 決定,目前 20)(scripts/build_playground.py,協定與出貨情境完全相同),
 * 不是瀏覽器裡的即時模擬。為什麼不做即時:出貨的連線檔只有興奮性邊,拿它即時算會一點就爆,
 * 而且會推翻本站自己的發現(PSI 不放電的原因正是它最強的早期輸入是抑制性的)。
 *
 * 顯示規範:
 *   - 一律給中位數 + 五次的範圍,不給單一數字。單次跑不可採信是本專案付過學費的教訓。
 *   - 「五次裡幾次有放電」是主角:0/5 要一眼看得出來,那才是實驗的結果。
 *   - 有些條件另外有可播的舞台資料;沒有的就明說「這一格只有數字」。
 *   - 播非基準條件時,主程式必須換掉字幕(基準字幕在講逃跑時間軸,套到別的條件上就是說謊)。
 */
import pgJson from '../public/data/playground.json';

type Stat = { median: number; min: number; max: number };
type GroupSummary = { fired_in: number; of: number; first_ms: Stat | null; count: Stat };
type Cond = {
  key: string; zh: string; en: string; n_stim: number; resampled: boolean; pool?: string;
  summary: Record<string, GroupSummary | Stat> & { total_spikes: Stat; stim_spikes: Stat; downstream_spikes: Stat };
  runs: { total_spikes: number; stim_spikes: number; downstream_spikes: number; first_ms: Record<string, number> }[];
};
const PG = pgJson as unknown as {
  protocol: { w_syn_mv: number; r_poi_hz: number; t_run_ms: number; stim_ms: number; seeds: number };
  conditions: Cond[];
};
/** PSI 在所有條件所有跑次裡放電幾次:單格 0/20 撐不起「不會放電」,跨條件的 0/180 才撐得起 */
const PSI_TOTAL = PG.conditions.reduce((a, c) => a + c.runs.length, 0);
const PSI_SILENT = PG.conditions.reduce((a, c) => a + c.runs.filter(r => !('psi' in r.first_ms)).length, 0);

/** 哪些條件另外匯出了可播的舞台資料(scripts/build_scenario.py) */
const PLAYABLE: Record<string, { bin: string; trace: string }> = {
  both:     { bin: 'data/scenarios/escape.bin',   trace: 'data/scenarios/escape_trace.json' },
  lc4:      { bin: 'data/scenarios/lc4.bin',      trace: 'data/scenarios/lc4_trace.json' },
  dose_39:  { bin: 'data/scenarios/dose39.bin',   trace: 'data/scenarios/dose39_trace.json' },
  rand_311: { bin: 'data/scenarios/rand311.bin',  trace: 'data/scenarios/rand311_trace.json' },
};

const GROUP_LABEL: Record<string, { zh: string; en: string }> = {
  detect: { zh: '偵測器', en: 'detectors' },
  gf:     { zh: '巨纖維', en: 'giant fiber' },
  jump:   { zh: '跳躍肌的神經', en: 'jump muscle nerve' },
  wing:   { zh: '翅膀肌的神經', en: 'wing muscle nerve' },
  psi:    { zh: 'PSI 中繼', en: 'PSI relay' },
};

const UI = {
  zh: {
    title: '實驗台', close: '關閉',
    lead: (n: number) => `同一顆腦,同一套協定,只換「刺激哪些神經元」。每一格都真的各跑 ${n} 次,下面給的是中位數與 ${n} 次的範圍。`,
    real: '真實的偵測器', less: '減少偵測器', ctrl: '對照組',
    stim: (n: number) => `刺激 ${n} 顆神經元`,
    fired: (k: number, n: number) => `${n} 次裡 ${k} 次放電`,
    never: (n: number) => `${n} 次都沒放電`,
    total: '下游放電數', first: '首次放電',
    totalNote: (t: string, o: string) => `(全部 ${t},其中被直接刺激的那些自己放了 ${o})`,
    bimodal: (k: number, n: number) => `⚠ ${n} 次裡有 ${k} 次結果完全不同(整顆腦被點燃),中位數看不出這件事`,
    stimRow: '(這一格就是被刺激的對象,它會放電是必然的)',
    onlyOnce: (k: number) => `只有 ${k} 次放電,這個數字不是統計量`,
    psiAll: (s: number, n: number) => `PSI 在九個條件、${n} 次執行裡,${s} 次都沒放電`,
    backBase: '回到標準重播',
    cantRerun: '產生這些數字的引擎與權重檔在不公開的研究倉。公開的是每一次執行的原始輸出,你可以自己重算這裡的每個中位數與範圍,但沒辦法重跑模擬。',
    varFixed: '刺激集合固定,各次之間只有模擬本身的隨機性在變',
    varResample: '每一次都重新抽一組神經元,所以範圍同時包含模擬的隨機性與「抽到哪幾顆」',
    play: '在舞台上播這一次', nodata: '這一格只有數字,沒有匯出舞台資料',
    proto: (p: typeof PG.protocol) => `協定與重播完全相同:w_syn ${p.w_syn_mv} mV、刺激 ${p.r_poi_hz} Hz 給前 ${p.stim_ms} ms、跑 ${p.t_run_ms} ms、每格 ${p.seeds} 個亂數種子。每一次執行的原始數字在 /data/playground.json。`,
    note: '這不是瀏覽器裡的即時模擬。每一格都是先用完整連接組跑出來的結果。',
  },
  en: {
    title: 'Lab', close: 'Close',
    lead: (n: number) => `Same brain, same protocol. The only thing that changes is which neurons get stimulated. Every cell below was actually run ${n} times, and the numbers are the median and the range across those runs.`,
    real: 'The real detectors', less: 'Fewer detectors', ctrl: 'Controls',
    stim: (n: number) => `${n} neurons stimulated`,
    fired: (k: number, n: number) => `fired in ${k} of ${n} runs`,
    never: (n: number) => `never fired in ${n} runs`,
    total: 'downstream spikes', first: 'first spike',
    totalNote: (t: string, o: string) => `(${t} in total, of which the directly stimulated cells fired ${o} themselves)`,
    bimodal: (k: number, n: number) => `⚠ ${k} of the ${n} runs came out completely different (the whole brain ignited); the median hides that`,
    stimRow: '(this row is the set being stimulated, so of course it fires)',
    onlyOnce: (k: number) => `fired in only ${k} run, so this is not a statistic`,
    psiAll: (s: number, n: number) => `PSI stayed silent in ${s} of ${n} runs, across all nine conditions`,
    backBase: 'Back to the standard replay',
    cantRerun: 'The engine and the weighted connectivity file that produced these numbers live in a private repo. What is public is the raw output of every run, so you can recompute every median and range here, but you cannot re-run the simulation itself.',
    varFixed: 'The stimulated set is fixed, so the range across five runs is the simulation\'s own randomness only.',
    varResample: 'A fresh set is drawn for every run, so the range covers both the simulation\'s randomness and which neurons happened to be picked.',
    play: 'Play this run on the stage', nodata: 'Numbers only for this one, no stage data exported',
    proto: (p: typeof PG.protocol) => `Identical protocol to the replay: w_syn ${p.w_syn_mv} mV, ${p.r_poi_hz} Hz for the first ${p.stim_ms} ms, ${p.t_run_ms} ms run, ${p.seeds} random seeds per cell. Raw numbers for every run are at /data/playground.json.`,
    note: 'This is not a live simulation in your browser. Every cell was computed beforehand on the full connectome.',
  },
};

export interface Lab {
  open(): void; close(): void; isOpen(): boolean;
  setLang(l: 'zh' | 'en'): void;
  /** 深連結用:選某個條件(play=true 時順便在舞台上播) */
  select(key: string, play?: boolean): void;
}

const esc = (s: string) => s.replace(/[&<>"]/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[m]!));
const GROUPS_ORDER = ['detect', 'gf', 'jump', 'wing', 'psi'];

export function createLab(onPlay: (key: string, bin: string, trace: string, label: string) => void): Lab {
  const el = document.getElementById('lab')!;
  let lang: 'zh' | 'en' = 'zh';
  let cur = PG.conditions[0].key;

  const byKey = (k: string) => PG.conditions.find(c => c.key === k)!;
  const stat = (s: Stat) => s.min === s.max ? `${s.median}` : `${s.median} <span class="rng">(${s.min}–${s.max})</span>`;

  function chain(c: Cond): string {
    const t = UI[lang];
    return GROUPS_ORDER.map(g => {
      const s = c.summary[g] as GroupSummary;
      if (!s) return '';
      const dead = s.fired_in === 0;
      const thin = !dead && s.fired_in < 3;
      const when = s.first_ms ? (thin ? esc(t.onlyOnce(s.fired_in)) : `${t.first} ${stat(s.first_ms)} ms`) : '';
      const note = g === 'detect' ? `<span class="tiny">${esc(t.stimRow)}</span>` : '';
      return `<div class="step${dead ? ' dead' : ''}">
        <b>${esc(GROUP_LABEL[g][lang])}</b>
        <span class="when">${dead ? esc(t.never(s.of)) : when}</span>
        <span class="runs">${dead ? '' : esc(t.fired(s.fired_in, s.of))}</span>
        ${note}
      </div>`;
    }).join('');
  }

  function render() {
    const t = UI[lang], c = byKey(cur);
    const group = (title: string, keys: string[]) =>
      `<div class="grp"><h4>${esc(title)}</h4>${keys.map(k => {
        const x = byKey(k);
        return `<button class="cond${k === cur ? ' on' : ''}" data-k="${k}">${esc(lang === 'zh' ? x.zh : x.en)}</button>`;
      }).join('')}</div>`;
    const p = PLAYABLE[cur];
    el.innerHTML = `
      <div class="labBar"><b>${esc(t.title)}</b><button id="labClose">${esc(t.close)} ✕</button></div>
      <div class="labBody">
        <p class="lead">${esc(t.lead(PG.protocol.seeds))}</p>
        ${group(t.real, ['both', 'lc4', 'lplc2'])}
        ${group(t.less, ['dose_155', 'dose_78', 'dose_39', 'dose_16'])}
        ${group(t.ctrl, ['rand_311', 'rand_126'])}
        <div class="result">
          <div class="rhead">${esc(lang === 'zh' ? c.zh : c.en)}<span>${esc(t.stim(c.n_stim))}</span>
            <em class="vary">${esc(c.resampled ? t.varResample : t.varFixed)}</em></div>
          <div class="chain">${chain(c)}</div>
          <div class="tot">${esc(t.total)} <b>${stat(c.summary.downstream_spikes)}</b>
            <span class="sub2">${esc(t.totalNote(String(c.summary.total_spikes.median), String(c.summary.stim_spikes.median)))}</span></div>
          ${(() => { const v = c.runs.map(r => r.downstream_spikes).sort((a, b) => a - b);
                     const med = v[Math.floor(v.length / 2)], k = v.filter(x => x > Math.max(200, med * 3)).length;
                     return k ? `<p class="bimodal">${esc(t.bimodal(k, v.length))}</p>` : ''; })()}
          ${p ? `<button id="labPlay">${esc(t.play)} ▶</button>` : `<p class="nodata">${esc(t.nodata)}</p>`}
          ${cur !== 'both' && PLAYABLE[cur] ? `<button id="labBase" class="ghost">${esc(t.backBase)}</button>` : ''}
        </div>
        <p class="proto">${esc(t.psiAll(PSI_SILENT, PSI_TOTAL))}</p>
        <p class="proto">${esc(t.proto(PG.protocol))}</p>
        <p class="proto strong">${esc(t.note)}</p>
        <p class="proto strong">${esc(t.cantRerun)}</p>
      </div>`;
    el.querySelectorAll<HTMLButtonElement>('.cond').forEach(b =>
      b.addEventListener('click', () => {
        cur = b.dataset.k!; render();
        // 手機上條件鈕佔滿一屏,選完要把結果捲進視野,否則使用者以為沒反應
        el.querySelector('.result')?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      }));
    document.getElementById('labClose')!.addEventListener('click', api.close);
    const pb = document.getElementById('labPlay');
    if (pb && p) pb.addEventListener('click', () => onPlay(cur, p.bin, p.trace, lang === 'zh' ? c.zh : c.en));
    const bb = document.getElementById('labBase');
    if (bb) bb.addEventListener('click', () => { const b = byKey('both'), q = PLAYABLE['both'];
      onPlay('both', q.bin, q.trace, lang === 'zh' ? b.zh : b.en); });
  }

  const api: Lab = {
    open() { el.hidden = false; render(); },
    close() { el.hidden = true; },
    isOpen() { return !el.hidden; },
    setLang(l) { lang = l; if (!el.hidden) render(); },
    select(key, play) {
      if (!PG.conditions.some(c => c.key === key)) { console.warn('實驗台:沒有這個條件', key); el.hidden = false; render(); return; }
      cur = key; el.hidden = false; render();
      const p = PLAYABLE[key];
      if (play && p) { const c = byKey(key); onPlay(key, p.bin, p.trace, lang === 'zh' ? c.zh : c.en); }
    },
  };
  return api;
}
