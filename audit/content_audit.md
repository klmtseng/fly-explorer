# content_audit — fly-explorer 內容層(validity-audit 第 1 段機械審計)

日期 2026-09-15。受審對象:`content/cards.json`(33 卡 / 70 事實)、`content/stages.json`(8 段)、
出處鏈 `docs/verification_log.md`、`docs/research_context_cards.md`。威脅層級:T1(宣稱為假)必跑;
T2 不適用(受審的是內容不是管線;網站本身另計);T3 未被要求,不跑。
每個 PASS 標「恆真」或「可能 FAIL」。

## 0. 釘住的宣稱(第 1 步)

機器清單:`audit/claims.md`(`scripts/audit_claims.py` 產生,exit 0 = 來源欄的本機路徑全部存在)。
口頭對使用者說過、也算宣稱的:
- H1 「每個數字都指得出產生它的腳本或論文;◆ 只給親讀過的來源,二手標 ○」。
- H2 「小朋友層沒有術語、首次出現當場解釋」(`jargon_lint.py` PASS)。
- H3 「字幕時間點全部取自出貨情境」(`verify_scenario.py` PASS)。
- H4 「模型的限制都誠實寫進卡片」。
- H5 「數字不能編;比喻可以簡化」。
halo 差集:另派冷 agent 從交付物獨立萃取宣稱(`audit/claims_independent.md`),差集見 §4。

## 1. 歷史失手強制挑戰(ledger 187 類,只答與內容類相關者;其餘為量化/系統類,不適用)

| 類 | 本專案會不會犯 | 怎麼驗 | 結果 |
|---|---|---|---|
| [2] 捏造/不可查證引用 | 會——20 條 ◆ 事實來自 12 篇文獻 | 逐篇比對 verification_log / research_context_cards 是否有親讀記錄;沒有的主線自己親讀 | **抓到 4 篇無記錄**(Fotowat 2009、Augustin 2019、Card & Dickinson 2008、von Reyn 2014)→ 全部主線親讀補齊;其中 **Fotowat 被誤讀(見 §3 F1)** |
| [3] 恆真句 PASS | 會 | 對每個 PASS 標記 | verify_scenario「位元組全數消耗」是格式檢查(恆真於正確編碼),但「逐點相同」是可 FAIL(self-test 負向控制證明) |
| [12] 覆蓋宣稱未重數 | 「33 張、70 事實、8 段」 | audit_claims.py 機器數 | 33/70/8 ✓(可能 FAIL) |
| [13] meta 旗標造假 | ●/◆/○ 就是旗標 | ◆ 逐條查親讀記錄 | 4 條原本無記錄(同 [2]),二手者已標 ○(線蟲 302、BRAIN CONNECTS、Morgan 1910 原文) |
| [24] 文案錨點未對 live 重驗 | 網站字幕 | verify_scenario 對出貨 escape.bin;stages t 值與 escape.csv 對照在 verification_log §脈衝長度 | ✓ |
| [36] 教學設計本身教錯概念 | 問答卡 5+1 張 | 讀每題正解 | fly-vs-human-vision 正解「量法不一樣不能比」是刻意設計;其餘正解與 more 層一致 |
| [52] 同代模型互審自背書 | 冷審用 opus,建造者 fable;非異質家族 | 記錄 | **侷限:Codex 沙箱壞,本輪無異質家族複審**(與 09-13 相同) |
| [124] 驗證證據不在交付物內 | 卡片 source 指到 ../fly 研究倉(不公開) | 標明 | **P2**:對外發佈後讀者看不到 ../fly/scripts;發佈前要把被引用的腳本或其輸出摘要搬進本倉 |
| [165] 超綱術語 | kid 層 | jargon_lint | PASS(可能 FAIL,self-test 負向控制證明) |
| [167] 宣稱授權但無 LICENSE | CC-BY 資料 | ls LICENSE | **待補**:repo 尚無 LICENSE 檔(M3 發佈項) |
| [168] 量詞誇大 | 「一半的腦都在看」「全腦唯一能改的地方」 | 對數字 | 60% 寫成「超過一半」✓;「唯一」= KC→MBON 可塑突觸為模型中唯一有學習規則者,措辭在 more 層有限定 |

## 2. 領域包 C1–C7

