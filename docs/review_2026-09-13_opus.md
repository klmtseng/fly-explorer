# fly-explorer 對抗式審查 — HEAD a61d2e8 (2026-09-13)

## 主線實跑閘門(全部我自己重跑)
tsc --noEmit exit 0 | jargon_lint exit 0 | verify_scenario exit 0 | vite build exit 0

## 逐條宣稱裁決
1 soma.bin 140,024 — 真。獨立重算 Traced+somaLocation=140,024;檔長 1,120,220==28+8n;三軸 scale 全等 3.8867812;extent 729.6/513.9/995.0 µm;voxel_nm_verified:false 已誠實標注。
2 索引對齊/stride — 真。node 重現 soma.ts 抽樣 + applyFrame 映射,7 組參數(含不整除 nAll=140023、nAll=7/max=3)mismatch=0 oob=0。但見 P1-3、P2-1。
3 FLYSCN02 往返 — 真。我自建 4 組負向控制(翻 byte/刪 byte/截尾/補尾)全 exit 1。但見 P1-4。
4 w_syn 相變 — **偽/未支持**。見 P1-1。
5 jargon_lint — 真。自建負向控制(塞 PWM exit 1、清空 glossed exit 1 報 7 處)。但見 P1-4、P2-4。
6 visual_provenance — 部分。見 P2-2。
7 引擎 --stim-ms — 真。HEAD~1 原始碼另編 flysim_old,同參數同 seed:old/new-default/new-explicit-0 三者 md5 全等 d3c384c5…;--stim-ms 25 md5 不同(正向對照,旗標確實有作用)。
8 quality.ts — 真。cyberpunk-room/src/engine/quality.ts 存在 185 行,37-132 確為 PRESETS+GPU 判定;low maxPoints=90000;抽樣非截斷已證。
9 cards.json — 真但有隱藏面。20 卡 id 唯一、欄位齊、雙語非空、30 個 fact 全有 provenance+source、21 measured/9 paper 完全吻合。見 P2-3。

## 額外正面發現(超出交辦)
- runs/build/escape.csv **可 bit-for-bit 重現**:用committed 的 escape.stim 重跑引擎,md5 91ebd9d3… 完全相同。整條情境產線確定性成立。

## P1
P1-1 相變宣稱被自家另一份 committed 資料推翻。verification_log.md:114-123 的表忠實轉錄自 runs/scenarios/g_*.csv(我逐檔數行確認:g_0.275_25=121,592、g_0.24_25=1,747),但 public/data/phase_sweep.json 在**同一個 (w_syn,k) 格**給 146,647 / 117,208 —— w=0.24,k=25 差 **67 倍**,w=0.179,k=25 差 **75 倍**(856 vs 64,174)。兩份都是 trials:1。verification_log.md:140-161 自己已證明此區雙穩態 CV 高達 1.26 並寫下「單次數字一律不得採信」(:159),卻沒回頭撤銷 :123 的「0.275→0.240 有相變」。按 phase_sweep.json,轉折點在 0.15→0.12(21,106→576),0.179 反而在**上方**。修法:撤回「臨界點下方」措辭,改述為可支持的那一條——「本 stim set 實跑總放電僅 6,024,且隨機 311 對照組 GF=0.00」(後者才是真證據)。
P1-2 畫面因果句被自家量測推翻。我從 escape.csv 獨立重算首次放電:DLMn 12.7ms、TTMn 13.7ms、PSI **28.5ms**。故 main.ts:129「翅膀肌跟上／要經過 PSI 轉一手,所以慢一拍」與 public/data/escape.json dlm note「經 PSI 轉一手才到」、psi note「必經中繼」在時序上不可能(DLMn 早 PSI 15.8ms);main.ts:128「跳躍肌先動」也錯(DLMn 早 1ms)。修法:改成「翅膀肌與跳躍肌幾乎同時(12.7/13.7ms),PSI 28.5ms 才放電,本模型中 PSI 不是首波路徑」。
P1-3 main.ts:130「35 ms 內整條路徑走完,剩下的是背景活動」為偽。verification_log.md:229-230 與我的重算一致:DLMn/DVMn 末次放電 **244.9/244.7ms**(t_run 250ms)。把 35-245ms 的模型自產輸出叫「背景活動」是把訊號錯標成雜訊。修法:改「35 ms 內波前抵達所有族群;翅膀肌持續放電至 ~245 ms」。
P1-4 兩支閘門的負向控制組不存在於任何 committed 檔案。`grep -n "負向\|控制組\|negative" docs/*.md scripts/*.py PROGRESS.md CLAUDE.md` **零命中**。宣稱 3/5 我重跑為真,但那是我臨時手搭的,repo 裡沒有可重跑的迴歸案例 —— 違反自家 maintenance.md「機器可判定的升格,不落一支迴歸案例不算升格完成」。修法:verify_scenario.py 與 jargon_lint.py 各加 `--self-test`,把我這四組+兩組固化成永久案例,並印逐項覆蓋率。

