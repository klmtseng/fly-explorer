# independent_review — validity-audit 第 2 段(2026-09-15)

受審:content/cards.json(33 卡)、content/stages.json、出處鏈。建造者:主線(Claude Fable)。
reviewer:冷審 opus(無提示,未看 ledger)、halo 冷萃取 sonnet、熱審 opus(給發現,任務含攻擊清單本身)。
侷限:三者與建造者同為 Claude 家族;Codex 沙箱不可用,無異質家族複審(記入 ledger)。

## 冷審回報(逐字保存;處置見 content_audit.md §4b)

(a) 問題清單(排序)
1. P1 mushroom-body.more:「61,210 條,佔全腦 1.5 千萬條連線的 0.04%」— 61,210/15,000,000 = 0.41%,差 10 倍;傳到 vs-mammal、vs-llm。verification_log.md:84 全腦邊數 25.6M 與卡片 15M 也不一致。
2. P1 tried-critical-point.more:「0.179 落在安全區」— verification_log.md:179-183 已明文撤回;出貨情境正是 w=0.179。
3. P1 spikes-hz.more + fact 207 Hz:log:133 判定不可當生理量,卡片卻寫「約上限一半」。
4. P1 escape-two-muscles.kid:「所以腿先動…所以翅膀慢一點點」— log:242-243 已撤除;6 ms 版 TTMn 只放電 1 次,1.3 ms 差推因果證據不足。
5. P1 tried-bistable.kid:「每個數字都是跑很多次以後才寫上去的」— 出貨情境單次(escape.csv 只有 trial 0)。
6. P1 escape-two-muscles 全卡 + tried-pulse-length fact + stages.json:34:把運動神經元 TTMn/DLMn 叫成「跳躍肌/翅膀肌」,與 muscle-link「肌肉不在資料裡」相衝。
7. P2 eight-senses.more:「12 類」只列 9 類、加總 14,068,短少 1,844 = unknown_sensory 1707 / (未標) 126 / mechanosensory_tbc 11;kid「八種」與 more「12 類」對不上。
8. P2 headline 3:verify_scenario.py 零次提及 stages.json;沒有任何機器檢查擋字幕時間漂移。
9. P2 stages.json:34 vs never-stops fact:「翅膀肌…跑到 600 ms 它還在」vs 卡片 562 ms。
10. P2 calcium-glow fact 80 ms 標 ● 實為算圖參數;kid「是真的實驗長的樣子」讓小孩以為在看鈣成像實錄。
11. P2 headline 1 破口:153 個內文數字無 provenance;最嚴重「人類膝跳反射 20 到 30 毫秒」「反射弧來回約 1 公尺」全 repo 無出處;why-sudden 的 20 nm / 50 突觸 / −52 / −45 / 7 mV、escape-converge 126/185/6,362/4,862、mushroom-body 4,064/42-45/2.05、neck-gap Z 座標無標記。
12. P2 body-overview 165,122 vs why-fly/whats-next 166,691 無解釋。
13. P2 ◆ 定義被違反:1910 source 自陳「原文未親讀」;7-9 天「經 BioNumbers」轉引;169 Hz/134°/2.83 mm「引 Chen & Sun」。反面:線蟲 302 與 BRAIN CONNECTS 正確標 ○ — 查過,沒問題。
14. P2 jargon_lint.py:50 把 stages 注入時寫死 en:"",英文側恆真。
15. P3 vs-mammal / vs-llm / no-spontaneous facts 為空卻做科學宣稱。
16. P3 vs-llm「沒有前向傳遞的層次結構」與 hex-columns 層狀晶格語氣相衝。
17. P3 calcium-glow.glossed 殘留 ["赫茲","Hz"]。
18. P3 spikes-hz source runs/engine/taskA_real.csv 斷鏈;audit_claims 的 runs/ fallback 應拿掉。
19. P3 出處鏈指向永不公開的 ../fly repo。
20. P3 body-overview.kid zh「十六萬」vs en 165,122。
21. 查過沒問題:motor-map 11 部位加總 815、腿 381;892+879=1,771;60%;454 Hz;13%/70×;CV 1.26 與 22×;714/929=77%;MICrONS/H01/斑馬魚與 research_context_cards 親讀引文吻合;escape-speed 已在審查途中改寫;Ache 2019、Card & Dickinson 2008、von Reyn 2014 出處正確。

(b) 五條 headline:1 不可信;2 大致可信但閘門有洞;3 不可信;4 半可信;5 可信,且是本專案最好的資產——缺口在文件裡的撤回沒有回流到卡片;verification_log.md:459 宣稱 FlyWire 139,255 在卡片上標 ○,該卡實際沒有這條。

(c) 單一最重要修正:寫確定性腳本把 verification_log 的撤回關鍵詞對 cards.json + stages.json grep,命中即 FAIL。先修的單一數字:mushroom-body 0.04%。

## halo 冷萃取(sonnet)摘要
238 條宣稱(數字≈150、來源≈95、全稱≈45、因果≈45),檔 audit/claims_independent.md。
最易被小孩追問的 5 條:三個神經元總數並存;hex「每型恰好一顆」只由總數推;escape-two-muscles 教科書 vs 模擬無橋接;never-stops 對小孩不友善;t=−24 方向待確認。

## 熱審(opus 429 中斷 → sonnet 完成;逐字保存要點)
P1-1 public/data/cards.json + dist/data/cards.json(09-13 手動複製,21/33 卡)含全部撤回句(25 hits);5 支閘門只查 content/。
P1-2 C3「捏造閘門」名不副實:兩支自測都不檢查引用真偽;無機器閘門攔捏造 DOI/標題。
P1-3 verify_stages ENGINE_CONST/PROBE_CONST 是純字面量,加一行就 PASS。
P2-1 escape-speed kid「比人類最快的反射還快」無引註,是刪數字後的定性殘留。P2-2 body-overview zh「十六萬」vs en「about 165,000」。
P2-3 audit_numbers 不認中文數詞。P2-4 hex-columns 標題 1,771 為孤兒推算值。P2-5 三張「誠實說」連續只講不同,整體印象可能變「模擬是假的」。
P3-1 jargon_lint 不掃 more 層(vs-llm LoRA 等超綱)。P3-2 retraction_lint 不掃 question。P3-3 audit_numbers 不含 label/source(誤報)。P3-4 CLAUDE.md:25「141,781」舊值。
查過沒問題:6 張問答卡選項唯一;三支自測負向確實被擋。
(b) 恆真/可繞過:C3 實質恆真;verify_stages 常數表可無限加;retraction_lint question 盲點;五支閘門全只認 content/(壞例子:改乾淨 content/,public/ 舊快照照樣上線)。
(c) 單一最重要修正:刪除/凍結 public 與 dist 的 cards.json,並納入掃描範圍——否則今天所有修正一上線就可能被 09-13 快照蓋回。
MLD:M=只信閘門 PASS,沒去比對被審檔案是不是真的會出貨;L=先審「這份檔案是不是使用者看到的那份」再審內容;D=repo 要有一行機器可查的單一真相 manifest。