- **C1 覆蓋度**:宣稱「33 張、每張兩層兩語」→ `audit_claims.py` 與 `build_review_page.py` 機器數 33;lint 掃 33 張 × 2 語。PASS(可能 FAIL)。
- **C2 事實正確性**:70 條事實逐條對照出處(§1 [2]);kid/more 文字裡的數字是否超出事實欄 → 由冷審與 halo 差集覆蓋。**抓到 1 條數字誤讀(F1)**。
- **C3 捏造閘門**:`jargon_lint.py --self-test` PASS(負向:塞 BAN 詞 / 移除 glossed 皆 exit 1);`verify_scenario.py --self-test` PASS(4 個負向控制);兩者本批實跑輸出存 `audit/_jargon_selftest.txt`、`audit/_verify_selftest.txt`。閘門版本 = 本 commit。PASS(可能 FAIL)。
- **C4 meta 旗標**:● = 我們的腳本量出;◆ = 主線或查證 agent 親讀原句並留記錄;○ = 二手/示意。逐條查後 4 條 ◆ 補親讀記錄(§1 [2]),0 條需降級。**注意 model_reviewed ≠ human_verified:全部 33 張卡使用者尚未審**(審閱頁已發,裁決未回)。
- **C5 快樂路徑**:內容層不適用;網站互動(問答點選)尚未實作,列入 M2e 驗收條件:答錯路徑要有截圖。
- **C6 可重跑**:`build_review_page.py` 由 cards.json 確定性產生;`build_scenario.py` 常數集中、`verify_scenario.py` import 同一份常數;環境 three 0.170 / vite 5.4.21 記於 PROGRESS。單檔 HTML 審閱頁為維護風險(只記)。
- **C7 版權/來源**:MaleCNS CC-BY 4.0(已標);本站不含 FlyWire 資料(CC BY-NC);卡片引用論文為短句轉述,非整段複製;Wikipedia 文字已改寫;arXiv 論文數字為引用。字型 Google Fonts。無個資。PASS。

## 3. 發現(全部經重現:引文逐字、檔案行號)

- **F1 P1(會教錯)** `content/cards.json` 卡 `escape-speed`:原寫「從看到東西到飛走只要 18 毫秒」、事實欄 `18 ms 視覺刺激→起飛 ◆ Fotowat 2009`。
  親讀 PMC3817277:「a single spike on average 18 ms (SD = 1.5 ms) after the lights went off」——18 ms 是**燈熄→巨纖維放電**;
  「TO occurred on average 25 ms (SD = 2 ms) after the light-off stimulus」——起飛是 25 ms;逼近刺激下「TO occurred 6 ms (SD = 11 ms) after the angular size reached 54°」。
  **已修**:標題與兩層改寫,事實欄拆成 18 / 25 / 6 ms 三條,均附親讀。膝跳反射對照保留但降級為數量級對照。
- **F2 P2** 14 條事實的 source 寫成本倉相對路徑(如 `../fly/scripts/io_inventory.py` 原寫 scripts/io_inventory.py),而該腳本在 `../fly/scripts/`(研究倉),本倉不存在——`audit_claims.py` 第一次跑 18 條 MISSING。**已修**:來源欄改成 `../fly/scripts/…`,checker 認 ../fly。**殘留 P2(發佈前)**:研究倉不公開,對外讀者無法追;M3 前要把被引用腳本(io_inventory / shuffle_csr / escape_path / mb_circuit_stats)或其輸出複製進本倉。
- **F3 P2** 4 篇 ◆ 文獻在兩份記錄檔皆無親讀記錄(Fotowat、Augustin、Card & Dickinson、von Reyn 2014)。**已修**:主線經 Europe PMC / PMC 全文 / bioRxiv 全文親讀,原句記於本檔 §3 與來源欄。
- **F4 P3** `stages.json` t=−24 的 src 指到外部 repo 文件,原寫法像本機路徑。**已修**:寫明 github.com/reiserlab/… 外部。
- **F5 P3(侷限,不修)** 本輪冷審 reviewer 與建造者同為 Claude 家族;Codex 沙箱不可用。發表前仍需異質複審(與 09-13 審查同一未決項)。

## 4. 獨立審查(第 2 段)— 冷審 / halo 差集 / 熱審