## P2
P2-1 手機模式數字失真。low preset stride=2 → applyFrame 丟掉 50% 活躍點(已測:kept=70,012/140,024),而 main.ts:164 把回傳的**繪製數**寫成「本幀 N 顆神經元在放電」—— 那是關於模擬的事實宣稱,手機上系統性低估一半。修法:分開顯示「本幀 N 顆在放電(手機模式顯示其中 M 顆)」,N 由編碼時另存每幀總數。
P2-2 visual_provenance.md 與實作三處不符:(a) :53-60 規定常駐圖例**四行**,index.html:93-97 只有三行,缺「(數字後方標示產生它的腳本)」;(b) :51 硬性規則 4「每個出現在畫面上的數字都要指得出產生它的腳本」—— STAGES 的 126/185/32ms/3ms/13ms/132µm/35ms 畫面上全無腳本標注;(c) :23 規定③的視覺語言是「虛線+流動動畫」,實作只有洋紅**文字色**(index.html:31),而 :50 明令「不得只靠圖例交代」。修法:三選一——補足圖例第四行與數字標注、或把規範降級為「已知未實作」並註明。
P2-3 3/20 張卡 facts 為空(no-spontaneous、vs-mammal、vs-llm),宣稱 9「每個 fact 有 provenance」對它們**空真**。vs-mammal/vs-llm 正是最需要出處的比較性宣稱。修法:jargon_lint 或另一支 lint 加「每卡 facts 非空」斷言。
P2-4 jargon_lint 只掃 content/cards.json,**掃不到真正面向小朋友的前端文案**。main.ts:128 的 STAGES 直接對使用者顯示 BAN 級詞「軸突」(BAN 清單 jargon_lint.py:20),外加未解釋的 LC4/LPLC2/PSI/巨纖維(GLOSS 級)。修法:把 src/main.ts 的 STAGES 抽到 content/ 並納入 lint 掃描範圍。
P2-5 情境載入的斷言是軟的。main.ts:139-140 的 nPoints!==nAll 斷言 throw 後被 :147 的 catch 只 console.warn,使用者看到的是「沒有播放器」而非錯誤。宣稱 2 說「載入時斷言」會被讀成硬閘門。修法:把索引不符與網路失敗分開處理,前者顯示可見錯誤。
P2-6 legend 標籤誇大。soma.ts:14 group 5 標「視葉 / Optic lobe」,但 group_of 只把 `ol_intrinsic`(81,052)歸進去;同屬視葉的 visual_projection 9,162(**含 LC4/LPLC2 本身**)與 visual_centrifugal 563 被塗成「中間神經元」。soma_meta.json 用的是正確的「視葉內在」。修法:前端標籤改「視葉內在」。
P2-7 STAGES 的 t 是幀號被當 ms 用(main.ts:160 `frame >= s2.t`),只因 dtMs==1.0 才巧合成立;且 t 值(0/4/10/14/22/40)是敘事節拍,與它自己引用的量測時刻(3/13/32/35ms)不同步 —— 觀眾在第 10 幀才看到「巨纖維首次放電在 3 ms」,而畫面上巨纖維第 3 幀就亮了。修法:t 改存 ms 並 `frame*dtMs >= t`,節拍對齊量測值。

