
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