### 4a. halo 差集(冷萃取 agent,sonnet,未看審計表;`audit/claims_independent.md`,238 條)
差集裡進了本輪的:三個神經元總數無對照(→ F7 已修)、hex「每型恰好一顆」只由總數推(→ F6 逐柱重數後改)、
escape-two-muscles 結構/動態無橋接(→ F10 + 熱修改寫)、t=−24 方向未驗(維持誠實標示,列 M3 前必解)。
其餘 U 型全稱句(如「所有從腦發出的命令都要擠過這裡」「果蠅是第一個被完整重建的成年動物腦」)逐條讀過:
前者由解剖結構必然(頸連結是唯一通道),後者與 research_context_cards §2 一致(線蟲是幼小無脊椎、幼蟲非成年)。

### 4b. 冷審(opus,無提示;21 項)— 逐條重現後的處置
| # | 冷審發現 | 重現 | 處置 |
|---|---|---|---|
| 1 | 0.04% 算術錯、傳三卡 | 重跑 mb_circuit_stats:61,210 邊 / 463,640 突觸;61,210/25.6M = 0.24% | **已修**(F8);分母改官方 25.6M 並寫明 |
| 2 | 「0.179 落在安全區」已被 log:179-183 撤回仍在卡上 | `sed -n 179,183p` 逐字確認 | **已修**:改寫成「引爆與否取決於刺激集合」;加進 retracted.json |
| 3 | 207 Hz 當生理量(log:133 禁止) | 確認 | **已修**:明寫模型值/相對指標 |
| 4 | 「腿先動因為翅膀轉手」(log:242-243 已撤除) | 確認 | **已修**:kid 改寫,跳躍與翅膀幾乎同時;加進 retracted.json |
| 5 | 「每個數字都跑很多次」假全稱(出貨動畫單次) | log:296 確認 | **已修**:限定為速率型數字 |
| 6 | TTMn/DLMn 被叫成肌肉 | 確認 | **已修**:事實標籤、字幕、PiP 讀數改「運動神經元/…神經」 |
| 7 | 感覺 12 類只列 9 類,少 1,844(恰是「不知道」那欄) | `io_inventory.json` sensory.by_class 逐項加總 = 15,912 | **已修**:補列 1,844 並定義「八種感覺」 |
| 8 | verify_scenario 不讀 stages.json,字幕時間無閘門 | `grep stages scripts/verify_scenario.py` 零命中 | **已修**:新 `scripts/verify_stages.py`(首/末次放電 + 列明常數,兩個負向自測) |
| 9 | 字幕「600 ms 翅膀肌還在」vs 卡片 562 ms | log:314 | **已修**:字幕改「全腦到 600、翅膀肌神經到 562」 |
| 10 | 80 ms 標 ● 實為顯示參數;kid「真的實驗長的樣子」 | render_glow_test.py 是算圖參數 | **已修**:改 ○ 顯示參數;kid 明說亮暗是模擬算的 |
| 11 | 153 個內文數字無標記;膝跳反射 20-30 ms / 1 m 零出處;偵測器「每顆約 50 突觸」 | grep 全 repo 無出處;11,222/311 = 36 | **已修**:膝跳數字刪除改定性;50→36 並加事實;−52/−45 補 ◆ Shiu。內文數字全面加標記列 M2e(卡片進站時 fact 欄逐數綁定) |
| 12 | 165,122 vs 166,691 無解釋 | 同 halo | **已修**(F7) |
| 13 | ◆ 定義被違反:1910 原文未親讀、7-9 天轉引、169 Hz 引 Chen & Sun | source 欄自曝 | **已修**:1910 → ○;7-9 天來源改 BDSC 親讀;◆ 定義寫進 cards.json note(親讀所引文件,轉引寫明) |
| 14 | jargon_lint 對字幕 en 掃空字串=恆真 | `scripts/jargon_lint.py:51` | **已修**:缺 en 時印「英文側未檢查,不算 PASS」 |
| 15 | 三卡 facts 空卻做科學宣稱 | 確認 | **已修**:補 ○/●(走路一年、自發活動、0.24%) |
| 16 | 「沒有前向傳遞的層次」vs 視葉層狀 | 確認 | **已修**:改「不是只有前饋層次」 |
| 17 | calcium-glow glossed 殘留 | 確認 | **已修** |
| 18 | taskA_real.csv 斷鏈;audit_claims 的 runs/ fallback | 確認 | **已修**:改 ../fly/runs/engine;fallback 拿掉 |
| 19 | 出處指向永不公開的研究倉 | 同 F2 殘留 | **M3 前必做**:搬腳本/輸出進本倉 |
| 20 | body-overview kid zh「十六萬」vs en 165,122 | 確認 | **已修**:en 改 about 165,000 |
| 21 | 查過沒問題清單(motor-map 加總、892+879、60%、454 Hz、13%/70×、CV 1.26、77%、MICrONS/H01、Ache/Card/von Reyn) | 主線抽驗 motor-map 加總與 77%、52% 皆親算 | ✓ |
冷審對五條 headline 的判定:H1 不可信 → 修後「事實欄 80 條全可追,內文數字綁定列 M2e」;H2 大致可信(en 側字幕待補);
H3 不可信 → 新閘門後可信;H4 半可信 → 三個撤回句回流後可信;H5 可信。
冷審單一最重要修正=「撤回沒回流」→ 已機制化:`content/retracted.json` + `scripts/retraction_lint.py`(自測負向擋住)。