## P3
P3-1 verify_scenario.py:42 截尾控制組以未捕捉的 IndexError 收場(exit 仍為 1),:34 的守衛只覆蓋 varint 迴圈未覆蓋 brightness byte;且翻 byte 的錯誤訊息說「檔案不完整或格式不符/讀到檔尾就截斷」,對「中段損壞」是誤導性歸因。
P3-2 main.ts:97,99 硬寫 140024/「140,024」而非 cloud.nAll;soma.bin 一重新產生就靜默說謊。
P3-3 index.html CSS:`#legend` 在 :18 設 bottom:14px、:48 設 top:92px,兩者皆未被清除 → 固定定位元素被上下撐開;:24 的 columns:2 被 :48 的 columns:1 覆蓋成死碼;:56 與 :63 兩個相同的 @media(max-width:560px) 可合併。
P3-4 scenario.ts:48 `counts` 寫入後從未讀取(死碼);:52 第一遍掃描的 `dv.getUint32(p)` 在損壞檔上會丟未包裝的 RangeError 而非格式訊息。tsconfig 只 include ["src"] 且未開 noUnusedLocals,掃不到。
P3-5 low preset 只用掉 77.8% 點數預算(stride=2 → 70,012/90,000);改成 90,000 上限的等距取樣可多顯示 28%。
P3-6 export_soma.py:38 `'efferent' in sc` 排在 ascending/descending 之前,故 efferent_ascending(8)、efferent_descending(4) 被歸為「運動」而非「上行/下行」—— 可能是刻意,但 docstring 未說明。
P3-7 escape.csv 欄名 `flywire_id` 實際裝的是 MaleCNS bodyId(build_scenario.py:69 / verify_scenario.py:55 都靠位置 row[2] 讀,功能無誤),命名誤導。
P3-8 .gitignore 有 `build-data/` 但 build-data/soma_ids.bin 實際已被追蹤(verify 能跑靠它)。結果是對的,規則與事實矛盾,新檔會被靜默漏掉。
P3-9 build_scenario.py:19-26 varint() 定義在 import 之前;:51 與 :104 重複 `import pyarrow.feather as f`,:51 那個從未使用。
P3-10 「132 µm」我一度以為無出處,實查有:cards.json:218 給了推導(Z 44,160→60,697,16,537 單位 ×8nm=132.3µm,算術正確)。但它繼承 8nm 未驗證假設,畫面上呈現為硬數字而無「待確認」標記。

## 弱模型(Sonnet 級)最可能誤讀的句子
1. 宣稱 4「在臨界點下方」——會被當成已驗證事實;實則支撐它的表格已被自家另一份資料與雙穩態發現推翻(P1-1)。
2. verification_log.md:232「整條路徑 35 ms 內走完」——同一張表的「末次」欄寫著 244ms。**「走完」指的是波前抵達,不是活動結束**,需改寫。
3. 宣稱 3/5 的「負向控制組都被擋下」——會被讀成 repo 裡有這些測試;實際一個都沒有(P1-4)。
4. 宣稱 9「每個 fact 有 provenance」——對 3 張零 fact 的卡是空真(P2-3)。
5. 宣稱 2「載入時斷言」——實際是被 catch 吞掉的 console.warn(P2-5)。

## 唯讀確認
git status --porcelain: (空)
git rev-parse HEAD: a61d2e8cb332175505d328f7ed1f7ec77cdfc327
所有變異實驗在 scratchpad 副本進行;vite build 只寫 gitignore 的 dist/。
