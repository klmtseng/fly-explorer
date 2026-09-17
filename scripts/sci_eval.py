#!/usr/bin/env python3
"""科學宣稱檢查器的評估台(盲測 + 逐類召回 + 誤報率 + 兩條基線)。

問題:「這句科學上對不對」沒有 ground truth,所以不能直接量準確率。
能量的是**鑑別力**:拿已驗證為真的句子,注入指定型別的錯誤但保持用詞乾淨,
看檢查器抓不抓得到;同時看它在沒動過的句子上誤報多少。

四個設計決定,每個都有理由:

1. **逐類報告,不報總分。** 總召回率會把「某一型別 0 偵測」藏起來。
   任何一類召回 0 → 整個評估 FAIL,不管總分多漂亮。
   (同一條規矩已經用在本專案其他閘門上:逐項覆蓋率。)

2. **自動附兩條基線**:always-ok(全部說沒問題)與 always-flag(全部說有問題)。
   前者召回 0 誤報 0,後者召回 1.0 誤報 1.0。任何受測檢查器的數字都跟這兩條並排印,
   所以「召回 0.9!」不可能單獨被讀成好消息。

3. **盲測**:交給檢查器的 `sci_eval_set.jsonl` 只有不透明 id 與句子,沒有 label 也沒有 class。
   答案在另一個檔。**這是程序上的盲,不是密碼學上的盲**——語料檔就在同一個 repo 裡,
   一個存心的檢查器讀得到。所以跑真評估時要派沒有本倉脈絡的 fresh-context 檢查者,
   並在報告裡寫明這一點。

4. **變異體注入在過濾器上游**。受測的是整條管線(揀句子 → 判斷),
   所以被 `sci_claims.py` 漏掉的變異體算「沒抓到」,而不是不算。

用法:
  python3 scripts/sci_eval.py --make                 # 產生 set 與 key
  python3 scripts/sci_eval.py --run "<檢查器指令>"     # 跑並評分(指令讀 stdin 吐 JSONL)
  python3 scripts/sci_eval.py --score answers.jsonl  # 評既有答案
  python3 scripts/sci_eval.py --score a.jsonl --only-needs literature --drop-in-sample
  python3 scripts/sci_eval.py --self-test
答案格式(每行):{"item": "<id>", "verdict": "ok"|"flag", "why": "...", "source": "選填"}
exit 0 = 評估完成且沒有零召回的類別,非 0 = 有類別完全抓不到,或答案不完整。
"""
import hashlib, json, pathlib, random, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MUT = ROOT / "audit/sci_mutants.jsonl"
SET = ROOT / "audit/sci_eval_set.jsonl"
KEY = ROOT / "audit/sci_eval_key.json"


def load_corpus(path=MUT):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if "_comment" in r:
            continue
        rows.append(r)
    return rows


