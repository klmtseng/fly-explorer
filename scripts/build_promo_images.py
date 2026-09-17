#!/usr/bin/env python3
"""產生社群宣傳圖:英文一套、中文一套,兩套內容對齊。

使用者 2026-09-17:「英文內容配英文配圖,中文發文配中文配圖」。
在這之前是手工截的,結果中文那張圖上面的色彩圖例還是英文,而英文那組配的手機截圖卻是中文介面。
改成腳本產生,兩套一起出,不會再錯配。

產出 docs/promo/en/ 與 docs/promo/zh/,各五張:
  hero   16:9  果蠅線稿裡的發光神經系統(t=16 ms),帶色彩圖例與網址
  gf     16:9  巨纖維放電那一刻(圖上給 20 次的範圍,不給單次跑的值:圖會脫離文章被轉發)
  lab    16:9  實驗台,隨機 311 顆那一格
  phone  直式  手機實機畫面(含儀表、字幕、圖例)
  feed   4:5   直式,給動態消息

需要先 `npx vite build`。截圖用的副本會隱藏右上角的開發用效能讀數:
無頭瀏覽器裡它顯示 0 fps 是假象,不是畫面內容。其餘一律未修改。

用法:python3 scripts/build_promo_images.py
"""
import http.server, json, os, pathlib, shutil, socket, socketserver, subprocess, sys, threading, urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
OUT = ROOT / "docs/promo"
CARD = ROOT / "scripts/promo_card.html"
CHROME = os.environ.get("CHROME", "google-chrome")
FLAGS = ["--headless=new", "--no-sandbox", "--hide-scrollbars", "--enable-unsafe-swiftshader",
         "--use-gl=angle", "--use-angle=swiftshader", "--virtual-time-budget=32000"]

TEXT = {
    "en": {
        "hero": ("A real fly brain, wired as it really is",
                 "140,024 of the 166,691 neurons in the MaleCNS connectome, at their measured 3D positions, replaying a simulated escape reflex."),
        "gf": ("The giant fiber fires about 3 ms in",
               "309 of the 311 looming detectors wire straight into one giant fiber per side. Across 20 runs the giant fiber lands at 2.8 to 3.3 ms, the jump muscle nerve at 13.8 to 16.8, the wing depressor at 11.9 to 15.7. Frame shown: 4 ms."),
        "feed": ("A fly's brain, in your browser", "140,024 neurons at their measured positions. It runs on a phone."),
    },
    "zh": {
        "hero": ("神經元是真的,亮起來的是模擬",
                 "連接組 166,691 顆神經元裡,有 140,024 顆帶三維座標,網站畫的就是這些。發光的位置是真資料,活動是模擬出來的;灰色線稿是我們畫的身體。"),
        "gf": ("巨纖維大約 3 毫秒放電",
               "311 顆逼近偵測器裡有 309 顆直接接到同側的巨纖維。跑 20 次,巨纖維落在 2.8 到 3.3 毫秒,跳躍肌的神經 13.8 到 16.8,翅膀肌 11.9 到 15.7。畫面停在 4 毫秒那一幀。"),
        "feed": ("一隻果蠅的腦,放進瀏覽器", "14 萬顆神經元,位置是量出來的。手機打得開。"),
    },
}