### 4c. 熱審(opus 因 session 額度 429 中斷 → 改派 sonnet;給了以上發現,任務:比喻/因果句 + 攻擊清單本身)
| # | 熱審發現 | 重現 | 處置 |
|---|---|---|---|
| P1-1 | 舊快照 public/data/cards.json(已 git rm,現在不存在才是正確狀態)(09-13 手動快照,21 卡)含 25 處撤回句,五支閘門只查 content/ | ls + 對該檔跑 retraction_lint.scan = 25 hits;`grep cards.json src/` 零命中(網站未讀它,但 Vite 會原樣發佈) | **已修**:`git rm`;`audit_claims.py` 加「單一真相」斷言(public/、src/ 下不得有 cards/stages 副本);dist 重建後無此檔 |
| P1-2 | C3「捏造閘門」名不副實:自測的是術語與編碼,引用真偽無任何機器閘門 | 讀兩支腳本確認 | **已修一半**:新 `scripts/citation_record_lint.py`(◆ 事實的引用鍵必須在親讀記錄檔出現;自測負向擋住)——它驗「有記錄」不驗「論文為真」,C3 措辭改為此;論文為真仍靠人親讀 |
| P1-3 | verify_stages 的常數表是純字面量,可無限加 | 讀 `scripts/verify_stages.py` | **已修**:每個常數的數字字串必須在 verification_log 出現,否則 import 即 assert 失敗 |
| P2-1 | escape-speed kid「比人類最快的反射還快」是刪掉數字後殘留的定性結論 | 確認 | **已修**:改成眨眼對照並標 ○ 常識 |
| P2-2 | body-overview kid zh「十六萬」無 hedge、與 en 不等價 | 確認 | **已修**:「大約十六萬五千」 |
| P2-3 | audit_numbers 不認中文數詞 | 實跑 | **已修**:中文數詞轉阿拉伯數字;抓到 why-fly「八百六十億」無事實欄 → 補 Azevedo ◆ |
| P2-4 | 1,771 是推算值無事實欄 | audit_numbers 孤兒 | **已修**:hex-columns 加 1,771 = 892 + 879 事實 |
| P2-5 | 三張「誠實說」連續只講不同,小孩可能以為模擬是假的 | 判斷題 | **已修**:三卡 kid 開頭加「先說什麼是真的…」平衡句 |
| P3-1 | jargon_lint 不掃 more 層,vs-llm 的 LoRA/目標函數超綱 | 確認 | **不修,記錄**:more 層定位「想知道更多」本就允許術語;超綱與否列 M2e 使用者審閱 |
| P3-2 | retraction_lint 不掃 question | 確認(現況乾淨) | **已修**:question 併入 |
| P3-3 | audit_numbers 不含 label/source → 誤報 | 實跑 | **已修**:label+source 納入;孤兒 8 → 3(54.8 萬=548,000、114.9=114.88、1,771 已有事實,人審無誤) |
| P3-4 | CLAUDE.md:25「141,781」第四個舊總數 | grep 唯一一處 | **已修**:140,024 並註明 141,781 是去重前匯出數 |
熱審對閘門的攻擊結論(採納):①C3 恆真 → 拆成「術語/編碼有負向控制」與「引用記錄閘門」兩件事;
②常數表可無限加 → 常數須有 log 記錄;③question 盲點 → 補;④閘門只認 content/ → 單一真相斷言。
熱審查過沒問題:6 張問答卡選項唯一對應;三支自測負向確實被擋。

