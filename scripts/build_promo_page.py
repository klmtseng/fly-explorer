#!/usr/bin/env python3
"""從 docs/promo_drafts.md 產生發文包頁面(artifact 用的單檔 HTML)。

動機:草稿與頁面先前是手動同步,改了草稿忘了改頁面,使用者問「配圖在?」才發現。
現在頁面由草稿產生,兩邊不可能走散。

輸出 /tmp 的 promo.html(不進版控;圖片由 Artifact 的 files 參數帶上去)。
用法:python3 scripts/build_promo_page.py [輸出路徑]
"""
import pathlib, re, sys, html, json

ROOT = pathlib.Path(__file__).resolve().parent.parent
MD = ROOT / "docs/promo_drafts.md"
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "/tmp/promo.html")

# 每個平台配哪些圖(published path → 說明)。圖片本身由 Artifact 的 files 參數上傳。
SHOTS = {
    "X": [("img/hero.png", "第 1 則 · 圖 1", "16 毫秒,翅膀肌與跳躍肌的神經正在放電"),
          ("img/phone.png", "第 1 則 · 圖 2", "手機實機畫面"),
          ("img/gf.png", "第 3 則", "巨纖維放電那一刻(圖上 4 毫秒,標題寫資料值 3.3)"),
          ("img/lab.png", "第 6 則", "實驗台:隨機 311 顆,巨纖維 20 次都沒放電")],
    "Reddit": [("img/hero.png", "主圖", "貼文本體"),
               ("img/lab.png", "留言補充", "實驗台"),
               ("img/phone.png", "留言補充", "手機實機")],
    "LinkedIn": [("img/hero.png", "第一張", "1600 × 900"),
                 ("img/lab.png", "第二張", "實驗台,那個被修正的數字就在上面")],
    "Facebook": [("img/zh.png", "中文版主圖", "亮起來的,是一顆真的腦在算"),
                 ("img/feed.png", "直式", "動態消息用")],
}
LANG = {"X": "EN", "Reddit": "EN", "LinkedIn": "EN", "Facebook": "ZH"}


def esc(s): return html.escape(s, quote=False)


def parse():
    md = MD.read_text(encoding="utf-8")
    head = md.split("---", 1)[0]
    intro = "\n".join(l for l in head.splitlines()[2:] if l.strip() and not l.startswith("- ") and not l.startswith("網址"))
    secs = []
    for m in re.finditer(r"^## \d+\. ([^\(（\n]+)[^\n]*\n(.*?)(?=^## |\Z)", md, re.S | re.M):
        name, body = m.group(1).strip(), m.group(2)
        note = re.search(r"^## \d+\. [^\n]*[（(]([^）)]*)[）)]", m.group(0), re.M)
        posts = []
        for pm in re.finditer(r"^\*\*([^*]+)\*\*\n(.*?)(?=^\*\*[^*]+\*\*\n|\n---|\Z)", body, re.S | re.M):
            label, text = pm.group(1).strip(), pm.group(2).strip()
            if label.startswith("合規預審"):
                posts.append(("FLAGS", text)); continue
            if label in ("標題", "內文", "貼文") or re.match(r"^\d+/$", label):
                posts.append((label, re.sub(r"^> ", "", text, flags=re.M)))
            else:
                posts.append(("NOTE:" + label, re.sub(r"^> ", "", text, flags=re.M)))   # 操作提醒之類的區塊,渲染成提示框
        secs.append({"name": name, "note": note.group(1) if note else "", "posts": posts})
    checks = re.search(r"## 發文前最後檢查\n(.*?)$", md, re.S)
    return intro, secs, (checks.group(1) if checks else "")


