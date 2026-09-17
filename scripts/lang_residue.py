#!/usr/bin/env python3
"""英文版殘留中文掃描(確定性閘門)。

把建好的 dist/ 用無頭 Chrome 開成英文版(?lang=en),掃六個畫面 **加上 34 張卡片的兩個層級**,
把 DOM 裡看得見的文字抓出來,任何 CJK 字元都算 FAIL。

2026-09-17 冷審 P1-9 + 閘門稽核後改寫:
  ① 加掃卡片面板(`&card=<id>&level=kid|more`)——先前只掃六個畫面,而出處欄的中英混雜字串
     正好只出現在卡片裡,結構上看不到,直到人工開卡才發現。
  ② 隱藏容器改用 HTML parser 逐層判斷。原本的 `<[^>]*hidden[^>]*>.*?</div>` 非貪婪正則會在
     第一個 </div> 就收手,巢狀時把後面的東西當成「隱藏」放行,而 `\\bhidden\\b` 連
     `data-hidden="0"` 都算。現在只認獨立的 hidden 屬性與 display:none。
  ③ 「中文」兩字的豁免,原本是對整頁做字串 replace(頁面任何地方寫「中文」都會被吃掉)。
     現在只跳過語言切換鈕那一個元素。
  ④ § 段名豁免原本是 `§[^\\s<;,)]+`——一整句沒有空格的中文會被整句吃掉。現在上限 12 個字。

用法:python3 scripts/lang_residue.py               # 需要先 vite build
      python3 scripts/lang_residue.py --cards-only
      python3 scripts/lang_residue.py --self-test   # 端到端負向案例:真的起站、真的開 Chrome
exit 0 = PASS,非 0 = FAIL。只驗「有沒有中文」,不驗翻譯對不對。
"""
import html, json, pathlib, re, subprocess, sys, tempfile, time, os, socket, shutil
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
CJK = r"一-鿿"
CHROME = os.environ.get("CHROME", "google-chrome")
FLAGS = ["--headless=new", "--no-sandbox", "--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader",
         "--window-size=1280,800", "--dump-dom"]
SKIP_TAGS = {"script", "style", "template", "head"}
VOID = {"br", "img", "input", "hr", "meta", "link", "source", "path", "circle", "rect", "use"}


class Visible(HTMLParser):
    """收集看得見的文字。跳過 script/style、獨立 hidden 屬性、display:none,以及語言切換鈕。"""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out, self.stack, self.skip_depth = [], [], 0

    def _hidden(self, attrs):
        d = dict(attrs)
        if "hidden" in d and (d["hidden"] in (None, "", "hidden", "true")): return True
        if "display:none" in (d.get("style") or "").replace(" ", ""): return True
        if d.get("data-lang") == "zh": return True          # 語言切換鈕:各語言用自己的文字寫自己
        return False

    def handle_starttag(self, tag, attrs):
        if tag in VOID: return
        self.stack.append(tag)
        if self.skip_depth: self.skip_depth += 1
        elif tag in SKIP_TAGS or self._hidden(attrs): self.skip_depth = 1

    def handle_endtag(self, tag):
        if tag in VOID: return
        if tag in self.stack:
            while self.stack:
                t = self.stack.pop()
                if self.skip_depth: self.skip_depth -= 1
                if t == tag: break

    def handle_data(self, data):
        if not self.skip_depth: self.out.append(data)


def visible_text(dom: str) -> str:
    dom = re.sub(r"<!--.*?-->", " ", dom, flags=re.S)
    p = Visible(); p.feed(dom)
    txt = " ".join(p.out)
    txt = re.sub(rf"§[{CJK}\w]{{1,12}}", "§", txt)     # 中文文件裡的段名錨點:允許,但上限 12 字
    return txt


def residues(txt: str):
    return sorted(set(m.group(0) for m in re.finditer(rf"[{CJK}][{CJK}，:：（）、。·]*", txt)))


def dump(url: str, budget=30000) -> str:
    r = subprocess.run([CHROME, *FLAGS, f"--virtual-time-budget={budget}", url], capture_output=True, text=True, timeout=180)
    return r.stdout


def serve(dirpath):
    with socket.socket() as s0:
        s0.bind(("127.0.0.1", 0)); port = s0.getsockname()[1]
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=dirpath,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    return srv, port


