/* 說明卡:content/cards.json 直接打包(單一來源;public/ 舊快照已於 2026-09-15 審計刪除)。
 *
 * 兩組切換:小朋友/想知道更多(層)、中文/English(語)。同一份卡片,兩套皮膚:
 *   kid  = 一次一張、字大、圓角、問答可點、答完才看解釋;出處只給符號,點「出處」才展開。
 *   more = 教科書排版:事實表格(數值 | 說明 | 標記 | 出處)、字小資訊密。
 * 卡片文字是 ④(我們寫的);裡面的數字各自帶 ●◆○,規範見 docs/visual_provenance.md。
 * 觸發:step/intro 型依階段掛點出現在字幕上方的「📖」小籤;click 型從索引找;所有卡都在索引裡。
 */
import cardsJson from '../content/cards.json';

export type Lang = 'zh' | 'en';
export type Level = 'kid' | 'more';
type T = { zh: string; en: string };
interface Fact { value: string; value_en?: string; label: T; provenance: 'measured' | 'paper' | 'todo'; source: string }
interface Card {
  id: string; module: string; anchor: string; trigger: string; title: T; kid: T; more: T; facts: Fact[];
  question?: { zh: string; en: string; options: { zh: string[]; en: string[] }; answer: number };
}
const DATA = cardsJson as unknown as { modules: Record<string, T>; provenance: Record<string, { mark: string; zh: string; en: string }>; cards: Card[] };
const CARDS = DATA.cards;
const MARK: Record<string, string> = { measured: '●', paper: '◆', todo: '○' };

/** 階段時間 → 這一刻相關的掛點(step/intro 型卡片由此出現在字幕上方) */
export const STAGE_ANCHORS: Record<number, string[]> = {
  [-24]: ['whole-body', 'idle'], 0: ['intro', 'compound-eye'], 1: ['gauge'], 3: ['giant-fiber'], 8: ['neck'],
  14: ['thorax', 'wing'], 30: ['timeline', 'experiment'], 250: ['timeline', 'idle'],
};

const UI = {
  zh: { kid: '小朋友', more: '想知道更多', index: '所有卡片', close: '關閉', src: '出處', check: '看答案', right: '答對了!', wrong: '再想想,正解是:', marks: '● 我們量的 ◆ 論文 ○ 待查證/示意', cards: '卡片', of: '/', facts: '數字', value: '數值', what: '這是什麼', mark: '標記', source: '出處' },
  en: { kid: 'Kids', more: 'Learn more', index: 'All cards', close: 'Close', src: 'Source', check: 'Show answer', right: 'Correct!', wrong: 'Not quite. The answer is:', marks: '● we measured ◆ paper ○ unverified/illustrative', cards: 'Cards', of: '/', facts: 'Numbers', value: 'Value', what: 'What it is', mark: 'Mark', source: 'Source' },
};

// 英文版的出處欄:source 是機器用的指標(路徑/§段名),裡面幾句固定的中文註記在英文版換成英文;
// 沒對到的中文由 scripts/lang_residue.py 抓出來(§ 後的段名例外:那是中文文件裡的錨點)。
export const SRC_EN: [RegExp, string][] = [
  // VA 2026-09-16 新增的出處註記(英文版也要讀得懂;長句在前,避免被短句先吃掉)
  [/摘要親讀,原句/g, 'abstract read first-hand, verbatim: '],
  [/\(親讀\)——但該值是它引用 Chen & Sun 的量測,屬二手轉引;且該文是數值模擬研究,169 Hz 是它的輸入參數,不是本文的觀測/g,
   ' (read first-hand) — but that value is cited from Chen & Sun, so it is secondhand here; that paper is a numerical simulation study and 169 Hz is one of its inputs, not something it measured'],
  [/無任一顆同時連兩顆巨纖維/g, 'none connects to both giant fibers'],
  [/貢獻 6,362 個突觸、LPLC2 183\/185 貢獻 4,860/g, 'contributing 6,362 synapses; LPLC2 183\/185 contributing 4,860'],
  [/個突觸/g, ' synapses'], [/貢獻/g, 'contributing '],
  [/\(外部\)/g, '(external)'], [/ 的 /g, ' → '], [/模型沒有自發活動/g, 'the model has no spontaneous activity'],
  [/原頁被擋,數字為二手轉引/g, 'page blocked; figure is secondhand'], [/官方頁被重導向,為二手轉引/g, 'official page redirected; secondhand'],
  [/官方專案頁親讀/g, 'official project page read first-hand'], [/前導版親讀/g, 'preprint read first-hand'], [/全文親讀/g, 'full text read first-hand'],
  [/摘要經/g, 'abstract via'], [/該文引/g, 'which cites'], [/示意,無出處/g, 'illustrative, no source'], [/未引文獻/g, 'no citation'],
  [/逐柱重數,腳本內嵌於該檔/g, 'recounted per column; script embedded in that file'], [/出貨連線檔\)重算:/g, 'shipped edge file) recomputed:'],
  [/兩眼相加\)/g, 'both eyes summed)'], [/探測\)/g, 'probe)'], [/的量測\)/g, ' measurement)'], [/清單\(/g, 'list ('], [/首波/g, 'first wave'],
  [/親讀/g, 'read first-hand'], [/我們有、別人沒有的東西/g, 'What we have that others do not'],
];
export const srcText = (src: string, lang: Lang) => lang === 'en' ? SRC_EN.reduce((t, [re, en]) => t.replace(re, en), src) : src;
const factValue = (f: { value: string; value_en?: string }, lang: Lang) => lang === 'en' && f.value_en ? f.value_en : f.value;