def render():
    intro, secs, checks = parse()
    css = (ROOT / "scripts/promo_page.css").read_text(encoding="utf-8")
    out = [f"<title>透視果蠅發文包</title>\n<style>\n{css}</style>\n", '<div class="wrap">', "<header>",
           "<h1>透視果蠅 發文包</h1>", f"<p>{esc(intro.strip())}</p>",
           '<div class="links"><a href="https://fly-brain-explorer.vercel.app">fly-brain-explorer.vercel.app</a>'
           '<a href="https://fly-brain-explorer.vercel.app/?lab=1">?lab=1 實驗台</a>'
           '<a href="https://github.com/klmtseng/fly-explorer">github.com/klmtseng/fly-explorer</a></div>',
           "</header>"]
    for s in secs:
        if s["name"] in ("圖片", "發文前最後檢查"): continue
        out.append(f'<section><div class="head"><h2>{esc(s["name"])}</h2>'
                   f'<span class="lang">{LANG.get(s["name"], "")}</span>'
                   f'<span class="note">{esc(s["note"])}</span></div>')
        for label, text in s["posts"]:
            if label.startswith("NOTE:"):
                body_html = esc(text).replace("\n", "<br>")
                body_html = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", body_html)
                body_html = re.sub(r"`([^`]+)`", r"<code>\1</code>", body_html)
                out.append(f'<div class="imgnote"><b>{esc(label[5:])}</b><br>{body_html}</div>')
                continue
            if label == "FLAGS":
                rows = "".join(f"<tr><td>{esc(l.lstrip('- ').split(':')[0])}</td><td>{esc(l.split(':', 1)[1] if ':' in l else '')}</td></tr>"
                               for l in text.splitlines() if l.startswith("- "))
                tail = " ".join(l.lstrip("→ ") for l in text.splitlines() if l.startswith("→"))
                out.append(f'<div class="flags"><h3>合規預審 四紅旗</h3><table>{rows}</table><p>{esc(tail)}</p></div>')
                continue
            out.append('<div class="post"><div class="bar">'
                       f'<span class="n">{esc(label)}</span><span class="count"></span>'
                       f'<button class="copy">複製</button></div>'
                       f'<div class="body">{esc(text)}</div></div>')
        shots = SHOTS.get(s["name"], [])
        if shots:
            out.append('<div class="shots">' + "".join(
                f'<div class="shot"><img src="{src}" alt="{esc(cap)}"><div class="cap"><b>{esc(tag)}</b>{esc(cap)}</div></div>'
                for src, tag, cap in shots) + "</div>")
        out.append("</section>")
    items = "".join(f'<li class="{"" if l.startswith("- [x]") else "open"}">{esc(l[6:])}</li>'
                    for l in checks.splitlines() if l.startswith("- ["))
    out.append(f'<div class="check"><h2>發文前最後檢查</h2><ul>{items}</ul></div>')
    out.append('<footer>這一頁由 <code>scripts/build_promo_page.py</code> 從 <code>docs/promo_drafts.md</code> 產生,'
               '兩邊不會走散。稽核報告在 <code>audit/va_20260917.md</code>。手機長按圖片可以存檔。</footer>')
    out.append("</div>")
    out.append("""<script>
document.querySelectorAll('.post').forEach(function(p){
  var body=p.querySelector('.body'), text=body.textContent, cnt=p.querySelector('.count');
  var isX=p.closest('section').querySelector('h2').textContent.trim()==='X';
  var eff=isX?text.replace(/https?:\\/\\/\\S+/g,'x'.repeat(23)).length:text.length;
  cnt.textContent=eff+' 字'+(isX?' / 280':'');
  if(isX&&eff>280) cnt.classList.add('over');
  var b=p.querySelector('.copy');
  b.addEventListener('click',function(){navigator.clipboard.writeText(text).then(function(){
    b.textContent='已複製'; b.classList.add('done');
    setTimeout(function(){b.textContent='複製'; b.classList.remove('done');},1600);
  }).catch(function(){b.textContent='複製失敗';});});
});
</script>""")
    OUT.write_text("\n".join(out), encoding="utf-8")
    n = sum(len(s["posts"]) for s in secs)
    print(f"{len(secs)} 個平台、{n} 段文字 → {OUT} ({OUT.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    render()
