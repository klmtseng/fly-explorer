# PROGRESS — fly-explorer

## M0 立項與資料層
- [x] scaffolding + git init + CLAUDE.md
- [x] 匯出 140,024 顆 soma 座標 + superclass 編碼 → `web/data/soma.bin`
- [x] 匯出輸入輸出清冊 → `web/data/io.json`
- [x] 驗證:三視圖投影解剖學正確(docs/soma_verification.png,主線親眼看過)
- [x] 再驗:使用者 iPhone 實機 60 fps(low 檔,抽樣 1/2 = 70,012 點),2026-09-13

## M0.5 視覺管線(2026-09-12 發現後新增)
- [x] 確認 `assignedOlHex1/2` = 視網膜拓樸座標,右 892 / 左 879 柱
- [x] 匯出六角柱座標(`scripts/export_hexmap.py`,官方中心 hex (18,19));**軸向哪邊是正前方未驗**,前奏字幕明寫
- [ ] 房間場景 → 果蠅視點 → 六角格亮度(這段可**即時算**,不需預錄)

## M1 情境錄製
- [x] 逃跑迴路 341 顆神經元座標已匯出(`scripts/export_escape.py` → `public/data/escape.json` 31KB)
      含顆數斷言,數量不符就 exit 1 不產檔
- [ ] 由標註檔導出各情境的刺激神經元集合(糖/苦/逼近/理毛/氣味…)
- [x] 逃跑情境:`scripts/build_scenario.py` → `public/data/scenarios/escape.bin`(FLYSCN02,0.09MB)+ 巨纖維電壓 trace;`verify_scenario.py --self-test`
- [x] 可追溯:每段字幕帶 src,出處三色圖例(發光=資料/洋紅=注入/線稿與琥珀=我們畫的),verification_log 逐項

## M2 內容
- [x] 內容清單 20 張卡 `content/cards.json`(雙語 × 雙層 × 出處標記,結構驗證通過)
- [x] 審閱頁產生器 `scripts/build_review_page.py`(單一來源:改 JSON 不改 HTML)
- [ ] **使用者審閱取捨**(哪些留/砍/改寫)← 卡在這
- [ ] 補卡:模組 D 只有 1 張、C 缺「什麼是突觸」入門卡

## M2.5 技術棧(2026-09-12 定案,環境已實測)
- three.js ^0.170 + postprocessing ^6.36 + Vite ^5.4 + TypeScript(對齊 cyberpunk-room 以便搬程式碼)
- 可直接抄:`cyberpunk-room/src/engine/quality.ts:37-132`(四級降級+GPU 判定)、
  `renderer.ts:79-108`(bloom + AgX;其註解有實測數字證明 AgX 對暗底發光場景較佳)
- 驗收腳本:`reference-repos/repos/threejs-game-skills/.../inspect-threejs-canvas.mjs`
- ⚠️ **vercel token 已失效**,實測 `vercel whoami` 回 not valid,部署前需重跑 device flow。gh 正常(klmtseng)
- ⚠️ 截圖驗收需 `preserveDrawingBuffer: true`,否則 `drawImage(canvas)` 讀回全黑

## M2.6 Vite 骨架 + 點雲(2026-09-12)
- [x] npm 裝妥:three 0.170.0 / postprocessing 6.39.5 / vite 5.4.21 / typescript 5.9.3
- [x] `src/quality.ts` 移植 cyberpunk-room 四級分級 + GPU 簽章判定(欄位換成點雲用)
- [x] `src/soma.ts` 讀 soma.bin → BufferGeometry + 自訂 shader(**brightness 屬性已預留給放電播放**)
- [x] `src/main.ts` OrbitControls + BloomEffect + AgX 色調映射
- [x] **實測渲染 140,024 點,載入 209-502 ms,建置 1.7MB(JS gzip 後 140KB)**
- [x] 主線親眼驗收解剖正確:腦在一端、空脖子在中間、腹神經索在另一端,紅色運動神經元在 VNC
- [ ] ⚠️ **上述截圖是 SwiftShader 軟體渲染**(本機 Chrome WebGL 壞),fps 數字無意義。
      真機驗收未做:需 Firefox(真 GPU)+ 使用者手機
- [ ] 取景還可再收緊;VNC 相對腦部偏暗

## 審查紀錄
- [x] 2026-09-13 opus 對抗審查,P1 全修(`docs/review_2026-09-13_opus.md`)
- [ ] 異質複審(Codex):本機沙箱不可用,使用者裁決延後到發表前;屆時先修 userns

