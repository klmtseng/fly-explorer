#!/usr/bin/env python3
"""把 vite 產物轉成 Artifact 可發佈的形式。

Artifact 會自己包 <!doctype>/<html>/<head>/<body>,所以頁面檔要直接寫內容,
不能帶那些標籤;且引用路徑不可有前導斜線。
"""
import re, pathlib, shutil, json, base64
ROOT = pathlib.Path(__file__).resolve().parent.parent
src = (ROOT/"dist/index.html").read_text(encoding="utf-8")

# artifact 的名字固定用中文那個:網站預設語言 2026-09-16 改英文,但 artifact 在藝廊裡的名稱要穩定(改了等於變成另一個頁面)
title = "果蠅腦 — 140,024 顆神經元"
style = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
body  = re.search(r"<body>(.*?)</body>", src, re.S).group(1)

# Vite 會把 module script 提到 <head>,所以要從整份文件撈,不能只看 body。
scripts = re.findall(r"<script[^>]*\bsrc=[^>]*></script>", src)
assert scripts, "找不到 script 標籤——vite 產物結構變了,不要靜默產出一個沒有程式的頁面"

page = f"<title>{title}</title>\n<style>{style}</style>\n{body.strip()}\n" + "\n".join(scripts) + "\n"
page = page.replace('src="./', 'src="').replace('href="./', 'href="')
page = page.replace('src="/', 'src="').replace('href="/', 'href="')   # Artifact 不吃前導斜線

# 所有 .bin → base64 JSON:Artifact 只服務標準 web 媒體型別,發不了 octet-stream。
for b in sorted((ROOT/"dist/data").rglob("*.bin")):
    raw = b.read_bytes()
    j = b.with_suffix(".json")
    j.write_text(json.dumps({"b64": base64.b64encode(raw).decode()}), encoding="utf-8")
    print(f"  {j.relative_to(ROOT/'dist')} {j.stat().st_size/1e6:.2f} MB (原始 {len(raw)/1e6:.2f} MB)")

out = ROOT/"dist/artifact.html"
out.write_text(page, encoding="utf-8")
print(f"→ {out} ({out.stat().st_size} bytes)")
print("引用:", re.findall(r'(?:src|href)="([^"]+)"', out.read_text(encoding='utf-8')))
