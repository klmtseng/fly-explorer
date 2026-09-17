#!/usr/bin/env python3
"""引文接地閘門:每一條「文獻說 X」都必須逐字對得上原文(確定性)。

這是評估系統裡唯一不靠判斷的那一段。它把
    「模型說這篇論文不同意你」
變成
    「這是那篇論文的第 N 個字元起的那一句」。

規則:`audit/sci_records.json` 的每一筆審查記錄,若 verdict 不是 unverifiable,
就必須帶 source(pmid/pmcid/doi)與 quote,而 quote **正規化後必須出現在抓回來的原文裡**。
正規化只碰排版:NFKC、破折號與引號統一、空白收斂——不碰任何實詞,
所以「Gaussian function」寫成「linear function」一定對不上。

原文快取放 `audit/sources/`(**不進版控**:論文全文有著作權,本倉不轉散布)。
版控裡留的是 source id、quote、抓回來那份文字的 sha256 與日期、命中位移,
別人重抓一次就能重驗。

用法:
  python3 scripts/verify_quotes.py --fetch     # 抓缺少的原文進快取(要連網)
  python3 scripts/verify_quotes.py             # 離線逐字比對
  python3 scripts/verify_quotes.py --self-test
exit 0 = 每一條引文都逐字對得上,非 0 = 有對不上或缺快取。
"""
import hashlib, json, pathlib, re, subprocess, sys, unicodedata, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
REC = pathlib.Path(__import__("os").environ.get("SCI_RECORDS", ROOT / "audit/sci_records.json"))
CACHE = ROOT / "audit/sources"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
DASH = dict.fromkeys(map(ord, "‐‑‒–—−―"), "-")
QUOTE = {ord("’"): "'", ord("‘"): "'", ord("“"): '"', ord("”"): '"', 0xAD: None}


def norm(s: str) -> str:
    """只做排版正規化。實詞一個字都不許動——不然這道檢查就不是逐字比對了。"""
    s = unicodedata.normalize("NFKC", s).translate(DASH).translate(QUOTE)
    return re.sub(r"\s+", " ", s).strip()


def source_key(src: dict) -> str:
    for k in ("pmcid", "pmid", "doi"):
        if src.get(k):
            return f"{k}-{re.sub(r'[^A-Za-z0-9._-]', '_', str(src[k]))}"
    raise ValueError("記錄缺 source id")


def fetch(src: dict) -> str:
    """Europe PMC:OA 全文優先,否則退回摘要。抓不到就讓它失敗,不編。"""
    def get(url, args=()):
        r = subprocess.run(["curl", "-s", "-G", url, *args], capture_output=True, text=True, timeout=120)
        return r.stdout
    if src.get("pmcid"):
        xml = get(f"{EPMC}/{src['pmcid']}/fullTextXML")
        if len(xml) > 2000:
            return re.sub(r"<[^>]+>", " ", xml)
    ident = f"EXT_ID:{src['pmid']}" if src.get("pmid") else f"DOI:{src['doi']}"
    js = get(f"{EPMC}/search", ["--data-urlencode", f"query={ident}",
                                "--data-urlencode", "format=json", "--data-urlencode", "resultType=core"])
    try:
        res = json.loads(js)["resultList"]["result"]
    except Exception:
        return ""
    if not res:
        return ""
    r = res[0]
    return re.sub(r"<[^>]+>", " ", " ".join(filter(None, [r.get("title"), r.get("abstractText")])))


def load():
    if not REC.exists():
        return []
    return json.loads(REC.read_text(encoding="utf-8"))["records"]


