# Design System — fly-explorer(果蠅腦教育網站)

建立 2026-09-15,由 /design-consultation 產生:競品研究(NASA Space Place、BrainPOP、BrainFacts 3D、FlyWire Codex)+ 三方提案(主線、Codex、Claude 子代理)+ 使用者以真字型預覽逐項裁決。
預覽頁:`~/.gstack/projects/fly-explorer/designs/design-system-20260915/preview.html`(已發佈為 artifact 16e59188)。

## Product Context
- **What this is:** 把 MaleCNS 真實果蠅腦連接組(140,024 顆有座標的神經元)做成 3D 互動網站,重播模擬的逃跑反射;33 張說明卡雙層雙語。
- **Who it's for:** 國小到國中生,以及他們的家長與老師。
- **Space/industry:** 兒童科普 / 神經科學教育。同類:NASA Space Place(兒童、暗底亮徽章)、BrainPOP(K-6 edtech、青白平面)、BrainFacts 3D brain(成人、白底臨床)、FlyWire Codex(研究工具、深藍)。
- **Project type:** 互動教育網站(3D 舞台 + 內容抽屜),手機直式 308px 為主要裝置。

## 北極星(每個設計決定都要服務它)
**你看到亮起來的,是一顆真的腦在算。**
→ 發光的是資料,不發光的是我們畫的。設計把這條規範直接做成材質:**發光的住在黑底,不發光的印在紙上。**

## Aesthetic Direction
- **Direction:** 標本劇場 + 一張紙(Specimen theatre + paper)。上層是永不改變的黑色舞台;下層是一張紙,兒童版是「探索票」,教科書版是「圖鑑頁」。兩套皮膚只換那張紙與上面的字,不碰腦。
- **Decoration level:** intentional — 紙有極淡的橫紋(repeating-linear-gradient 1.8% 黑)、短硬陰影(0 −6px 0 rgba(0,0,0,.35))、墨線分段。沒有漸層、沒有裝飾圖示、沒有吉祥物。
- **Mood:** 兒童版=小孩手上拿著一張剛撕下來的探索票,興奮、暖、大字;教科書版=翻開一本圖鑑,安靜、密、可信。
- **Reference sites:** spaceplace.nasa.gov、brainpop.com/science、brainfacts.org/3d-brain、codex.flywire.ai。

## 硬約束(先於一切美學)
1. **舞台固定 `#080A0D`**(現站 `#07090a` 系),皮膚色不得染到腦、不得改光。
2. **四個保留色只在舞台與圖例出現,UI 不得用:** 發光綠 `#8fe3a8`(真資料)、洋紅 `#C8629E`(注入/我們加的)、琥珀 `#E8A34A`(神經→肌肉)、冷灰 `#9AA8C4`(我們畫的身體)。功能分色模式的族群色(`#2eff6e`/`#ff3b24`/`#ffa021`/`#2fd8ea`)同列。
3. **手機 308px 直式**是驗收基準;桌機紙在右欄 400px。
4. 科學正確性不因皮膚放寬:卡片文字與數字來自 `content/cards.json`,皮膚只換排版。

## Typography(全部 Google Fonts,2026-09-15 逐一確認可載入)
### 兒童「探索票」
- **Display(中文標題、問句):** Huninn 粉圓體 400 — 台灣製的圓體,友善但不是卡通;不用合成粗體。
- **Display(英文標題、大數字):** Bricolage Grotesque 800 — 有個性、不幼稚,國中生不會覺得被當小孩(R4)。
- **Body:** Noto Sans TC 400/500/600。
- **Scale(手機):** 問句 26/34 · 步驟數字 40/40 · 內文 17/28 · 選項 16/24 · 註 14/21。
### 教科書「圖鑑頁」
- **Display(章節標題):** Noto Serif TC 700。
- **Body:** Noto Sans TC 400。
- **英文、控制項、數字:** Source Sans 3 400/600。
- **Scale(手機):** 章節 23/32 · 小標 18/27 · 內文 16/27 · 圖說與參考文獻 14/22 · 控制項 14/20。密度靠層級,不靠縮中文字。
### 共用
- **Data/標記/時鐘:** IBM Plex Mono 400/500(現站已用;tabular 數字)。
- **Loading:** `https://fonts.googleapis.com/css2?family=Huninn&family=Bricolage+Grotesque:wght@600;800&family=Noto+Sans+TC:wght@400;500;700&family=Noto+Serif+TC:wght@500;700&family=Source+Sans+3:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap`;每個字族都要有 PingFang TC / Noto Sans TC / system-ui 後備。

