#!/usr/bin/env python3
"""實驗台資料的閘門(validity-audit 2026-09-17 挑戰[3]:實驗台是全站唯一沒有確定性檢查的資料)。

public/data/playground.json 是網頁直接顯示的數字。它原本沒有任何機器檢查:
summary 若被手改、或與 runs 不一致,沒有東西會擋。這支補上四道:

  P1 summary 必須能由 runs 重算出來(中位數、最小、最大、fired_in),逐格逐族群比對。
  P2 基準條件(both)的**種子 1** 必須逐項等於出貨情境 runs/build/escape.csv 的實際值
     ——這是「重跑管線沒壞」的唯一硬證據,對不上代表兩邊的協定已經漂開。
  P3 條件數、每格次數、可播條件的 .bin 檔必須與 src/lab.ts 宣告的一致(覆蓋宣稱重數)。
  P4 網頁文案講的「跑過 N 次」必須等於實際次數。

--self-test 跑三個負向案例:改 summary、改 seed-1 讀數、拿掉一個可播檔,三者都必須被擋。
exit 0 = PASS,非 0 = FAIL。
"""
import json, pathlib, statistics, sys, csv, collections, copy, tempfile, subprocess, os, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
PG_PATH = pathlib.Path(os.environ.get("PLAYGROUND_JSON", ROOT / "public/data/playground.json"))
LAB_TS = ROOT / "src/lab.ts"
ESCAPE_CSV = ROOT / "runs/build/escape.csv"
GROUPS_CACHE = ROOT / "runs/build/escape_groups.json"
SCEN = ROOT / "public/data/scenarios"
GROUPS = ["detect", "gf", "jump", "wing", "psi"]


def fail(msgs, m):
    msgs.append(m)


def p1_summary_recomputable(pg, msgs):
    """summary 必須是 runs 算出來的,不是手寫的。"""
    for c in pg["conditions"]:
        runs = c["runs"]
        tot = [r["total_spikes"] for r in runs]
        want = {"median": int(statistics.median(tot)), "min": min(tot), "max": max(tot)}
        if c["summary"]["total_spikes"] != want:
            fail(msgs, f"P1 {c['key']} total_spikes 與 runs 重算不符:檔案 {c['summary']['total_spikes']} vs 重算 {want}")
        for g in GROUPS:
            s = c["summary"].get(g)
            if s is None:
                fail(msgs, f"P1 {c['key']} 缺族群 {g}"); continue
            firsts = [r["first_ms"][g] for r in runs if g in r["first_ms"]]
            counts = [r["count"].get(g, 0) for r in runs]
            if s["fired_in"] != len(firsts) or s["of"] != len(runs):
                fail(msgs, f"P1 {c['key']}/{g} fired_in/of 不符:檔案 {s['fired_in']}/{s['of']} vs 重算 {len(firsts)}/{len(runs)}")
            wf = {"median": round(statistics.median(firsts), 2), "min": min(firsts), "max": max(firsts)} if firsts else None
            if s["first_ms"] != wf:
                fail(msgs, f"P1 {c['key']}/{g} first_ms 不符:檔案 {s['first_ms']} vs 重算 {wf}")
            wc = {"median": int(statistics.median(counts)), "min": min(counts), "max": max(counts)}
            if s["count"] != wc:
                fail(msgs, f"P1 {c['key']}/{g} count 不符:檔案 {s['count']} vs 重算 {wc}")


def p2_seed1_matches_shipped(pg, msgs):
    """基準條件的第一次(種子 1)必須等於出貨情境的實際放電資料。"""
    if not ESCAPE_CSV.exists() or not GROUPS_CACHE.exists():
        fail(msgs, f"P2 無法驗證:找不到 {ESCAPE_CSV.name} 或 {GROUPS_CACHE.name}")
        return
    grp = {int(k): v for k, v in json.loads(GROUPS_CACHE.read_text()).items()}
    first, count, total = {}, collections.Counter(), 0
    with open(ESCAPE_CSV) as fh:
        for row in csv.DictReader(fh):
            total += 1
            g = grp.get(int(row["flywire_id"]))
            if not g: continue
            t = float(row["t"]); count[g] += 1
            if g not in first or t < first[g]: first[g] = t
    scale = 1000.0 if first and max(first.values()) < 5 else 1.0
    shipped = {g: round(first[g] * scale, 2) for g in first}
    both = next((c for c in pg["conditions"] if c["key"] == "both"), None)
    if both is None:
        fail(msgs, "P2 找不到 both 條件"); return
    r0 = both["runs"][0]
    if r0["total_spikes"] != total:
        fail(msgs, f"P2 種子 1 的總放電 {r0['total_spikes']} ≠ 出貨情境 {total}")
    for g in GROUPS:
        a, b = r0["first_ms"].get(g), shipped.get(g)
        if a != b:
            fail(msgs, f"P2 種子 1 的 {g} 首次放電 {a} ≠ 出貨情境 {b}")