def scan(port, name, q, budget=30000):
    dom = dump(f"http://127.0.0.1:{port}/?preset=low&lang=en{q}", budget)
    if len(dom) < 1000: return name, None
    return name, residues(visible_text(dom))


def self_test():
    """端到端:真的起一台站、真的開 Chrome、真的跑同一組判定函式。

    閘門稽核 2026-09-17:舊版 self-test 只把一段字串餵給 residues(),
    連 Chrome 都沒開——它證明的是正則會動,不是這支閘門擋得住東西。
    """
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="langres_"))
    M = "<html><head><meta charset='utf-8'></head><body>"   # 沒有 charset 的話 Chrome 會用 latin-1 解碼,測不到中文
    (tmp / "ok.html").write_text(M + "<div>Hello <span>world</span></div>"
                                 "<code>docs/a.md §六角座標慣例</code>"
                                 "<div hidden>隱藏的中文</div>"
                                 "<button data-lang='zh'>中文</button></body></html>", encoding="utf-8")
    cases = [
        ("bad.html", M + "<div>Hello <span>世界</span></div></body></html>", ["世界"]),
        # 巢狀:舊版非貪婪正則在第一個 </div> 收手,把外層後面的中文當成隱藏放行
        ("nest.html", M + "<div hidden><div>a</div></div><p>殘留中文</p></body></html>", ["殘留中文"]),
        # data-hidden 不是 hidden
        ("attr.html", M + "<div data-hidden='0'>假裝隱藏</div></body></html>", ["假裝隱藏"]),
        # § 後面接一整句:只豁免 12 字,其餘要露出來
        ("long.html", M + "<code>§這是一句很長的中文句子不該被整句豁免掉喔</code></body></html>", None),
        # 頁面正文寫「中文」兩字:只有語言鈕豁免
        ("word.html", M + "<p>中文</p></body></html>", ["中文"]),
    ]
    for fn, body, _ in cases: (tmp / fn).write_text(body, encoding="utf-8")
    srv, port = serve(tmp)
    ok = True
    try:
        r = residues(visible_text(dump(f"http://127.0.0.1:{port}/ok.html", 3000)))
        print(f"  {'✓' if not r else '✗'} 正向:乾淨頁面(含 §段名/hidden/語言鈕)→ {r or '無殘留'}")
        ok &= not r
        for fn, _, want in cases:
            r = residues(visible_text(dump(f"http://127.0.0.1:{port}/{fn}", 3000)))
            good = bool(r) if want is None else r == want
            print(f"  {'✓' if good else '✗'} 負向 {fn}: {r}" + ("" if want is None else f"(預期 {want})"))
            ok &= good
    finally:
        srv.terminate(); shutil.rmtree(tmp, ignore_errors=True)
    print("SELF-TEST", "PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)


def main():
    if "--self-test" in sys.argv: self_test()
    dist = ROOT / "dist"
    if not (dist / "index.html").exists(): print("FAIL: dist/ 不存在,先 vite build"); sys.exit(2)
    ids = [c["id"] for c in json.loads((ROOT / "content/cards.json").read_text())["cards"]]
    jobs = [] if "--cards-only" in sys.argv else [
        ("home", "", 30000), ("kid", "&track=kid", 30000), ("more", "&track=more", 30000), ("free", "&track=free", 30000),
        ("lab", "&track=free&lab=1", 30000), ("lab-rand", "&track=free&lab=rand_311&labplay=1", 30000)]
    jobs += [(f"card:{i}/{lv}", f"&track=free&card={i}&level={lv}", 9000) for i in ids for lv in ("kid", "more")]
    srv, port = serve(dist)
    fails = []
    try:
        with ThreadPoolExecutor(max_workers=4) as ex:
            for name, r in ex.map(lambda j: scan(port, j[0], j[1], j[2]), jobs):
                if r is None: print(f"{name}: FAIL(DOM 空,Chrome 沒跑起來?)"); fails.append(name); continue
                if r: print(f"{name}: FAIL ({len(r)} 殘留): " + " | ".join(r)[:400]); fails.append(name)
    finally:
        srv.terminate()
    print(f"掃了 {len(jobs)} 個畫面(含 {len(ids)} 張卡 × 2 層)")
    print("RESULT:", "PASS" if not fails else f"FAIL ({len(fails)} 個畫面有殘留中文:{', '.join(fails[:8])})")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
