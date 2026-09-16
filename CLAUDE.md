# fly-explorer — 給小孩看的果蠅腦互動網站

立項 2026-09-12。從 [[project_fly]] 分出的**對外副專案**:把 MaleCNS 連接組與自建 LIF 引擎的
成果,做成國小到國中生看得懂的互動網站,目標發佈到 GitHub + Vercel。

## 為什麼要分開 repo

`Projects/fly/` 是 local-only 研究倉,含 1.1GB 連接組原始資料與 279MB 打亂 CSR 進了 git 歷史。
**那個 repo 永遠不轉 public**(對應 judgment-rubrics R5 pre-public 閘門 2:要開源就開新 repo)。
本 repo 從第一個 commit 就以公開為前提寫,只放衍生資料與前端程式碼。

## 已定案的三個決策(2026-09-12 使用者裁決)

| 決策 | 選擇 | 影響 |
|---|---|---|
| 模擬方式 | **預錄劇本播放** | 本機跑好情境 → 壓縮成資料檔 → 網頁只負責播放與打光。無後端。 |
| 年齡定位 | **雙層切換** | 「小朋友 / 想知道更多」兩個模式共用同一份內容骨架 |
| 語言 | **中英雙語切換** | 所有文案抽到語言檔,不得寫死在元件裡 |
| 配色 | **情境切換配色,預設科學版(GCaMP 綠)** | 不同感覺用不同色,但預設忠於真實鈣成像 |

架構上要讓「之後換成 WASM 即時引擎」不需重寫前端:播放層與資料層切乾淨。

## 我們有、別人沒有的東西

1. **140,024 顆神經元的真實三維座標(2026-09-15 更正:141,781 是去重前的匯出數,出貨 soma.bin 為 140,024)**(`somaLocation`,標註檔內,已驗證非空)
2. **一台跑得動的 LIF 引擎**(`../fly/engine/flysim`,C,零依賴;研究倉不公開,卡片引用的量測腳本已複製到 `scripts/fly/`,2026-09-16)
3. **完整的輸入輸出清冊**(`../fly/runs/io_inventory.json`)
4. **★ 視網膜拓樸圖**:標註檔的 `assignedOlHex1/2` 給出複眼的六角柱座標。
   **右眼 892 柱 / 左眼 879 柱**(23,720 顆柱狀神經元)。每根柱子中位 27 顆神經元,
   且 L1/L2/L3/L5/Mi1/Mi4/Mi9/Tm1/Tm2/Tm9/Tm20/C2/C3/T1 **每型每柱恰好一顆**
   (各型計數 1,732-1,773 ≈ 柱數)——這是果蠅視葉的晶格結構,教科書級正確。
   → 可以做「小眼 ↔ 腦內柱」的真實對應,不是示意圖。

所以網站上亮起來的是**真的那顆腦在真實解剖位置上的真實模擬輸出**,不是示意動畫。
這是核心價值主張,任何簡化都不能把它稀釋掉。

## 紀律

- **寫任何動畫程式碼前先讀 `docs/visual_provenance.md`**(視覺出處規範)。
  核心規則:**資料會發光,我們畫的東西不發光**。連接組裡沒有肌肉/翅膀/身體,
  畫面上所有身體動作都是我們加的,必須用線稿而非發光表現。
  且模型的視覺前端是斷的,「眼睛看到→偵測器啟動」那一步是注入的,必須標示。
  已落地的分色(2026-09-14):外殼冷灰線稿;**肌肉與神經→肌肉連線琥珀**(連接組沒有這段);
  **前奏與結局洋紅**(注入/我們加的);只有發光的是資料。新畫任何東西先決定它屬於哪一色。
- **科學正確性不因為受眾是小孩而放寬。** 比喻可以簡化,數字不能編。
  每個出現在網站上的數字都要指得出產生它的腳本。
- 資料授權 **CC-BY 4.0**(MaleCNS),網站必須顯著標示出處與 Berg et al. 2026 引用。
- 對外發佈(GitHub/Vercel)前跑 `~/.openclaw/workspace/scripts/pre_public_gate.sh`,PASS 才推。
- 本機 Chrome WebGL 壞,**3D 驗收一律用 Firefox**(見 reference_machine_graphics_env)。

## Skill routing

When the user's request matches an available skill, invoke it via the Skill tool. When in doubt, invoke the skill.

Key routing rules:
- Product ideas/brainstorming → invoke /office-hours
- Strategy/scope → invoke /plan-ceo-review
- Architecture → invoke /plan-eng-review
- Design system/plan review → invoke /design-consultation or /plan-design-review
- Full review pipeline → invoke /autoplan
- Bugs/errors → invoke /investigate
- QA/testing site behavior → invoke /qa or /qa-only
- Code review/diff check → invoke /review
- Visual polish → invoke /design-review
- Ship/deploy/PR → invoke /ship or /land-and-deploy
- Save progress → invoke /context-save
- Resume context → invoke /context-restore
- Author a backlog-ready spec/issue → invoke /spec

## Design System
Always read DESIGN.md before making any visual or UI decisions.
All font choices, colors, spacing, and aesthetic direction are defined there.
Do not deviate without explicit user approval.
In QA mode, flag any code that doesn't match DESIGN.md.
（本專案補充:DESIGN.md 的四個保留色規則與 docs/visual_provenance.md 是同一條,兩邊都要對。）