const esc = (s: string) => s.replace(/[&<>"]/g, m => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[m]!));

export interface Cards {
  lang: Lang; level: Level;
  setLang(l: Lang): void; setLevel(l: Level): void;
  open(id: string, list?: string[]): void; openIndex(): void; close(): void;
  /** 依階段時間更新字幕上方的小籤 */
  chipsFor(stageT: number): void;
  /** 共用即時放電計數器(DESIGN.md R3):n = 出貨情境到此幀的累計真實放電數;phase 決定口氣與標示 */
  setSpikes(n: number, ms: number, phase: 'prelude' | 'live' | 'epilogue'): void;
  isOpen(): boolean;
  /** scrollytelling 用:一張卡的 HTML 與問答接線 */
  cardHtml(id: string, num?: number): string;
  wireQuiz(el: HTMLElement, id: string): void;
}

/** 開場語言:?lang= > 上次選的 > 預設英文(2026-09-16 使用者決定:網站對外以英文為預設)。
 *  抽出來是因為主程式要在 await 任何資料之前就把靜態文字換好,不能等 createCards()。*/
export function storedLang(): Lang {
  const q = new URLSearchParams(location.search).get('lang');
  if (q === 'zh' || q === 'en') return q;
  try {
    const v = localStorage.getItem('fly.cards');
    if (v) { const p = JSON.parse(v); if (p.lang === 'zh' || p.lang === 'en') return p.lang; }
  } catch { /* 無儲存也要能跑 */ }
  return 'en';
}

export function createCards(): Cards {
  const sheet = document.getElementById('sheet')!, body = document.getElementById('sheetBody')!;
  const chips = document.getElementById('chips')!, pos = document.getElementById('cPos')!;
  let lang: Lang = storedLang(), level: Level = 'kid';
  try { const v = localStorage.getItem('fly.cards'); if (v) ({ level = 'kid' } = JSON.parse(v)); } catch { /* 無儲存也要能跑 */ }
  let cur: string | null = null, list: string[] = [];
  let answered: Record<string, number> = {};   // 問答卡:這次開啟時選了哪個
  let view: 'card' | 'index' = 'index';

  const save = () => { try { localStorage.setItem('fly.cards', JSON.stringify({ lang, level })); } catch { /* ignore */ } };
  const byId = (id: string) => CARDS.find(c => c.id === id);

  function renderBar() {
    sheet.querySelectorAll<HTMLButtonElement>('[data-lvl]').forEach(b => { b.setAttribute('aria-pressed', String(b.dataset.lvl === level)); b.textContent = UI[lang][b.dataset.lvl as Level]; });
    sheet.querySelectorAll<HTMLButtonElement>('[data-lang]').forEach(b => b.setAttribute('aria-pressed', String(b.dataset.lang === lang)));
    document.getElementById('sheetIndexBtn')!.textContent = UI[lang].index;
    document.getElementById('sheetClose')!.setAttribute('aria-label', UI[lang].close);
    document.getElementById('sheetMarks')!.textContent = UI[lang].marks;
    sheet.classList.toggle('kid', level === 'kid'); sheet.classList.toggle('more', level === 'more');
  }

  function factsHtml(c: Card): string {
    if (!c.facts.length) return '';
    if (level === 'kid') {
      // 小朋友:數字大、標籤短;出處收起來,點才展開(符號一定給,不藏標記)
      return `<div class="facts">` + c.facts.map(f =>
        `<div class="fact m-${f.provenance}"><b>${MARK[f.provenance]} ${esc(factValue(f, lang))}</b><span>${esc(f.label[lang])}</span>` +
        `<details><summary>${UI[lang].src}</summary><code>${esc(srcText(f.source, lang))}</code></details></div>`).join('') + `</div>`;
    }
    return `<table class="ftab"><thead><tr><th>${UI[lang].value}</th><th>${UI[lang].what}</th><th>${UI[lang].mark}</th><th>${UI[lang].source}</th></tr></thead><tbody>` +
      c.facts.map(f => `<tr class="m-${f.provenance}"><td><b>${esc(factValue(f, lang))}</b></td><td>${esc(f.label[lang])}</td><td>${MARK[f.provenance]}</td><td><code>${esc(srcText(f.source, lang))}</code></td></tr>`).join('') + `</tbody></table>`;
  }

  /** 教科書:參考文獻清單(事實欄 source 去重、編號、懸掛縮排) */
  function refsHtml(c: Card): string {
    const srcs = [...new Set(c.facts.map(f => f.source))];
    if (!srcs.length) return '';
    return `<ul class="refs">` + srcs.map((x, i) => `<li>[${i + 1}] ${esc(srcText(x, lang))}</li>`).join('') + `</ul>`;
  }

  function questionHtml(c: Card): string {
    if (!c.question) return '';
    const q = c.question, sel = answered[c.id];
    const opts = q.options[lang].map((o, i) => {
      const cls = sel === undefined ? '' : i === q.answer ? 'ok' : i === sel ? 'no' : 'dim';
      return `<button class="opt ${cls}" data-opt="${i}" ${sel !== undefined ? 'disabled' : ''}>${esc(o)}</button>`;
    }).join('');
    const fb = sel === undefined ? '' : `<p class="fb ${sel === q.answer ? 'ok' : 'no'}">${sel === q.answer ? UI[lang].right : UI[lang].wrong + ' ' + esc(q.options[lang][q.answer])}</p>`;
    return `<div class="q"><p class="qt">${esc(q[lang])}</p><div class="opts">${opts}</div>${fb}</div>`;
  }

  /** 一張卡的 HTML(目前的層與語);scrollytelling 與抽屜共用 */
  function cardHtml(id: string, num?: number): string {
    const c = byId(id); if (!c) return '';
    const mod = DATA.modules[c.module];
    const bodyText = c[level][lang];
    // 問答卡在小朋友層:答完才給解釋(答案就在解釋裡);想知道更多層直接全給
    const hide = level === 'kid' && c.question && answered[id] === undefined;
    const inMod = CARDS.filter(x => x.module === c.module).indexOf(c) + 1;
    // 小朋友層的步驟數字:引導版由呼叫端給「第幾步」(num),抽屜用全部卡片的流水號——
    // 舊版用「模組內第幾張」,連續兩張都印 01(使用者 2026-09-16 回報)。教科書層維持「圖 B.2」(模組.序)。
    const kidNo = num ?? CARDS.indexOf(c) + 1;
    const head = level === 'kid'
      ? `<div class="num">${String(kidNo).padStart(2, '0')}</div><div class="mod">${esc(mod[lang])}</div>`
      : `<div class="mod">${lang === 'zh' ? '圖' : 'Fig.'} ${num !== undefined ? num : `${esc(c.module)}.${inMod}`} ｜ ${esc(mod[lang])}</div>`;
    // 教科書層:引導版照閱讀順序「圖 1…圖 11」(同一章的圖號連號);抽屜才用圖鑑編號「圖 B.2」(模組.序)。
    // 舊版引導版也印圖鑑編號,順序變成 A.1、E.2、D.1、B.1…(使用者 2026-09-16 回報)。
    return head + `<h2>${esc(c.title[lang])}</h2>` + questionHtml(c) +
      (hide ? '' : `<p class="txt">${esc(bodyText).replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')}</p>` + factsHtml(c) + (level === 'more' ? refsHtml(c) : ''));
  }
  /** 把問答鈕接上:答了就重畫該容器 */
  function wireQuiz(el: HTMLElement, id: string) {
    el.querySelectorAll<HTMLButtonElement>('.opt').forEach(b => b.addEventListener('click', () => { answered[id] = Number(b.dataset.opt); el.innerHTML = cardHtml(id, el.dataset.num ? Number(el.dataset.num) : undefined); wireQuiz(el, id); }));
  }
  function renderCard(id: string) {
    const c = byId(id); if (!c) return;
    cur = id; view = 'card';
    body.innerHTML = cardHtml(id);
    wireQuiz(body, id);
    const i = list.indexOf(id);
    pos.textContent = list.length > 1 ? `${i + 1} ${UI[lang].of} ${list.length}` : '';
    (document.getElementById('cPrev') as HTMLButtonElement).disabled = i <= 0;
    (document.getElementById('cNext') as HTMLButtonElement).disabled = i < 0 || i >= list.length - 1;
    body.scrollTop = 0;
  }

  function renderIndex() {
    view = 'index'; cur = null; pos.textContent = '';
    (document.getElementById('cPrev') as HTMLButtonElement).disabled = true;
    (document.getElementById('cNext') as HTMLButtonElement).disabled = true;
    let h = '';
    for (const [mid, mod] of Object.entries(DATA.modules)) {
      const cs = CARDS.filter(c => c.module === mid); if (!cs.length) continue;
      h += `<h3>${esc(mid)} · ${esc(mod[lang])}</h3><ul class="idx">` + cs.map(c =>
        `<li><button data-id="${c.id}">${c.question ? '❓ ' : ''}${esc(c.title[lang])}</button></li>`).join('') + `</ul>`;
    }
    body.innerHTML = h;
    body.querySelectorAll<HTMLButtonElement>('[data-id]').forEach(b => b.addEventListener('click', () => { list = CARDS.map(c => c.id); renderCard(b.dataset.id!); }));
    body.scrollTop = 0;
  }

  const api: Cards = {
    get lang() { return lang; }, get level() { return level; },
    setLang(l) { lang = l; save(); renderBar(); if (view === 'card' && cur) renderCard(cur); else if (!sheet.hidden) renderIndex(); api.chipsFor(lastStage); if (lastSpk) api.setSpikes(...lastSpk); },
    setLevel(l) { level = l; save(); renderBar(); if (view === 'card' && cur) renderCard(cur); if (lastSpk) api.setSpikes(...lastSpk); },
    open(id, ids) { list = ids ?? [id]; sheet.hidden = false; renderBar(); renderCard(id); },
    openIndex() { sheet.hidden = false; renderBar(); renderIndex(); },
    close() { sheet.hidden = true; },
    cardHtml, wireQuiz,
    isOpen() { return !sheet.hidden; },
    setSpikes(n, ms, phase) {
      const el = document.getElementById('spk')!; el.hidden = false;
      const N = n.toLocaleString(), T = ms.toFixed(0);
      if (phase === 'prelude') el.innerHTML = lang === 'zh' ? `<span class="inj">前奏是注入的,真實放電還沒開始</span>` : `<span class="inj">prelude is injected; no real spikes yet</span>`;
      else if (level === 'kid') el.innerHTML = lang === 'zh' ? `你剛剛看到真的神經細胞放電 <b>✓ ${N}</b> 次` : `You just watched real nerve cells fire <b>✓ ${N}</b> times`;
      else el.innerHTML = `n = <b>${N}</b> spikes · t = 0–${T} ms`;
      if (phase === 'epilogue') el.innerHTML += lang === 'zh' ? ` <span class="inj">· 之後是我們加的結局</span>` : ` <span class="inj">· ending is ours</span>`;
      lastSpk = [n, ms, phase];
    },
    chipsFor(stageT) {
      lastStage = stageT;
      const anchors = STAGE_ANCHORS[stageT] ?? [];
      const cs = CARDS.filter(c => anchors.includes(c.anchor) && (c.trigger === 'step' || c.trigger === 'intro' || c.trigger === 'click')).slice(0, 3);
      // 手機上模式列塞不下第八顆鈕:索引入口改成小籤列最後一顆「📖 全部」(桌機兩邊都有)
      chips.innerHTML = cs.map(c => `<button data-id="${c.id}">📖 ${esc(c.title[lang])}</button>`).join('') +
        `<button class="all" data-all="1">📖 ${UI[lang].index}</button>`;
      chips.hidden = false;
      chips.querySelectorAll<HTMLButtonElement>('[data-id]').forEach(b => b.addEventListener('click', () => api.open(b.dataset.id!, cs.map(c => c.id))));
      chips.querySelector<HTMLButtonElement>('[data-all]')!.addEventListener('click', () => api.openIndex());
    },
  };
  let lastStage = -24;
  let lastSpk: [number, number, 'prelude' | 'live' | 'epilogue'] | null = null;

  sheet.querySelectorAll<HTMLButtonElement>('[data-lvl]').forEach(b => b.addEventListener('click', () => api.setLevel(b.dataset.lvl as Level)));
  sheet.querySelectorAll<HTMLButtonElement>('[data-lang]').forEach(b => b.addEventListener('click', () => api.setLang(b.dataset.lang as Lang)));
  document.getElementById('sheetClose')!.addEventListener('click', api.close);
  document.getElementById('sheetIndexBtn')!.addEventListener('click', renderIndex);
  document.getElementById('cPrev')!.addEventListener('click', () => { const i = list.indexOf(cur!); if (i > 0) renderCard(list[i - 1]); });
  document.getElementById('cNext')!.addEventListener('click', () => { const i = list.indexOf(cur!); if (i >= 0 && i < list.length - 1) renderCard(list[i + 1]); });
  document.getElementById('mCards')!.addEventListener('click', () => sheet.hidden ? api.openIndex() : api.close());
  addEventListener('keydown', e => { if (e.key === 'Escape' && !sheet.hidden) api.close(); });
  renderBar();
  return api;
}