def p3_coverage(pg, msgs):
    """條件數、每格次數、可播檔案,必須與程式碼宣告的一致。"""
    lab = LAB_TS.read_text(encoding="utf-8")
    # 2026-09-17 閘門稽核 S23:原本的正則要求逗號後恰好一個空白,而 lab.ts 是對齊過的,
    # 於是 declared 實測為**空集合**,整個「可播檔案必須存在」的迴圈按建構不可能 FAIL。
    declared = set(re.findall(r"^\s*(\w+):\s*\{\s*bin:\s*'([^']+)',\s*trace:\s*'([^']+)'\s*\}", lab, re.M))
    if not declared:
        fail(msgs, "P3 從 lab.ts 抓不到任何可播條件——正則與程式碼格式脫鉤,這道檢查等於沒跑")
    keys = {c["key"] for c in pg["conditions"]}
    for key, binp, tracep in declared:
        if key not in keys:
            fail(msgs, f"P3 lab.ts 宣告可播條件 {key},但 playground.json 沒有這一格")
        for rel in (binp, tracep):
            f = SCEN.parent / rel.replace("data/", "", 1) if rel.startswith("data/") else ROOT / rel
            if not f.exists():
                fail(msgs, f"P3 可播條件 {key} 的檔案不存在:{rel}")
    n = {len(c["runs"]) for c in pg["conditions"]}
    if len(n) != 1:
        fail(msgs, f"P3 各格次數不一致:{sorted(n)}")
    elif n != {pg["protocol"]["seeds"]}:
        fail(msgs, f"P3 protocol.seeds={pg['protocol']['seeds']} 與實際次數 {sorted(n)} 不符")


def p4_prose_matches(pg, msgs):
    """網頁文案講的「跑過 N 次」必須等於實際次數(覆蓋宣稱重數)。"""
    n = pg["protocol"]["seeds"]
    zh = {"一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9, "十": 10}
    for f in [LAB_TS, ROOT / "README.md", ROOT / "index.html"] + sorted((ROOT / "docs").glob("*.md")):
        if not f.exists(): continue
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for m in re.finditer(r"跑過\s*([一二三四五六七八九十]|\d+)\s*次", line):
                v = zh.get(m.group(1), None) or int(m.group(1)) if m.group(1).isdigit() else zh.get(m.group(1))
                if v != n:
                    fail(msgs, f"P4 {f.relative_to(ROOT)}:{i} 寫「跑過{m.group(1)}次」,實際 {n} 次")
            for m in re.finditer(r"(?:actually )?run (\d+) times", line):
                if int(m.group(1)) != n:
                    fail(msgs, f"P4 {f.relative_to(ROOT)}:{i} 寫「run {m.group(1)} times」,實際 {n} 次")


def check(path=None):
    pg = json.loads((path or PG_PATH).read_text())
    msgs = []
    p1_summary_recomputable(pg, msgs)
    p2_seed1_matches_shipped(pg, msgs)
    p3_coverage(pg, msgs)
    p4_prose_matches(pg, msgs)
    return pg, msgs


def main():
    if "--self-test" in sys.argv:
        base = json.loads(PG_PATH.read_text())
        me = pathlib.Path(__file__).resolve()
        def run(mutate, label):
            v = copy.deepcopy(base); mutate(v)
            with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
                json.dump(v, fh, ensure_ascii=False); tmp = fh.name
            r = subprocess.run([sys.executable, str(me)], env=dict(os.environ, PLAYGROUND_JSON=tmp), capture_output=True, text=True)
            ok = r.returncode != 0
            print(f"  {'✓' if ok else '✗'} {label}: exit {r.returncode}(預期非 0)")
            return ok
        def m_summary(v): v["conditions"][0]["summary"]["total_spikes"]["median"] = 99999
        def m_seed1(v): v["conditions"][0]["runs"][0]["first_ms"]["gf"] = 1.0
        def m_count(v): v["conditions"][0]["runs"].pop()
        def m_seeds(v): v["protocol"]["seeds"] = 99   # P3:protocol 與實際次數脫鉤
        r0 = subprocess.run([sys.executable, str(me)], capture_output=True, text=True)
        print(f"  {'✓' if r0.returncode == 0 else '✗'} 正向:未改動的資料 exit {r0.returncode}(預期 0)")
        res = [r0.returncode == 0,
               run(m_summary, "負向:手改 summary 的中位數"),
               run(m_seed1, "負向:改掉種子 1 的首次放電(與出貨情境脫鉤)"),
               run(m_count, "負向:某一格少跑一次"),
               run(m_seeds, "負向:protocol.seeds 與實際次數不符")]
        print("SELF-TEST", "PASS" if all(res) else "FAIL"); sys.exit(0 if all(res) else 1)

    pg, msgs = check()
    n = pg["protocol"]["seeds"]
    print(f"條件 {len(pg['conditions'])} 格 × {n} 次;summary 由 runs 重算比對;種子 1 對出貨情境;可播檔案存在性")
    for m in msgs: print("  ❌", m)
    print("RESULT:", "PASS" if not msgs else "FAIL")
    sys.exit(1 if msgs else 0)


if __name__ == "__main__":
    main()