def serve(dirpath):
    # directory 必須用 partial 傳進 __init__:設成類別屬性會被 __init__ 的 self.directory 蓋掉,
    # 結果四台伺服器全都在服務 cwd(2026-09-17 踩過,截出來的圖全是 404 頁與未打包的首頁)
    import functools
    base = type("H", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *a, **k: None})
    h = functools.partial(base, directory=str(dirpath))
    with socket.socket() as s0:
        s0.bind(("127.0.0.1", 0)); port = s0.getsockname()[1]
    srv = socketserver.TCPServer(("127.0.0.1", port), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, port


def shot(url, path, w, h, dscale=None):
    cmd = [CHROME, *FLAGS, f"--window-size={w},{h}"]
    if dscale: cmd.append(f"--force-device-scale-factor={dscale}")
    cmd += [f"--screenshot={path}", url]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    f = pathlib.Path(path)
    if not f.exists():
        sys.exit(f"截圖失敗:{url}\n{r.stderr[-300:]}")
    # 自檢:伺服器設錯時會截到 404 頁(白底黑字),而本站每一張圖都是深色舞台
    from PIL import Image
    import numpy as np
    a = np.asarray(Image.open(f).convert("L"))
    if a.mean() > 200:
        sys.exit(f"截到的看起來是錯誤頁(平均亮度 {a.mean():.0f},本站畫面應該是深色):{url}")


def main():
    if not (DIST / "index.html").exists():
        sys.exit("找不到 dist/,先跑 npx vite build")
    tmp = pathlib.Path("/tmp/promo_shotbuild")
    if tmp.exists(): shutil.rmtree(tmp)
    shutil.copytree(DIST, tmp)
    # 只為截圖隱藏開發用效能讀數(無頭環境顯示 0 fps 是假象);另備一份只留畫布的
    idx = (tmp / "index.html").read_text()
    (tmp / "index.html").write_text(idx.replace("</style>", "#perf{display:none!important}\n</style>", 1))
    stage = pathlib.Path("/tmp/promo_stagebuild")
    if stage.exists(): shutil.rmtree(stage)
    shutil.copytree(DIST, stage)
    (stage / "index.html").write_text(idx.replace(
        "</style>", "#top,#bottom,#perf,#home,#scrolly,#exitTrack,#sheet,#lab{display:none!important}\n</style>", 1))

    work = pathlib.Path('/tmp/promo_stage_img'); work.mkdir(exist_ok=True)
    srv_a, pa = serve(tmp); srv_b, pb = serve(stage); srv_c, pc = serve(CARD.parent); srv_d, pw = serve(work)
    try:
        # 舞台底圖(與語言無關):高 DPI 讓點雲維持視覺密度
        shot(f"http://127.0.0.1:{pb}/?lang=en&t=16", work / "st16.png", 800, 450, 2)
        shot(f"http://127.0.0.1:{pb}/?lang=en&t=4", work / "st4.png", 800, 450, 2)
        shot(f"http://127.0.0.1:{pb}/?lang=en&t=16", work / "stport.png", 540, 675, 2)
        for lang in ("en", "zh"):
            d = OUT / lang; d.mkdir(parents=True, exist_ok=True)
            # 實機截圖與實驗台:各自的語言
            # 手機那張:視窗要用真手機的 CSS 尺寸(390×844)。先前是 308×575,高度只有真機的三分之二,
            # 於是儀表、卡片鈕與字幕互相疊在一起——那是截圖設定造成的,不是網站在手機上的樣子(冷審 2026-09-17)。
            shot(f"http://127.0.0.1:{pa}/?preset=low&track=free&lang={lang}&t=16", d / "phone.png", 390, 844, 2)
            # 實驗台那張:英文字比中文長,1600×900 會在「下游放電」那一列以上就被切掉。
            # 改成 2000×1125 的版面配 0.8 倍縮放:輸出仍是 1600×900,但整個面板進得去。
            shot(f"http://127.0.0.1:{pa}/?preset=low&track=free&lang={lang}&lab=rand_311", d / "lab.png", 2000, 1125, 0.8)
            # 合成卡:標題與圖例都照語言
            t = TEXT[lang]
            for name, img, size in (("hero", "st16.png", (1600, 900)), ("gf", "st4.png", (1600, 900)), ("feed", "stport.png", (1080, 1350))):
                title, sub = t[name]
                url = (f"http://127.0.0.1:{pc}/promo_card.html?img=http://127.0.0.1:{pw}/{img}"
                       f"&t={urllib.parse.quote(title)}&s={urllib.parse.quote(sub)}"
                       + ("&zh=1" if lang == "zh" else ""))
                shot(url, d / f"{name}.png", *size)
            print(f"  {lang}: " + ", ".join(sorted(p.name for p in d.glob('*.png'))))
    finally:
        for s in (srv_a, srv_b, srv_c, srv_d): s.shutdown()
    print(f"→ {OUT}/en 與 {OUT}/zh")


if __name__ == "__main__":
    main()