def make(corpus, seed=20260917, set_path=SET, key_path=KEY):
    items, key = [], {}
    for r in corpus:
        oid = "it-" + hashlib.sha1(f"{seed}|{r['id']}".encode()).hexdigest()[:8]
        items.append({"item": oid, "where": r.get("where", ""), "text": r["text"]})
        key[oid] = {"src_id": r["id"], "label": r["label"], "class": r.get("class", "-"),
                    "needs": r.get("needs", "?"), "in_sample": r.get("in_sample", False),
                    "why_wrong": r.get("why_wrong", ""), "source": r.get("source", "")}
    random.Random(seed).shuffle(items)
    set_path.write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items), encoding="utf-8")
    key_path.write_text(json.dumps({"seed": seed, "key": key}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return items, key


def baseline(key, verdict):
    return [{"item": k, "verdict": verdict} for k in key]


def subset(key, only_needs=None, drop_in_sample=False):
    """按「這題要靠什麼才判得出來」篩題。
    2026-09-17 盲測踩到的坑:我禁止檢查器讀本倉,卻考了它十題非有本倉量測不可的題目,
    於是那些「漏抓」量到的是資料取用權,不是科學判斷力。評分要嘛按 needs 分開看,
    要嘛就得把該給的資料給它。"""
    return {k: v for k, v in key.items()
            if (only_needs is None or v.get("needs") == only_needs)
            and not (drop_in_sample and v.get("in_sample"))}


def score(key, answers):
    """回傳 (逐類召回, 誤報率, 問題清單)。"""
    got = {}
    problems = []
    for a in answers:
        if a.get("item") not in key:
            problems.append(f"答案裡有不在題目裡的 id:{a.get('item')}")
            continue
        if a.get("verdict") not in ("ok", "flag"):
            problems.append(f"{a['item']} 的 verdict 不是 ok/flag:{a.get('verdict')!r}")
            continue
        got[a["item"]] = a
    missing = [k for k in key if k not in got]
    if missing:
        problems.append(f"{len(missing)} 題沒作答(視同 ok):{', '.join(missing[:4])}…")
    by_class, by_needs, fp, n_ok, ungrounded = {}, {}, 0, 0, 0
    for k, meta in key.items():
        flagged = got.get(k, {}).get("verdict") == "flag"
        if meta["label"] == "bad":
            c = by_class.setdefault(meta["class"], [0, 0])
            c[1] += 1
            c[0] += flagged
            n = by_needs.setdefault(meta.get("needs", "?"), [0, 0])
            n[1] += 1
            n[0] += flagged
        else:
            n_ok += 1
            fp += flagged
        if flagged and not got.get(k, {}).get("source"):
            ungrounded += 1
    return by_class, by_needs, (fp, n_ok), problems, ungrounded


def report(label, key, answers, quiet=False):
    by_class, by_needs, (fp, n_ok), problems, ungrounded = score(key, answers)
    hit = sum(c[0] for c in by_class.values())
    tot = sum(c[1] for c in by_class.values())
    if not quiet:
        print(f"\n【{label}】")
        for c, (h, n) in sorted(by_class.items()):
            bar = "零召回 ←" if h == 0 else ""
            print(f"  {c:24s} 召回 {h}/{n} = {h/n:.2f}  {bar}")
        print(f"  {'總計(僅供參考)':22s} 召回 {hit}/{tot} = {hit/tot:.2f}"
              f" | 誤報 {fp}/{n_ok} = {fp/max(1,n_ok):.2f} | flag 但沒附出處 {ungrounded}")
        for p in problems:
            print("  ⚠", p)
    if not quiet and by_needs:
        print("  ── 按「判得出來要靠什麼」拆:" +
              " | ".join(f"{n} {h}/{t}" for n, (h, t) in sorted(by_needs.items())))
    zero = [c for c, (h, _) in by_class.items() if h == 0]
    return zero, problems


def run_cmd(cmd, items):
    payload = "".join(json.dumps(i, ensure_ascii=False) + "\n" for i in items)
    r = subprocess.run(cmd, shell=True, input=payload, capture_output=True, text=True, timeout=1800)
    out = []
    for line in r.stdout.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    if not out:
        print("檢查器沒有吐出任何 JSONL。stderr 末段:\n" + r.stderr[-400:])
    return out


def main():
    if "--self-test" in sys.argv:
        import tempfile
        tmp = pathlib.Path(tempfile.mkdtemp())
        mut = tmp / "m.jsonl"
        mut.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in [
            {"id": "ok-a", "label": "ok", "text": "甲"}, {"id": "ok-b", "label": "ok", "text": "乙"},
            {"id": "b-1", "label": "bad", "class": "X", "text": "丙"},
            {"id": "b-2", "label": "bad", "class": "Y", "text": "丁", "needs": "own-data"},
            {"id": "b-3", "label": "bad", "class": "Y", "text": "戊", "needs": "literature", "in_sample": True},
        ]), encoding="utf-8")
        items, key = make(load_corpus(mut), 1, tmp / "s.jsonl", tmp / "k.json")
        ok = []
        # ① 盲:題目檔不得洩漏 label / class / why_wrong
        leak = [f for f in ("label", "class", "why_wrong", "ok-a", "b-1") if f in (tmp / "s.jsonl").read_text()]
        ok.append(("題目檔沒有洩漏答案", not leak))
        # ② 完美作答:每類召回 1.0、誤報 0、無零召回類別
        perfect = [{"item": k, "verdict": "flag" if v["label"] == "bad" else "ok", "source": "s"} for k, v in key.items()]
        z, p = report("自測 完美", key, perfect, quiet=True)
        ok.append(("完美作答:沒有零召回類別", not z and not p))
        # ③ 偷懶作答(全說沒問題):必須被判出兩個零召回類別
        z, _ = report("自測 always-ok", key, baseline(key, "ok"), quiet=True)
        ok.append(("全說沒問題 → 抓出零召回類別", sorted(z) == ["X", "Y"]))
        # ④ 亂 flag:召回滿分但誤報也滿分,評估必須把誤報算出來
        by, _bn, (fp, n_ok), _, ung = score(key, baseline(key, "flag"))
        ok.append(("全部 flag → 誤報率 1.0 被算出來", fp == n_ok == 2))
        ok.append(("全部 flag → 沒附出處被算出來", ung == len(key)))
        # ⑤ needs 篩選與 in_sample 排除
        lit = subset(key, "literature")
        ok.append(("--only-needs 篩得出 literature 題", len(lit) == 1 and all(v["needs"] == "literature" for v in lit.values())))
        ok.append(("--drop-in-sample 排得掉看過答案的題", len(subset(key, "literature", True)) == 0))
        # ⑥ 漏答要被抓
        _, p = report("自測 漏答", key, perfect[:2], quiet=True)
        ok.append(("漏答被列為問題", any("沒作答" in x for x in p)))
        # ⑦ 亂寫 id 要被抓
        _, p = report("自測 亂 id", key, perfect + [{"item": "it-zzzz", "verdict": "flag"}], quiet=True)
        ok.append(("不在題目裡的 id 被抓", any("不在題目裡" in x for x in p)))
        for name, good in ok:
            print(f"  {'✓' if good else '✗'} {name}")
        print("SELF-TEST", "PASS" if all(g for _, g in ok) else "FAIL")
        sys.exit(0 if all(g for _, g in ok) else 1)

    corpus = load_corpus()
    if "--make" in sys.argv:
        items, key = make(corpus)
        n_bad = sum(1 for v in key.values() if v["label"] == "bad")
        classes = sorted({v["class"] for v in key.values() if v["label"] == "bad"})
        print(f"題目 {len(items)} 題({n_bad} 個變異體 / {len(items)-n_bad} 個已驗證為真)→ {SET.relative_to(ROOT)}")
        print(f"錯誤型別 {len(classes)} 類:{', '.join(classes)}")
        print(f"答案在 {KEY.relative_to(ROOT)}——交給檢查器的只有題目檔。")
        return

    key = json.loads(KEY.read_text())["key"]
    items = [json.loads(l) for l in SET.read_text(encoding="utf-8").splitlines() if l.strip()]
    only = sys.argv[sys.argv.index("--only-needs") + 1] if "--only-needs" in sys.argv else None
    drop = "--drop-in-sample" in sys.argv
    if only or drop:
        key = subset(key, only, drop)
        items = [i for i in items if i["item"] in key]
        print(f"(只計 needs={only or '全部'}" + (",且排除 in_sample 題" if drop else "") + f":{len(key)} 題)")
    if "--run" in sys.argv:
        cmd = sys.argv[sys.argv.index("--run") + 1]
        answers = run_cmd(cmd, items)
        label = f"受測檢查器:{cmd[:40]}"
    elif "--score" in sys.argv:
        f = pathlib.Path(sys.argv[sys.argv.index("--score") + 1])
        answers = [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip().startswith("{")]
        label = f"受測檢查器:{f.name}"
    else:
        print(__doc__); sys.exit(2)

    if only or drop:
        # 篩過題目之後,被篩掉那些題的答案不是「亂寫的 id」,只是不在這次計分範圍
        answers = [a for a in answers if a.get("item") in key]
    report("基線 always-ok(全部說沒問題)", key, baseline(key, "ok"))
    report("基線 always-flag(全部說有問題)", key, baseline(key, "flag"))
    zero, problems = report(label, key, answers)
    print("\n判準:任一類別召回 0 即 FAIL;誤報率與『沒附出處』要跟召回一起讀,不得單看召回。")
    bad = bool(zero) or any("不在題目裡" in p for p in problems)
    if zero:
        print("零召回類別:" + ", ".join(zero))
    print("RESULT:", "PASS" if not bad else "FAIL")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