## Color
- **Approach:** restrained per skin — 每套皮膚一個冷色動作色 + 一個暖紅強調色,其餘是紙與墨。色是稀有的、有意義的。
### 兒童「探索票」W1 午後陽光(使用者三選一)
| Token | Hex | 用途 |
|---|---|---|
| `--paper` | `#F6E3BE` | 票面紙 |
| `--card` | `#FFF8E8` | 選項卡面、輸入 |
| `--ink` | `#3A2614` | 主文字(暖棕,不用近黑) |
| `--muted` | `#7C5D3C` | 次要文字、步驟標 |
| `--act` | `#3B6FD9` | 動作:按鈕、已選、焦點 |
| `--mark` | `#D2452B` | 強調:步驟數字、答對、蓋章 |
紙的邊框 `#E0C79A`。W2 烤麵包(#F2D8B6/#2F5F8F/#C4442A)與 W3 杏桃(#F9E3CD/#2F55C9/#DF5A2E)為未採用的替代,留在預覽頁。
### 教科書「圖鑑頁」
| Token | Hex | 用途 |
|---|---|---|
| `--paper` | `#EDE8DF` | 頁邊 |
| `--card` | `#FAF7F0` | 頁面 |
| `--ink` | `#25221E` | 主文字 |
| `--muted` | `#686057` | 圖說、參考文獻 |
| `--act` | `#243D83` | 連結、控制項、焦點 |
| `--mark` | `#862F36` | 圖號、章節標籤 |
分隔線 `#D9D2C4`、頁頂線 `#C9C1B2`。
### Neutrals
暖灰系(紙→墨):`#FAF7F0` `#EDE8DF` `#D9D2C4` `#C9C1B2` `#686057` `#25221E`。舞台側的文字用暖米白 `#c9cbc4`,不發光。
### Semantic
答對=`--mark` 文字 + 「答對了」字樣與勾號;答錯=`--act` 外框 + 「再想想」;**不得借用綠光或琥珀當成功/警告色**。錯誤/警告訊息用 `--mark`。
### Dark mode
舞台永遠是暗的;紙沒有暗模式(那會回到「資料與說明糊在一起」的問題)。系統暗色偏好只影響本頁 UI 邊框亮度,不影響皮膚。

## Spacing
- **Base unit:** 4px。
- **Density:** 兒童 comfortable;教科書 compact-by-hierarchy。
- **Scale:** 2xs(2) xs(4) sm(8) md(16) lg(24) xl(32) 2xl(48)。
- **手機版面(308px):** 標題列 44px / 舞台 280px / 紙。兒童紙:外邊距 12px、內距 16px → 文字寬 252px,紙頂往舞台疊 12px;選項最低 48px 高、直立堆疊。教科書頁:滿寬、內距 16px → 文字寬 276px、方角、與舞台齊平。
- **桌機:** 紙為右欄 400px,舞台佔其餘。

## Layout
- **Approach:** composition-first — 一個主角(舞台)、一張紙、左對齊閱讀、動作直立堆疊。
- **Grid:** 手機單欄;桌機舞台 + 右欄。
- **Max content width:** 紙內文字 252–276px(手機)、~360px(桌機)。
- **Border radius:** 兒童票角 4px;教科書頁 0;按鈕 4px;不用統一大圓角(那是 AI 味)。
- **切換皮膚:** 舞台與播放時刻不動,只換紙。

## Motion
- **Approach:** minimal-functional — 壯觀屬於重播本身。
- **Easing:** enter(ease-out) exit(ease-in) move(ease-in-out)。
- **Duration:** 紙升起 200ms;答題回饋 150ms;reduced-motion 直接切換。

## 兩套皮膚各自的規則
| | 探索票(kid) | 圖鑑頁(more) |
|---|---|---|
| 一次幾張 | 一張,步驟數字 01/02… | 連續頁,章節與圖號「圖 3.2」 |
| 問答 | 選項直立、答完才給解釋 | 題目與解釋並列 |
| 數字 | 大字卡 + ●◆○ 符號,出處收起 | 表格:數值/說明/標記/出處 |
| 圖示 | 無;PiP 線畫果蠅是唯一角色 | 無 |
| 計數器(R3) | 「你剛剛看到真的神經細胞放電 ✓ 1,204 次」 | 「n = 1,204 spikes · t = 0–14 ms」 |
| 出處 | 符號一定給 | 逐條參考文獻,懸掛縮排 |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-09-15 | 舞台固定暗、皮膚只換紙 | 發光資料在白底會死;三方(主線/Codex/子代理)結構一致 |
| 2026-09-15 | 兒童版取 W1 午後陽光 | 使用者要求「再溫暖一些」,三種暖度預覽後選 W1 |
| 2026-09-15 | 無吉祥物、無圖示 | 不跟兒童網站擠可愛;可愛從問句與字型來;PiP 果蠅是唯一角色 |
| 2026-09-15 | 共用即時放電計數器 | 北極星變成看得到的證據;數字本來就有(每幀 nActive) |
| 2026-09-15 | 保留色不當 UI 色 | 沿用 docs/visual_provenance.md;兩套強調紅都停在紅橘,不進琥珀 |
