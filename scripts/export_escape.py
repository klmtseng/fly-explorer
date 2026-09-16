#!/usr/bin/env python3
"""匯出「看見逼近 → 跳走」這條逃跑迴路的神經元座標與角色。

整條鏈只有約 345 顆,遠小於全腦 140,024 顆,所以可以每一顆都個別畫、個別點擊,
比在點雲裡找光斑清楚得多。

角色順序就是訊號傳遞順序,前端照這個順序逐段點亮。
"""
import json, pathlib, collections, re, sys
import pyarrow.feather as f

ROOT = pathlib.Path(__file__).resolve().parent.parent
ANN = ROOT.parent / "fly/data/body-annotations-male-cns-v1.0-minconf-0.5.feather"
OUT = ROOT / "public/data/escape.json"

# (角色key, type 比對正則, 中文, 英文, 說明, 預期顆數)。順序 = 訊號傳遞順序。
#
# ⚠️ 不可一律用 startswith:`LC4` 的前綴會多撈 LC40/41/43/44/46b 共 76 顆
#    完全不同的細胞型別(實測)。但 DLMn/DVMn 又非用前綴不可(真實 type 是 "DLMn c-f")。
#    所以逐段指定正則,並用預期顆數斷言擋住下次再犯。
STAGES = [
    ("lc4",   r"LC4",        "LC4 逼近偵測",   "LC4 looming detector",  "偵測逼近速度",        126),
    ("lplc2", r"LPLC2",      "LPLC2 逼近偵測", "LPLC2 looming detector","偵測視角大小",        185),
    ("gf",    r"DNp01",      "巨纖維",        "Giant fiber",           "全腦最粗的神經,左右各一",  2),
    ("psi",   r"PSI",        "PSI 中繼",      "PSI relay",             "教科書中繼站;模型裡 28.5ms 才放電,晚於翅膀肌",  2),
    ("ttm",   r"TTMn",       "跳躍肌神經元",   "Jump muscle MN",        "巨纖維直連;首次放電 13.7ms",  2),
    ("dlm",   r"DLMn[\s,a-f-]*", "翅膀下壓肌", "Wing depressor MN",    "首次放電 12.7ms,早於 PSI——第一波不走 PSI",  10),
    ("dvm",   r"DVMn[\s,0-9a-c-]*","翅膀上舉肌","Wing elevator MN",     "",                    14),
]

d = f.read_table(ANN, columns=['bodyId','type','status','somaLocation','somaSide']).to_pydict()
N = len(d['bodyId'])

out = {"stages": [], "neurons": []}
missing = collections.Counter()
bad = []
for key, pat, zh, en, note, expect in STAGES:
    rx = re.compile(pat + r"$")
    ids = [i for i in range(N)
           if (d['status'][i] or '') == 'Traced' and rx.match(d['type'][i] or '')]
    if len(ids) != expect:
        bad.append(f"{key}: 抓到 {len(ids)} 顆,預期 {expect}")
    kept = 0
    for i in ids:
        loc = d['somaLocation'][i]
        if loc is None:
            missing[key] += 1
            continue
        out["neurons"].append({
            "id": int(d['bodyId'][i]), "stage": key,
            "type": d['type'][i], "side": d['somaSide'][i] or "?",
            "p": [int(loc[0]), int(loc[1]), int(loc[2])],
        })
        kept += 1
    out["stages"].append({"key": key, "zh": zh, "en": en, "note": note,
                          "n_total": len(ids), "n_placed": kept})
    print(f"{zh:16s} {len(ids):4d} 顆,有座標 {kept:4d}" + (f"  (缺 {missing[key]})" if missing[key] else ""))

if bad:
    print("\n❌ 顆數與預期不符,不產生檔案(預期值來自主線先前實測並經文獻對照):")
    for b in bad: print("   " + b)
    sys.exit(1)

OUT.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
print(f"\n合計 {len(out['neurons'])} 顆可定位 → {OUT} ({OUT.stat().st_size/1024:.0f} KB)")
if missing:
    print("⚠️ 缺座標的:", dict(missing), "—— 前端要能處理缺漏,不可假設每顆都畫得出來")
