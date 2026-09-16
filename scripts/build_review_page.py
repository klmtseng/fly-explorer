#!/usr/bin/env python3
"""從 content/cards.json 生成給人審閱的頁面。

單一來源原則:文案只存在 cards.json,這支只負責渲染。
改文案改 JSON,重跑這支,不要直接改產出的 HTML。
"""
import json, pathlib, html
ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = json.loads((ROOT/"content/cards.json").read_text(encoding="utf-8"))
OUT = ROOT/"docs/content_review.html"

n_cards = len(DATA["cards"])
n_meas = sum(1 for c in DATA["cards"] for f in c["facts"] if f["provenance"] == "measured")
n_paper = sum(1 for c in DATA["cards"] for f in c["facts"] if f["provenance"] == "paper")
n_q = sum(1 for c in DATA["cards"] if "question" in c)

HTML = """<title>果蠅網站內容清單</title>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Chivo:wght@700;900&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root{
  --paper:#F5F6F3; --panel:#ECEEE9; --card:#FFFFFF;
  --ink:#14181C; --ink-2:#4C545A; --ink-3:#79827F;
  --rule:#D3D8CF; --rule-soft:#E3E7DF;
  --exc:#B4661B; --exc-soft:#F0E3D2; --inh:#17646E; --inh-soft:#D8E5E6;
  --todo:#8A6A9E;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --paper:#101310; --panel:#181C18; --card:#1C211C;
  --ink:#E8EBE2; --ink-2:#A9B1A6; --ink-3:#7E867C;
  --rule:#323930; --rule-soft:#262C25;
  --exc:#E8973F; --exc-soft:#392B16; --inh:#5FC0CC; --inh-soft:#153238;
  --todo:#B592C9;
}}
:root[data-theme="dark"]{
  --paper:#101310; --panel:#181C18; --card:#1C211C;
  --ink:#E8EBE2; --ink-2:#A9B1A6; --ink-3:#7E867C;
  --rule:#323930; --rule-soft:#262C25;
  --exc:#E8973F; --exc-soft:#392B16; --inh:#5FC0CC; --inh-soft:#153238;
  --todo:#B592C9;
}
*{box-sizing:border-box}
body{background:var(--paper);color:var(--ink);margin:0;
  font-family:"IBM Plex Sans","PingFang TC","Noto Sans TC","Microsoft JhengHei",system-ui,sans-serif;
  font-size:15.5px;line-height:1.7;-webkit-font-smoothing:antialiased}
.wrap{max-width:940px;margin:0 auto;padding:0 24px 100px}
h1{font-family:Chivo,system-ui,sans-serif;font-weight:900;font-size:clamp(28px,4.6vw,42px);
  letter-spacing:-.02em;margin:0;line-height:1.05}
.mast{padding:46px 0 22px}
.sub{color:var(--ink-2);margin:14px 0 0;max-width:56ch}
.stats{display:flex;flex-wrap:wrap;gap:0;margin:26px 0 0;border:1px solid var(--rule-soft)}
.stats div{flex:1 1 130px;padding:12px 16px;border-right:1px solid var(--rule-soft)}
.stats div:last-child{border-right:none}
.stats b{font-family:"IBM Plex Mono",monospace;font-size:21px;font-weight:500;display:block;letter-spacing:-.02em}
.stats span{font-size:11.5px;color:var(--ink-3);display:block;margin-top:2px}
.bar{position:sticky;top:0;z-index:5;background:var(--paper);
  border-bottom:1px solid var(--rule);padding:11px 0;margin-bottom:8px;
  display:flex;gap:22px;flex-wrap:wrap;align-items:center}
.grp{display:flex;gap:0;border:1px solid var(--rule);border-radius:2px;overflow:hidden}
.grp button{font:500 12px/1 "IBM Plex Mono",monospace;padding:8px 14px;border:0;cursor:pointer;
  background:transparent;color:var(--ink-2);letter-spacing:.04em}
.grp button[aria-pressed="true"]{background:var(--ink);color:var(--paper)}
.grp button:focus-visible{outline:2px solid var(--exc);outline-offset:-2px}
.legend{font-family:"IBM Plex Mono",monospace;font-size:11.5px;color:var(--ink-3);
  display:flex;gap:14px;flex-wrap:wrap;margin-left:auto}
h2{font-family:Chivo,system-ui,sans-serif;font-size:19px;font-weight:700;margin:44px 0 4px;
  display:flex;align-items:baseline;gap:12px}
h2 em{font-style:normal;font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--exc);
  letter-spacing:.1em}
h2 .cnt{font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--ink-3);font-weight:400;margin-left:auto}
.modnote{color:var(--ink-3);font-size:13px;margin:0 0 14px;border-bottom:1px solid var(--rule);padding-bottom:12px}
.card{background:var(--card);border:1px solid var(--rule-soft);padding:20px 22px;margin:12px 0}
.card h3{font-family:Chivo,system-ui,sans-serif;font-size:17.5px;font-weight:700;margin:0 0 4px;letter-spacing:-.01em}
.cid{font-family:"IBM Plex Mono",monospace;font-size:10.5px;color:var(--ink-3);letter-spacing:.08em;
  display:flex;gap:12px;flex-wrap:wrap;margin-bottom:10px}
.cid span::before{content:"";display:inline-block}
.q{background:var(--exc-soft);border-left:2px solid var(--exc);padding:12px 15px;margin:12px 0;font-size:14.5px}
.q .qlab{font-family:"IBM Plex Mono",monospace;font-size:10.5px;letter-spacing:.12em;
  text-transform:uppercase;color:var(--exc);display:block;margin-bottom:5px}
.q ol{margin:8px 0 0;padding-left:20px;font-size:14px;color:var(--ink-2)}
.q li.ans{color:var(--exc);font-weight:600}
.body{margin:10px 0 0}
.facts{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px;padding-top:13px;border-top:1px solid var(--rule-soft)}
.fact{border:1px solid var(--rule-soft);padding:7px 11px;font-size:12.5px;line-height:1.45}
.fact b{font-family:"IBM Plex Mono",monospace;font-size:14px;font-weight:500;display:block}
.fact .src{font-family:"IBM Plex Mono",monospace;font-size:10px;color:var(--ink-3);display:block;margin-top:3px}
.m-measured{border-left:2px solid var(--inh)} .m-measured b{color:var(--inh)}
.m-paper{border-left:2px solid var(--exc)} .m-paper b{color:var(--exc)}
.m-todo{border-left:2px solid var(--todo)} .m-todo b{color:var(--todo)}
.noface{font-size:12.5px;color:var(--ink-3);margin-top:12px;padding-top:12px;border-top:1px solid var(--rule-soft);
  font-family:"IBM Plex Mono",monospace}
footer{margin-top:60px;padding-top:20px;border-top:1px solid var(--rule);font-size:12.5px;color:var(--ink-3)}
[hidden]{display:none!important}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
<div class="wrap">
<header class="mast">
  <h1>果蠅網站內容清單</h1>
  <p class="sub">__NCARDS__ 張說明卡的初稿。每張都有中英雙語 × 小朋友／進階雙層，每個數字都標了出處。
     用上面的切換鈕實際讀讀看，決定哪些留、哪些砍、哪些要改寫。</p>
  <div class="stats">
    <div><b>__NCARDS__</b><span>說明卡</span></div>
    <div><b>__NMEAS__</b><span>● 我們量的數字</span></div>
    <div><b>__NPAPER__</b><span>◆ 論文來源</span></div>
    <div><b>__NQ__</b><span>先問再答的卡</span></div>
  </div>
</header>
<div class="bar">
  <div class="grp" role="group" aria-label="語言">
    <button data-set="lang" data-val="zh">中文</button>
    <button data-set="lang" data-val="en">English</button>
  </div>
  <div class="grp" role="group" aria-label="深度">
    <button data-set="lvl" data-val="kid">小朋友</button>
    <button data-set="lvl" data-val="more">想知道更多</button>
  </div>
  <div class="legend">
    <span style="color:var(--inh)">● 我們量的</span>
    <span style="color:var(--exc)">◆ 論文</span>
    <span style="color:var(--todo)">○ 待查證</span>
  </div>
</div>
<main id="out"></main>
<footer>
  <p>文案單一來源：<code>content/cards.json</code>。本頁由 <code>scripts/build_review_page.py</code> 生成，請勿直接編輯 HTML。</p>
  <p>資料 MaleCNS v1.0 (CC-BY 4.0)，Berg et al., <i>Cell</i> 189(18):5504–5526 (2026)。模型參數 Shiu et al., <i>Nature</i> 634:210–219 (2024)。</p>
</footer>
</div>
<script>
const DATA = __JSON__;
const S = {lang:'zh', lvl:'kid'};
try{ const v=localStorage.getItem('flyrev'); if(v){Object.assign(S, JSON.parse(v));} }catch(e){}
const esc = s => String(s).replace(/[&<>"]/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));
const MARK = {measured:'●', paper:'◆', todo:'○'};

function render(){
  const byMod = {};
  DATA.cards.forEach(c => (byMod[c.module] ||= []).push(c));
  let h = '';
  for(const [mid, mod] of Object.entries(DATA.modules)){
    const list = byMod[mid]; if(!list) continue;
    h += `<h2><em>${esc(mid)}</em>${esc(mod[S.lang])}<span class="cnt">${list.length} 張</span></h2>`;
    h += `<p class="modnote">${esc(mod.zh)} · ${esc(mod.en)}</p>`;
    for(const c of list){
      h += `<article class="card"><h3>${esc(c.title[S.lang])}</h3>`;
      h += `<div class="cid"><span>${esc(c.id)}</span><span>掛點 ${esc(c.anchor)}</span><span>觸發 ${esc(c.trigger)}</span></div>`;
      if(c.question){
        const q = c.question;
        h += `<div class="q"><span class="qlab">先問再答</span>${esc(q[S.lang])}<ol>`;
        (q.options[S.lang]||[]).forEach((o,i) => {
          h += `<li class="${i===q.answer?'ans':''}">${esc(o)}${i===q.answer?' ✓':''}</li>`;
        });
        h += `</ol></div>`;
      }
      h += `<p class="body">${esc(c[S.lvl][S.lang])}</p>`;
      if(c.facts.length){
        h += '<div class="facts">';
        for(const f of c.facts){
          h += `<div class="fact m-${esc(f.provenance)}"><b>${MARK[f.provenance]} ${esc(f.value)}</b>`
             + `${esc(f.label[S.lang])}<span class="src">${esc(f.source)}</span></div>`;
        }
        h += '</div>';
      } else {
        h += `<p class="noface">純概念卡，沒有數字</p>`;
      }
      h += `</article>`;
    }
  }
  document.getElementById('out').innerHTML = h;
  document.querySelectorAll('.grp button').forEach(b => {
    b.setAttribute('aria-pressed', String(S[b.dataset.set] === b.dataset.val));
  });
}
document.querySelectorAll('.grp button').forEach(b => b.addEventListener('click', () => {
  S[b.dataset.set] = b.dataset.val;
  try{ localStorage.setItem('flyrev', JSON.stringify(S)); }catch(e){}
  render();
}));
render();
</script>
"""
OUT.parent.mkdir(exist_ok=True)
out = (HTML.replace("__JSON__", json.dumps(DATA, ensure_ascii=False))
           .replace("__NCARDS__", str(n_cards)).replace("__NMEAS__", str(n_meas))
           .replace("__NPAPER__", str(n_paper)).replace("__NQ__", str(n_q)))
OUT.write_text(out, encoding="utf-8")
print(f"{n_cards} 張卡 → {OUT} ({OUT.stat().st_size/1024:.0f} KB)")
