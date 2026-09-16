#!/usr/bin/env python3
"""MaleCNS 的輸入層與輸出層清冊。

回答「這個模型有哪些輸入、哪些輸出」——全部由標註檔的 superclass/class/subclass
欄位導出,不手寫任何分類。subclass 的縮寫含義由資料自證(節段 somaNeuromere +
出神經 exitNerve + type 名稱三者交叉),不靠記憶解讀。

輸出 runs/io_inventory.json,供下游(教學網站等)使用。
"""
import json, collections, pathlib
import pyarrow.feather as f

import os
ROOT = pathlib.Path(os.environ.get("FLY_REPO", pathlib.Path(__file__).resolve().parents[2].parent / "fly"))   # 研究倉根目錄(含 data/ 原始資料);複製到公開倉後改由環境變數指定
ANN = ROOT / "data/body-annotations-male-cns-v1.0-minconf-0.5.feather"
OUT = ROOT / "runs/io_inventory.json"

COLS = ['bodyId','type','class','subclass','superclass','status',
        'somaNeuromere','entryNerve','exitNerve']
d = f.read_table(ANN, columns=COLS).to_pydict()
N = len(d['bodyId'])
tr = [i for i in range(N) if (d['status'][i] or '') == 'Traced']

def g(i, k):
    return d[k][i] or ''

# subclass 縮寫 -> 人話。每一條都附「資料自證」欄位,說明判定依據。
MOTOR_TARGETS = {
    'fl': ("前腳",    "T1 前胸節 · ProLN 前足神經 · 脛骨屈肌/股骨縮肌"),
    'ml': ("中腳",    "T2 中胸節 · MesoLN 中足神經"),
    'hl': ("後腳",    "T3 後胸節 · MetaLN 後足神經"),
    'wm': ("翅膀",    "T2 · ADMN · DLMn/DVMn 飛行肌"),
    'nm': ("脖子",    "T1/LB · CvN 頸神經"),
    'hm': ("平衡棒",  "T3 · AbN1 · hDVM/hi1/hi2"),
    'ad': ("腹部",    "A1-A10 腹節 · AbN 腹神經"),
    'pm': ("口器/咽", "PhN 咽神經 · MxLbN 上顎唇神經 · MN1-MN12(MN9 在此)"),
    'am': ("附屬肌",  "AN · GNG 系"),
    'rm': ("其他 rm", "ON/AN"),
    'xm': ("其他 xm", "DMetaN/PDMNa"),
}

inv = {"traced_total": len(tr), "superclass": {}, "sensory": {}, "motor": {}, "relay": {}}

inv["superclass"] = dict(collections.Counter(g(i,'superclass') or '(空)' for i in tr).most_common())

sens = [i for i in tr if 'sensory' in g(i,'superclass')]
inv["sensory"] = {
    "total": len(sens),
    "by_class": dict(collections.Counter(g(i,'class') or '(未標)' for i in sens).most_common()),
}

mot = [i for i in tr if g(i,'superclass').endswith('motor')]
by_sub = collections.Counter(g(i,'subclass') or '(空)' for i in mot)
inv["motor"] = {
    "total": len(mot),
    "by_target": [
        {"code": k, "label": MOTOR_TARGETS.get(k, (k, ""))[0],
         "evidence": MOTOR_TARGETS.get(k, (k, ""))[1], "n": v}
        for k, v in by_sub.most_common()
    ],
}

for sc, label in (('descending_neuron', '下行(腦→神經索,送指令)'),
                  ('ascending_neuron',  '上行(神經索→腦,送回饋)')):
    ids = [i for i in tr if g(i,'superclass') == sc]
    inv["relay"][sc] = {"label": label, "total": len(ids)}

OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(inv, ensure_ascii=False, indent=2), encoding='utf-8')

print(f"Traced {len(tr):,}")
print(f"感覺(輸入) {len(sens):,} 顆 / {len(inv['sensory']['by_class'])} 類")
print(f"運動(輸出) {len(mot):,} 顆 / {len(inv['motor']['by_target'])} 個身體部位")
print(f"下行 {inv['relay']['descending_neuron']['total']:,}  上行 {inv['relay']['ascending_neuron']['total']:,}")
print(f"→ {OUT}")