## 5. 結案判定

- **T1 宣稱為假**:五條 headline 修後狀態——H1(每個數字可追、◆=親讀)**可信但有明確邊界**:事實欄 82 條全部有路徑或親讀記錄(兩支機器閘門),
  內文數字對事實欄/記錄的機器比對剩 3 條人審通過的近似值;◆ 定義已寫進資料檔。H2 **可信(zh)/未檢查(en 字幕)**。H3 **可信**(新閘門 + 自測)。
  H4 **可信**:三個撤回句已回流並機制化。H5 **可信**。
- **本輪撤回/降級**:18 ms→拆三數字;0.04%→0.24%;「14 型恰好一顆」→12 型附比例;安全區/腿先動/上限一半 三句撤;80 ms ●→○;
  1910 ◆→○;膝跳反射與「人類最快反射」刪;207 Hz 標模型值。**發現 22 條,P1 8 條,全部先重現再修,無一未重現即寫入。**
- **硬限制(不可修,明列)**:①reviewer 與建造者同家族,無 Codex 異質複審;②卡片尚未經使用者審閱(model_reviewed ≠ human_verified);
  ③出處指向不公開研究倉,M3 前須搬入;④字幕 en 欄未建,英文側未受檢;⑤t=−24 六角座標方向未驗;⑥T3(教學是否有效)未跑。
- **判定:內容層 T1 通過(修正後),可進入使用者審閱;不可直接發佈**(受②③⑤與 M3 閘門約束)。
- 閘門實跑輸出:`audit/_gates_2026-09-15.txt`;reviewer 原文:`audit/independent_review.md`;ledger 已 append 10 筆。

## 5. 結案判定

(待 §4 完成。)

### 3b. 第 1 段續(halo 差集 + 機器數字檢查後新增)

- **F6 P1(會教錯)** 卡 `hex-columns`:原寫「14 種細胞型每型在每根柱子裡恰好一顆(各型總數 1,732-1,773)」。
  逐柱重數(`audit/_hex_per_column.txt`):12 種在 96.7-99.8% 的柱子恰好一顆 ✓,但 **L3 = 892、C2 = 874 顆**,只在約一半的柱子有座標
  (右眼 892 柱 → 疑為標註只給了一側)。原句對兩型為假。**已修**:改列 12 種、附比例;L3/C2 註明原因未定。
  來源:`CLAUDE.md`「每型每柱恰好一顆」那句也是同一個未經逐柱驗證的推論(從總數≈柱數推的)→ 同步改。
- **F7 P2(可誤讀)** 站上三個「神經元總數」並存:標題 140,024、卡片 165,122、166,691,無對照(halo 冷萃取抓到)。
  三者各自正確(論文口徑 / 完整追蹤 / 有細胞本體座標),差額 25,098 幾乎全是感覺神經元(`CLAUDE.md:22`)。
  **已修**:`body-overview` more 層三個數字並列說明,事實欄加 140,024 ●。
- **F8 P1(數字錯)** 卡 `mushroom-body`/`vs-mammal`/`vs-llm`:「61,210 條可塑**突觸**…佔全腦 1.5 千萬條連線的 **0.04%**」。
  重跑 `../fly/scripts/mb_circuit_stats.py`(`audit/_mb_stats.txt`,46 s):KC→MBON **61,210 條邊 / 463,640 個突觸**。
  61,210 是連線數不是突觸數;61,210 / 15.27M = 0.40%、/ 25.6M(官方邊數)= 0.24%——原文 0.04% 是分母混用 152M 原始列。
  **已修**:「61,210 條連線(463,640 個突觸)」,比例改 0.24%(分母 25.6M,Berg 2026),三張卡同步。
- **F9 P3** 卡 `escape-converge`:LPLC2→巨纖維寫 4,862;由出貨 `public/data/escape_edges.json` 重算為 **4,860**(LC4 6,362 ✓)。**已修**為可重現值並改來源。
- **F10 P3** 卡 `escape-two-muscles` 的「與教科書完全吻合」加「結構上」,與同卡後段「動態不同」銜接(halo 提出)。
- 機器檢查:`scripts/audit_numbers.py` prose 數字孤兒 24 → 8(其餘 8 條為四捨五入/衍生和/同卡事實已含,逐條人審無誤)。