def check(records, do_fetch=False, quiet=False):
    CACHE.mkdir(parents=True, exist_ok=True)
    bad = []
    for r in records:
        rid = r.get("claim_id", "?")
        if r.get("verdict") == "unverifiable":
            if r.get("quote"):
                bad.append((rid, "標成 unverifiable 卻帶引文——要嘛查得到要嘛別引"))
            continue
        if not r.get("quote") or not r.get("source"):
            bad.append((rid, "verdict 不是 unverifiable,卻沒有 source 或 quote")); continue
        key = source_key(r["source"])
        f = CACHE / f"{key}.txt"
        if do_fetch and not f.exists():
            txt = fetch(r["source"])
            if len(txt) < 200:
                bad.append((rid, f"抓不到原文({key})")); continue
            f.write_text(txt, encoding="utf-8")
        if not f.exists():
            bad.append((rid, f"快取缺 {f.relative_to(ROOT)},先跑 --fetch")); continue
        raw = f.read_text(encoding="utf-8")
        digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
        pos = norm(raw).find(norm(r["quote"]))
        if pos < 0:
            bad.append((rid, f"引文不在原文裡({key});這條引用不成立")); continue
        if r.get("source_sha256") and r["source_sha256"] != digest:
            bad.append((rid, f"原文換版了(記錄 {r['source_sha256']} vs 現在 {digest}),引文需重驗")); continue
        r["_pos"], r["_sha"] = pos, digest
        if not quiet:
            print(f"  ✓ {rid} {key} @{pos} 「{r['quote'][:58]}…」")
    return bad


def main():
    if "--self-test" in sys.argv:
        import tempfile, os
        tmp = pathlib.Path(tempfile.mkdtemp())
        (CACHE).mkdir(parents=True, exist_ok=True)
        fake = CACHE / "pmid-999999999.txt"
        fake.write_text("A model summing a linear function of angular velocity and a "
                        "Gaussian function of angular size replicates GF looming response dynamics.", encoding="utf-8")
        cases = [
            ("正向:引文逐字命中", [{"claim_id": "t1", "verdict": "contradicted", "source": {"pmid": "999999999"},
                                    "quote": "a Gaussian function of angular size"}], True),
            ("負向:把 Gaussian 換成 linear(本評估要抓的錯誤型別)",
             [{"claim_id": "t2", "verdict": "contradicted", "source": {"pmid": "999999999"},
               "quote": "a linear function of angular size"}], False),
            ("負向:有 verdict 沒引文",
             [{"claim_id": "t3", "verdict": "supported", "source": {"pmid": "999999999"}}], False),
            ("負向:標 unverifiable 卻帶引文",
             [{"claim_id": "t4", "verdict": "unverifiable", "quote": "whatever"}], False),
            ("正向:排版差異(全形括號/彎引號/破折號)不算不同",
             [{"claim_id": "t5", "verdict": "supported", "source": {"pmid": "999999999"},
               "quote": "a Gaussian  function of angular   size"}], True),
        ]
        ok = []
        for label, recs, want_pass in cases:
            bad = check(recs, quiet=True)
            good = (not bad) if want_pass else bool(bad)
            ok.append(good)
            print(f"  {'✓' if good else '✗'} {label}" + ("" if good else f" → {bad}"))
        fake.unlink(missing_ok=True)
        print("SELF-TEST", "PASS" if all(ok) else "FAIL")
        sys.exit(0 if all(ok) else 1)

    records = load()
    if not records:
        print(f"FAIL:{REC} 沒有任何審查記錄"); sys.exit(1)
    bad = check(records, do_fetch="--fetch" in sys.argv)
    if "--fetch" in sys.argv:
        for r in records:
            if r.get("_sha"):
                r["source_sha256"] = r["_sha"]
                r.setdefault("fetched_on", datetime.date.today().isoformat())
        out = {"note": "每條引文都由 scripts/verify_quotes.py 逐字對過原文;原文快取在 audit/sources/(不進版控)。",
               "records": [{k: v for k, v in r.items() if not k.startswith("_")} for r in records]}
        REC.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{len(records)} 條記錄,對不上 {len(bad)}")
    for rid, m in bad:
        print("  ❌", rid, m)
    print("RESULT:", "PASS" if not bad else "FAIL")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
