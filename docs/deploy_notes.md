
## vercel.json 的快取設定(2026-09-16)

- `/assets/*`:`max-age=31536000, immutable`。檔名帶內容雜湊,改內容一定換檔名,可以永久快取。
- `/data/*`:`max-age=86400` + `stale-while-revalidate=604800`。資料檔換情境才會變。
- 原本全站是 Vercel 預設的 `max-age=0, must-revalidate`,每次重新整理都要往返一趟。

**踩過的雷**:第一版在 `vercel.json` 裡用 `"//"` 當註解鍵,本機 `json.load()` 過得去,
Vercel 直接 `Invalid vercel.json - should NOT have additional property "//"`,**部署從那一刻起全部失敗**,
而線上仍服務舊版本,表面上看不出來。vercel.json 不吃註解;驗它不能只驗 JSON 合法,要看部署狀態。

## 不同步到公開倉的檔案(2026-09-16)

開發倉用 `git ls-files` 匯出到 `fly-explorer-public`。以下檔案**留在開發倉,不進公開倉**,
匯出後要自己刪掉或事先排除:

- `docs/promo_drafts.md`:社群宣傳草稿與 LinkedIn 合規預審,屬內部工作文件。
- `docs/promo/`:社群宣傳圖與動畫(1.5 MB),行銷資產,不是網站的一部分。

匯出指令後接一行清理:
```bash
git ls-files -z | tar --null -T - -cf - | tar -xf - -C "$PUB"
rm -rf "$PUB/docs/promo_drafts.md" "$PUB/docs/promo"
```

## 閘門掃不到的讀者表面(2026-09-18)

使用者在手機上看 GitHub 才發現:**repo 的 description 還是中文,而且帶著已撤回的那句「真的腦在算」**。
閘門一支都碰不到它:那句話不在任何檔案裡,它在 GitHub 的中繼資料裡。

發佈前要人工看一遍的表面,列在這裡(沒有腳本能代勞):

- GitHub repo 的 **description / homepage / topics**(`gh repo view <repo> --json description,homepageUrl,repositoryTopics`)
- Vercel 專案設定裡的名稱與網域
- 社群平台上已經發出去的貼文與配圖(改了站上的說法,舊貼文不會跟著改)
- artifact / 簡報這類已經送出去的副本

**順帶抓到的四處**:把那句話加進 `content/retracted.json` 之後,閘門立刻報出
`DESIGN.md` 的北極星、`content/tracks.json` 的**首頁大標**(訪客讀到的第一句,中英都還是舊版)、
以及中文宣傳主圖的標題(`scripts/build_promo_images.py`)。
`content/tracks.json` 會漏掉,是因為內容層掃描只看 cards 與 stages;現在整個 `content/*.json` 都掃,
而 `content/retracted.json` 自己豁免(它按定義含有每一句撤回句)。

教訓與 9/17 那輪同型,第四次:**閘門守得住的,只有它掃描集合裡的東西。**
新增一個讀者看得到的表面時,第一個問題是「哪支閘門掃得到它」。
