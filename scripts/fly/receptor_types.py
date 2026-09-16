#!/usr/bin/env python3
"""標註檔 receptorType 欄位有哪些值(卡片 next-new-stories「這隻腦標註的受器種類」的出處)。
2026-09-16 發表前置審查發現該事實原本引用一個不存在的段落,改成這支腳本 + docs/data_facts.md 落檔。
需要 MaleCNS 標註檔(環境變數 FLY_ANN,或研究倉 data/);輸出各值計數。"""
import os, pathlib, collections, sys
import pyarrow.feather as f
ANN = pathlib.Path(os.environ.get("FLY_ANN", pathlib.Path(__file__).resolve().parents[2].parent / "fly/data/body-annotations-male-cns-v1.0-minconf-0.5.feather"))
t = f.read_table(ANN, columns=["receptorType"])
cnt = collections.Counter(x for x in t.column("receptorType").to_pylist() if x)
print(f"rows={t.num_rows} annotated={sum(cnt.values())} distinct={len(cnt)}")
for k, v in cnt.most_common(): print(f"{k}\t{v}")
