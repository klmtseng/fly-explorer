#!/usr/bin/env python3
"""英文版殘留中文掃描(確定性閘門)。

把建好的 dist/ 用無頭 Chrome 開成英文版(?lang=en),分別看首頁、小朋友版、專業版、自由探索四個畫面,
把 DOM 裡看得到的文字抓出來,任何 CJK 字元都算 FAIL——例外只有一種:「§」後面的段名
(那是指向中文文件的錨點,例如 docs/verification_log.md §六角座標慣例),以及 <script>/<style>/註解。

用法:python3 scripts/lang_residue.py            # 需要先 vite build;自己起 http.server
      python3 scripts/lang_residue.py --self-test  # 負向案例:塞一段中文進假頁面,必須 FAIL
exit 0 = PASS,非 0 = FAIL。只驗「有沒有中文」,不驗翻譯對不對。
"""
import html, pathlib, re, subprocess, sys, tempfile, time, os, socket
ROOT = pathlib.Path(__file__).resolve().parent.parent
CJK = re.compile(r"[㐀-鿿，：（）、。]")
CHROME = os.environ.get("CHROME", "google-chrome")
FLAGS = ["--headless=new", "--no-sandbox", "--enable-unsafe-swiftshader", "--use-gl=angle", "--use-angle=swiftshader",
         "--window-size=1280,800", "--virtual-time-budget=30000", "--dump-dom"]

def visible_text(dom: str) -> str:
    dom = re.sub(r"<(script|style)\b.*?</\1>", " ", dom, flags=re.S | re.I)
    dom = re.sub(r"<!--.*?-->", " ", dom, flags=re.S)
    dom = re.sub(r"<[^>]*\bhidden\b[^>]*>.*?</(div|section|button|span|p)>", " ", dom, flags=re.S)   # hidden 容器不算看得到
    txt = html.unescape(re.sub(r"<[^>]+>", " ", dom))
    txt = re.sub(r"§[^\s<;,)]+", "§", txt)          # 中文文件的段名錨點:允許
    txt = txt.replace("中文", " ")                    # 語言切換鈕上的語言名:各語言用自己的文字寫,允許
    return txt

def residues(txt: str):
    return sorted(set(m.group(0) for m in re.finditer(r"[㐀-鿿][㐀-鿿，：（）、。·]*", txt)))

def dump(url: str) -> str:
    r = subprocess.run([CHROME, *FLAGS, url], capture_output=True, text=True, timeout=120)
    return r.stdout

def main():
    if "--self-test" in sys.argv:
        fake = "<html><body><div id=x>Hello <span>世界</span></div><code>docs/a.md §六角座標慣例</code><div hidden>隱藏的</div></body></html>"
        r = residues(visible_text(fake))
        ok = r == ["世界"]
        print("self-test:", "PASS" if ok else f"FAIL {r}"); sys.exit(0 if ok else 1)
    dist = ROOT / "dist"
    if not (dist / "index.html").exists(): print("FAIL: dist/ 不存在,先 vite build"); sys.exit(2)
    with socket.socket() as s0: s0.bind(("127.0.0.1", 0)); port = s0.getsockname()[1]
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=dist,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.0)
    fails = 0
    try:
        for name, q in [("home", ""), ("kid", "&track=kid"), ("more", "&track=more"), ("free", "&track=free")]:
            dom = dump(f"http://127.0.0.1:{port}/?preset=low&lang=en{q}")
            if len(dom) < 1000: print(f"{name}: FAIL(DOM 空,Chrome 沒跑起來?)"); fails += 1; continue
            r = residues(visible_text(dom))
            print(f"{name}: {'PASS' if not r else 'FAIL'} ({len(r)} 殘留)" + (": " + " | ".join(r)[:1200] if r else ""))
            fails += bool(r)
    finally:
        srv.terminate()
    print("RESULT:", "PASS" if not fails else f"FAIL ({fails} 畫面有殘留中文)")
    sys.exit(1 if fails else 0)

if __name__ == "__main__":
    main()
