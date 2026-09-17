/* 實驗台:同一顆腦、同一套協定,只換「刺激哪些神經元」。
 *
 * 每一格都是**真的跑過五次**的結果(scripts/build_playground.py,協定與出貨情境完全相同),
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
  summary: Record<string, GroupSummary | Stat> & { total_spikes: Stat };
};
const PG = pgJson as unknown as {
  protocol: { w_syn_mv: number; r_poi_hz: number; t_run_ms: number; stim_ms: number; seeds: number };
  conditions: Cond[];
};

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
    lead: '同一顆腦,同一套協定,只換「刺激哪些神經元」。每一格都真的跑過五次,下面給的是中位數與五次的範圍。',
    real: '真實的偵測器', less: '減少偵測器', ctrl: '對照組',
    stim: (n: number) => `刺激 ${n} 顆神經元`,
    fired: (k: number, n: number) => `${n} 次裡 ${k} 次放電`,
    never: (n: number) => `${n} 次都沒放電`,
    total: '總放電數', first: '首次放電',
    play: '在舞台上播這一次', nodata: '這一格只有數字,沒有匯出舞台資料',
    proto: (p: typeof PG.protocol) => `協定與重播完全相同:w_syn ${p.w_syn_mv} mV、刺激 ${p.r_poi_hz} Hz 給前 ${p.stim_ms} ms、跑 ${p.t_run_ms} ms、每格 ${p.seeds} 個亂數種子。原始數字在 public/data/playground.json。`,
    note: '這不是瀏覽器裡的即時模擬。每一格都是先用完整連接組跑出來的結果。',
  },
  en: {
    title: 'Lab', close: 'Close',
    lead: 'Same brain, same protocol. The only thing that changes is which neurons get stimulated. Every cell below was actually run five times, and the numbers are the median and the range across those runs.',
    real: 'The real detectors', less: 'Fewer detectors', ctrl: 'Controls',
    stim: (n: number) => `${n} neurons stimulated`,
    fired: (k: number, n: number) => `fired in ${k} of ${n} runs`,
    never: (n: number) => `never fired in ${n} runs`,
    total: 'total spikes', first: 'first spike',
    play: 'Play this run on the stage', nodata: 'Numbers only for this one, no stage data exported',
    proto: (p: typeof PG.protocol) => `Identical protocol to the replay: w_syn ${p.w_syn_mv} mV, ${p.r_poi_hz} Hz for the first ${p.stim_ms} ms, ${p.t_run_ms} ms run, ${p.seeds} random seeds per cell. Raw numbers in public/data/playground.json.`,
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
      const when = s.first_ms ? `${t.first} ${stat(s.first_ms)} ms` : '';
      return `<div class="step${dead ? ' dead' : ''}">
        <b>${esc(GROUP_LABEL[g][lang])}</b>
        <span class="when">${dead ? esc(t.never(s.of)) : when}</span>
        <span class="runs">${dead ? '' : esc(t.fired(s.fired_in, s.of))}</span>
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
        <p class="lead">${esc(t.lead)}</p>
        ${group(t.real, ['both', 'lc4', 'lplc2'])}
        ${group(t.less, ['dose_155', 'dose_78', 'dose_39', 'dose_16'])}
        ${group(t.ctrl, ['rand_311', 'rand_126'])}
        <div class="result">
          <div class="rhead">${esc(lang === 'zh' ? c.zh : c.en)}<span>${esc(t.stim(c.n_stim))}</span></div>
          <div class="chain">${chain(c)}</div>
          <div class="tot">${esc(t.total)} <b>${stat(c.summary.total_spikes)}</b></div>
          ${p ? `<button id="labPlay">${esc(t.play)} ▶</button>` : `<p class="nodata">${esc(t.nodata)}</p>`}
        </div>
        <p class="proto">${esc(t.proto(PG.protocol))}</p>
        <p class="proto strong">${esc(t.note)}</p>
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
  }

  const api: Lab = {
    open() { el.hidden = false; render(); },
    close() { el.hidden = true; },
    isOpen() { return !el.hidden; },
    setLang(l) { lang = l; if (!el.hidden) render(); },
    select(key, play) {
      if (!PG.conditions.some(c => c.key === key)) return;
      cur = key; el.hidden = false; render();
      const p = PLAYABLE[key];
      if (play && p) { const c = byKey(key); onPlay(key, p.bin, p.trace, lang === 'zh' ? c.zh : c.en); }
    },
  };
  return api;
}
