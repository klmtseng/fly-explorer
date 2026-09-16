# 交接:解說語音(旁白)能力 — 給另一個 session 立項用

寫於 2026-09-15,由 fly-explorer 主線寫。目的:語音是可重用能力,不該埋在果蠅專案裡;
另開專案做成小工具,做完照本檔的接口接回來。**本檔只講需求與已知事實,不指定技術方案。**

## 這邊要的東西(接口合約)

輸入:一段文字 + 聲線設定(哪個聲線、語言 zh/en、語速)。文字來源是 `content/cards.json`(33 卡 × kid/more × zh/en ≈ 130 段,每段 30-60 秒)與 `content/stages.json`(8 段字幕)。
輸出:
1. 音檔:Opus 或 AAC,32-48 kbps,單聲道;檔名 `<card_id>.<layer>.<lang>.opus`(例 `escape-speed.kid.zh.opus`)。
2. 清單 `narration/manifest.json`:每段 `{id, layer, lang, file, duration_s, voice, model, model_version, text_sha256}`。
   `text_sha256` 讓這邊能機器判斷「卡片文字改了、音檔過期」——跟本專案「單一來源、改了就重生」的規矩一致。
3. 一支可重跑的 CLI:`narrate --cards content/cards.json --out narration/ --voice <名>`,重跑只重生 sha 變了的段落。

## 硬限制(使用者定的)

- **免費**:模型與工具零費用;網站端不得有即時合成(流量一大就有算力費)。所以是**本機預算、網站放靜態檔**。
- **公開網站撐得住**:靜態檔走 Vercel CDN;估算 130 段 × 0.4 MB ≈ 50 MB,免費方案每月 100 GB 流量 ≈ 20 萬次播放。
- **聲音要有磁性、有說服力**:這是主觀指標,交接的重點之一是**先定義怎麼量**(見下)。
- **授權**:模型授權至少允許教育/非商業公開使用;聲線來源只准(a)使用者自己錄的參考音,(b)模型內建且授權允許的聲線。**不得複製任何真人的聲音。**
- **本機環境**:CPU-only、**沒有 AVX2**(bitnet.cpp 已判不可跑;PyTorch 類框架可能 Illegal instruction 或極慢)。一次性批次合成若本機跑不動,可用免費雲端筆記本,因為只算一次。
- **iOS**:音訊必須由使用者點擊後才能播(瀏覽器規則),網站端要有「聽解說」鈕,不可自動播。

## 本機已驗證的起點(別重找)

- Kokoro(Apache 2.0)中文/英文 TTS 在本機跑通過:記憶檔 `reference_kokoro_chinese_tts.md`。
- 手機助理專案有台灣腔 TTS 管線:`Projects/a14-assistant`、記憶 `project_samsung_phone.md`。
- 語音工具手冊:`~/Desktop/AI_MAC/docs/voice-tools.md`(whisper/piper/ffmpeg)。
- 響度驗收要跨工具:`ffmpeg volumedetect`,不能只信寫檔那支函式庫(rainforest 教訓,見 judgment-rubrics R5 音訊列)。

## 評估方法(這部分的研究成果可以搬到別的專案)

「磁性/說服力」不能靠自己聽一聽就下結論。建議:
1. 固定同一段文字(取 `escape-speed` 的 kid.zh),讓每個候選聲線各合成一次,檔名盲化。
2. 使用者(以及至少一位小孩)做**配對盲聽**,每對選一個,記下來算勝率;n 小的時候只寫「點估計較佳」,不寫「顯著」。
3. 客觀量測當輔助不當裁判:語速(字/秒)、停頓分布、基頻範圍、響度一致性;先確認它們跟盲聽結果同向再用。
4. 每個候選記錄:模型、版本、授權、本機能不能跑、每段合成秒數。

## 接回來的步驟(這邊要做的)

1. 卡片進網站(M2e)時,每張卡加「聽解說」鈕,讀 manifest 找對應音檔;找不到就不顯示鈕。
2. 語言鈕同時切音檔;小朋友版與教科書版可用不同聲線。
3. 出處規範加一列:旁白是我們唸的(④),稿子=卡片文字,不另外加沒經過審計的內容。
4. 發佈前把 manifest 的 `text_sha256` 對卡片重算一次,過期即 FAIL(跟 retraction_lint 同一層的閘門)。