## M2d 模組 A 視覺層 + 實體視窗(2026-09-13 使用者要求)
- [x] 透明外殼(頭/胸/腹、六腳、翅、複眼、口器),**線稿不發光**,比例用實測(CNS 佔體長 36%、空脖子 132µm)
- [x] **實體小視窗(PiP)**:第二個小視口,顯示果蠅身體在現實中會做什麼——
      腿/翅/口器動作由解碼的運動神經元活動驅動,形狀是我們畫的(④),已標示「幅度是示意」
- [x] 肌肉線稿(主畫面):`src/muscles.ts` 琥珀,濃淡隨真實運動神經元放電,bloom 之外不發光(2026-09-14)

## M2e 卡片進網站(下一步;2026-09-14 盤點:21 張卡只存在 content/,網站一個都沒顯示)
- [x] 使用者審閱 33 張卡(2026-09-15,validity-audit 三輪修正後):「審核過了,沒什麼問題,可以作了」
- [x] 雙層切換鈕 + 中英切換鈕(`src/cards.ts` 抽屜;選擇存 localStorage)2026-09-15
- [x] 卡片依階段掛點出「📖」小籤(STAGE_ANCHORS),索引含全部 33 張;問答卡可作答;kid=大字圓角一次一張,more=事實表格 2026-09-15
- [ ] 3D 熱點點擊(觸角/複眼/蘑菇體直接點)——目前走索引
- [ ] 字幕(stages.json)補英文欄位,jargon_lint 已能檢查中英兩份

## 2026-09-14 已完成的視覺/互動層(使用者實機逐項驗收)
- [x] 真實比例+平塗淡色 PiP、歸位/自轉/＋－、可見區域取景、手機面板並排、播放時運鏡推近、上下拍翅、
      我們加的結局(洋紅)、播放列塞進 308px

## M3 發佈
- [ ] pre_public_gate PASS
- [ ] GitHub + Vercel

## 待決 / 風險
- 情境的刺激集合在 MaleCNS 上未必有對應(M2 已知:雄性連接組無糖受器,只有費洛蒙受器)
  → 可能要改用「由資料定義的情境」,像 fly 專案 M2 那樣。**這是最大的未知。**
- **⚠️ 模型沒有自發活動**:不給輸入 = 全腦零放電。所以「果蠅發呆」的畫面腦是全黑的。
  這是真實的模型限制,**要誠實顯示不要假造閒置活動**。可當教學點:
  真果蠅腦一直在自己活動,這個模型不會——差別在哪、為什麼重要。
- **預錄的本質限制**:使用者只能從有限選單挑刺激,不能自由創造。
  「氣味濃度連續變化」「任意光源位置」這類需要即時引擎(WASM)。
  → 前端的播放層與資料層必須切乾淨,之後換引擎不重寫。

- 2026-09-14 M2d 肌肉層 ✓:`src/muscles.ts` 琥珀色線稿(bloom 之外不發光),DLM/DVM/TTM 纖維 + 真實運動神經元細胞體→肌肉連線,濃淡跟真實放電;證據 docs/muscle_layer_2026-09-14.png

## M2f 三分流示意版(2026-09-16 使用者定)
- [x] 首頁三扇門:小朋友版 / 專業版 / 自由探索(記在 localStorage,可 ↩ 換版本)
- [x] 引導版:`content/tracks.json` 13 步(舞台停幀或播一段 + 一張卡),兩版共用骨架只換層與紙;導覽列 上一步/下一步;儀表全收
- [x] 自由探索 = 原畫面;取景把紙(全寬或右欄)與導覽列算進可見區域
- [x] 2026-09-16 引導版改 scrollytelling:舞台釘背後、文字往上捲、捲動進度=鏡頭過渡+播放時間軸、文字塊隨距離淡縮、兩段滿版只留一句
- [x] 2026-09-16 英文版補齊:首頁/圖例/模式鈕/PiP/電壓計/字幕(stages.json en+sub_en)/出處註記/含中文單位的數值(value_en);新閘門 scripts/lang_residue.py(英文版四畫面殘留中文=0,--self-test 負向案例);jargon_lint 掃英文字幕、audit_numbers 掃英文層、verify_stages 兩語數字對帳
- [x] 2026-09-16 自由探索加「字幕」開關(localStorage、?cap=0;關掉只留洋紅角標);手機藏 ＋／－
- [ ] 首頁美術;引導版過場句;手機紙限高後長卡片的可讀性;英文翻譯品質尚未經母語/異質複審(只驗了「無殘留、數字一致、術語有解釋」)
