#!/usr/bin/env python3
"""參考檢查器(確定性下限):只用 sci_claims.py 的過濾器判斷。

它不懂科學,只會說「這句在做推論又提到外部實體,可疑」。存在的意義是給評估台一條
**比 always-flag 有意義、比真檢查器笨得多**的下限:任何模型檢查器如果贏不過它,
就不值得付那個成本。讀 stdin 的 JSONL,吐 stdout 的 JSONL。
"""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from sci_claims import is_candidate

for line in sys.stdin:
    line = line.strip()
    if not line.startswith("{"):
        continue
    it = json.loads(line)
    t = it["text"]
    trig = is_candidate(t)
    flag = trig is not None
    print(json.dumps({"item": it["item"], "verdict": "flag" if flag else "ok",
                      "why": f"過濾器觸發 {trig}(不含科學判斷)" if flag else "過濾器沒揀到"},
                     ensure_ascii=False))
