# 獨立宣稱萃取(唯讀,不查證,不看審計表)

來源:content/cards.json(33 卡)、content/stages.json、index.html #prov + PiP。
類型:數字=N、全稱=U、因果=C、來源=S(一句話常同時具多種性質,取主要+次要)。
zh/en 不一致的另列「en差異」欄註記。

| 卡/位置 | 層 | 宣稱原句(逐字) | 類型 |
|---|---|---|---|
| body-overview | kid | 果蠅比一粒米還小,可是牠腦裡有十六萬個神經細胞。 | N |
| body-overview | kid | 這些細胞佔了牠身體長度的三分之一。 | N |
| body-overview | kid(en差異) | en: "packs 165,122 nerve cells" — zh 用約數「十六萬」,en 用精確數 165,122 | N |
| body-overview | more | 中樞神經系統沿身體前後軸長 995 微米 | N |
| body-overview | more | 果蠅體長約 2,500-3,000 微米 | N |
| body-overview | facts | 165,122 神經元(scripts/io_inventory.py) | N |
| body-overview | facts | 995 µm 神經系統全長(scripts/export_soma.py) | N |
| body-overview | facts | 36% 佔體長比例(scripts/export_soma.py)——與 kid 的「三分之一」(≈33%)不同 | N |
| antenna-soma | kid | 在觸角上!感覺細胞的身體長在觸角、眼睛和腳毛上,只把一條細線伸進腦裡報告。 | U |
| antenna-soma | more | 掃描的體積裡,中央腦的感覺神經元細胞本體是 0/4,868,腹神經索 2/6,365,而其他類別都有 90-100%。 | N |
| antenna-soma | more | 昆蟲的感覺神經元本體在周邊感覺器官,只有軸突進入中樞。 | U |
| antenna-soma | facts | 0 / 4,868 腦內感覺神經元有細胞本體(scripts/export_soma.py) | N |
| eight-senses | kid | 我們學過五種感覺。果蠅有八種——多了知道自己身體在哪裡的感覺、感覺溫度的、還有專門感覺空氣濕度的。 | N |
| eight-senses | more | 15,912 顆感覺神經元分成 12 類:視覺 4,107、嗅覺 2,639、觸覺 2,558、一般機械感覺 1,733、本體感覺 1,454、味覺 1,428、濕度 66、化學 58、溫度 25。 | N |
| eight-senses | facts | 15,912 感覺神經元(scripts/io_inventory.py) | N |
| eight-senses | facts | 66 濕度感覺神經元(scripts/io_inventory.py) | N |
| optic-lobe | kid | 果蠅腦裡超過一半的細胞只做一件事:看。 | N |
| optic-lobe | more | 視葉 89,390 顆 + 視覺投射神經元 9,201 顆,佔 165,122 顆的 60%。 | N |
| optic-lobe | more | 視覺處理在昆蟲身上是壓倒性的資源投入。(單一隻果蠅的測量被推廣為「昆蟲」通則) | U |
| optic-lobe | facts | 89,390 視葉神經元(scripts/io_inventory.py) | N |
| neck-gap | kid | 頭和胸之間有一段完全沒有細胞的空隙,長 132 微米——大約是一根頭髮的兩倍寬。 | N |
| neck-gap | kid | 所有從腦發出的命令都要擠過這裡。 | U |
| neck-gap | more | 腦的細胞本體到 Z=44,160 為止,腹神經索從 Z=60,697 開始,中間 16,537 個單位(約 132 µm)全是通過的軸突束。 | N |
| neck-gap | more | 巨纖維的巨大軸突就在其中。 | S |
| neck-gap | facts | 132 µm 沒有細胞本體的長度(scripts/export_soma.py) | N |
| motor-map | kid | 六隻腳加起來 381 條,最多。翅膀只有 67 條——拍翅膀的動作簡單,走路才複雜。 | N/C |
| motor-map | more | 815 顆運動神經元分布 11 個部位:腹部 214、前腳 135、後腳 130、中腳 116、口器 67、翅膀 67、脖子 44、平衡棒 16、其他 26。 | N |
| motor-map | more | 翅膀那 67 顆裡,24 顆接到真正拍動翅膀的動力肌,其餘多是控制翅膀角度的轉向肌 | N |
| motor-map | more | 文獻若只數動力肌會得到比較小的數字。 | S |
| motor-map | more | 分類由節段、出神經與肌肉名三者交叉判定,不是人工歸類。 | S |
| motor-map | facts | 815 運動神經元(scripts/io_inventory.py) | N |
| motor-map | facts | 381 控制腳的(scripts/io_inventory.py) | N |
| wing-beat | kid | 起飛的時候,果蠅翅膀一秒拍大約 170 下,每一下前後掃過 134 度。 | N |
| wing-beat | kid | 靜止的時候翅膀平平地疊在背上。 | U |
| wing-beat | kid | 小視窗裡的果蠅比例照真的畫:翅膀差不多跟身體一樣長。 | S |
| wing-beat | more | 數字來自起飛空氣動力學研究所引用的量測:翅長 2.83 mm、平均翅弦 0.85 mm、拍翅 169 Hz、拍幅 134° | N/S |
| wing-beat | more | 拍動的方向我們畫成以上下為主(拍翅面相對身體傾斜 55°),這個角度沒有出處 | S |
| wing-beat | more | 真果蠅懸停時拍翅面接近水平,起飛與前飛時傾斜。 | U |
| wing-beat | facts | 169 Hz 起飛拍翅頻率(paper, arXiv:1504.04484 引 Chen & Sun) | N |
| wing-beat | facts | 134° 拍幅(paper, arXiv:1504.04484) | N |
| wing-beat | facts | 2.83 mm 翅長(paper, arXiv:1504.04484) | N |
| wing-beat | facts | 55° 我們畫的拍翅面傾角(todo,src/shell.ts STROKE_TILT,自陳「無出處」) | N/S |
| hex-columns | kid | 複眼上每一個小格子,腦裡都有一根對應的柱子在處理它看到的東西。右眼 892 根,左眼 879 根。 | N/U |
| hex-columns | more | 每根柱子中位 27 顆神經元,而 L1、L2、Mi1、Tm1 等 14 種細胞型,每型在每根柱子裡恰好一顆(各型總數 1,732-1,773,對上總柱數 1,771)。 | N/U |
| hex-columns | more | 這是一個晶格:同一份微電路複製 1,771 次平行處理整個視野。 | U |
| hex-columns | facts | 892 / 879 右眼/左眼柱數(annotation assignedOlHex1/2) | N |
| hex-columns | facts | 27 每柱神經元中位數(annotation assignedOlHex1/2) | N |
| spikes-hz | kid | 神經細胞之間傳的每個訊號都一模一樣大,所以沒辦法用大小表達強弱。 | U/C |
| spikes-hz | kid | 牠們改用「一秒發幾次」來表達——發得越密就是越強烈。 | C |
| spikes-hz | more | 這叫速率編碼,等同電子學的脈衝頻率調變。 | S |
| spikes-hz | more | 模型的不應期是 2.2 毫秒,所以理論上限約 454 赫茲。 | N/C |
| spikes-hz | more | 我們量到 MN9 在 207 赫茲,約上限一半;移除抑制性連線後衝到 308,那不是更活躍,是失控。 | N/C |
| spikes-hz | facts | 207 Hz MN9 放電率(measured, runs/engine/taskA_real.csv) | N |
| spikes-hz | facts | 2.2 ms 不應期(paper, Shiu et al. Nature 634 2024) | N |
| calcium-glow | kid | 科學家真的看得到腦在發光。他們讓神經細胞裝上一種蛋白,細胞一活躍就會發綠光 | U/C |
| calcium-glow | kid | 這個畫面不是我們想像的,是真的實驗長的樣子。 | S |
| calcium-glow | more | 鈣螢光指示劑(如 GCaMP)把離散的脈衝累積成連續的亮度,再慢慢衰減。 | S |
| calcium-glow | more | 我們的亮度模型用同一個物理:每次放電 +1,以 80 毫秒指數衰減。 | N/S |
| calcium-glow | facts | 80 ms 螢光衰減時間常數(measured, scripts/render_glow_test.py) | N |
| shuffle-control | kid | 完全傳不到。我們試了三次,每次都把連線打亂但保持每顆細胞連的數目一樣——訊號一次都沒有到達終點。 | N/U |
| shuffle-control | kid | 所以重要的不是「連幾條」,是「連到誰」。 | C |
| shuffle-control | more | 保度數虛無模型:反覆交換兩條邊的終點,使每顆神經元的出度、入度與權重分布逐一完全不變。 | S/U |
| shuffle-control | more | 真實連接組下 MN9 是 207.00 赫茲,三個打亂版本都是 0.00。 | N |
| shuffle-control | more | 網路並沒有死(仍有 24-29 萬次放電),只是訊號再也到不了該到的地方。 | N/C |
| shuffle-control | facts | 207.00 → 0.00 Hz 真實→打亂(measured, scripts/shuffle_csr.py) | N |
| shuffle-control | facts | 0.388% 打亂後保留的原始連線(measured, scripts/shuffle_csr.py) | N |
| no-spontaneous | kid | 如果什麼刺激都不給,畫面上的腦是全黑的——一個訊號都沒有。 | N/U |
| no-spontaneous | kid | 真的果蠅不是這樣,牠的腦隨時都在自己活動。 | U |
| no-spontaneous | more | 模型沒有自發活動,每一個脈衝都能往回追到被刺激的那幾顆神經元。 | U/S |
| no-spontaneous | more | 這讓因果關係乾淨(看到的活動一定來自刺激),代價是失去了真實腦的背景動態。 | C |
| never-stops | kid | 刺激只給了 6 毫秒,可是腦裡的活動一路響到我們把模擬關掉為止:跑到 600 毫秒還在。 | N |
| never-stops | kid | 真的果蠅不會這樣,牠飛一陣子會停。 | U |
| never-stops | kid | 播放到 250 毫秒之後那段「慢慢暗下來、翅膀收回去」是我們加的結局,不是模擬算出來的,畫面上用洋紅色標出來。 | S |
| never-stops | more | 全腦放電每 50 ms 維持 500-600 次(約 1-2 Hz 自持),翅膀肌最後一次放電 562 ms,活動不歸零。 | N |
| never-stops | more | 模型沒有自發活動(不給輸入全黑),但一旦點燃也沒有機制讓它停:沒有適應、沒有把迴路關掉的抑制回路。這兩點真果蠅都不是這樣。 | U/S |
| never-stops | facts | 599.8 ms 最後一次放電(measured, docs/verification_log.md) | N |
| never-stops | facts | 562 ms 翅膀肌最後放電(measured, docs/verification_log.md) | N |
| escape-converge | kid | 兩顆,左右各一。311 個偵測器全部接到牠們身上。 | N/U |
| escape-converge | kid | 這兩顆叫巨纖維,是全腦最粗的神經——粗才傳得快。 | S/C |
| escape-converge | more | LC4(126 顆)與 LPLC2(185 顆)全數連到 DNp01,分別貢獻 6,362 與 4,862 個突觸。 | N/U |
| escape-converge | more | 文獻上 LC4 編碼逼近速度、LPLC2 編碼視角大小,巨纖維把兩者線性整合後決定要不要發放。 | S/C |
| escape-converge | facts | 311 → 2 收斂比(measured, scripts/escape_path.py) | N |
| escape-converge | facts | LC4=速度, LPLC2=大小(paper, Ache et al. 2019) | S |
| escape-two-muscles | kid | 巨纖維直接接到跳躍的肌肉,所以腿先動。但它沒有直接接到翅膀肌肉——中間要經過另一顆細胞轉一手,所以翅膀慢一點點。 | C |
| escape-two-muscles | kid | 不過在我們的模擬裡,那顆轉手細胞(叫 PSI)從頭到尾沒放電,翅膀的訊號走了另一條路。 | N |
| escape-two-muscles | kid | 畫面照模擬畫,所以你看到的跟教科書不完全一樣。 | S |
| escape-two-muscles | more | 巨纖維→TTMn(跳躍肌)2 條邊 90 個突觸,是直連;巨纖維→DLMn(翅膀下壓肌)0 條邊,必須經過 PSI(巨纖維→PSI 4 條邊,PSI→DLMn 10 條邊 449 個突觸)。這與教科書描述的 GF→PSI→DLMn 完全吻合。 | N/S |
| escape-two-muscles | more | 出貨情境的模擬裡 PSI 完全沒放電(最強的早期輸入是抑制性的),翅膀下壓肌 DLMn 首波 15.7 ms 走 LC4→DNp03→AN19B001→DLMn 這條路(AN19B001→DLMn 權重 +802/+672)。 | N |
| escape-two-muscles | more | 教科書的 GF→PSI→DLMn 含電突觸,本模型只有化學突觸、GF→PSI 僅 16 個突觸,PSI 被驅動得又弱又慢。 | S/C |
| escape-two-muscles | facts | 90 巨纖維→跳躍肌突觸(measured) | N |
| escape-two-muscles | facts | 0 巨纖維→翅膀肌直連(measured) | N |
| escape-two-muscles | facts | 15.7 ms 模擬裡翅膀肌首次放電,走 AN19B001(measured) | N |
| escape-two-muscles | facts | 0 次 PSI 在本情境的放電(measured) | N |
| muscle-link | kid | 這張腦地圖畫的是神經細胞和它們之間的連線。肌肉不在裡面,神經細胞接到肌肉的那個接點也不在。 | U |
| muscle-link | kid | 畫面上琥珀色的肌肉和線是我們畫的,只有它們亮起來的時間是真的——來自 26 顆管肌肉的神經細胞什麼時候放電。 | N/S |
| muscle-link | more | MaleCNS 標註了 815 顆運動神經元,但資料集裡沒有肌肉、也沒有神經肌肉接合。 | N/U |
| muscle-link | more | 我們用 24 顆 DLMn/DVMn 與 2 顆 TTMn 的真實細胞體座標當連線起點,濃淡跟著它們逐幀的放電 | S |
| muscle-link | more | 肌纖維的位置與走向是教科書示意,哪顆神經元接哪條纖維也是同側輪流分派,不是逐條對應。 | S |
| muscle-link | facts | 26 連線起點:真實運動神經元(measured, scripts/export_edges.py) | N |
| muscle-link | facts | 0 資料集裡的肌肉(measured, scripts/io_inventory.py) | N |
| escape-speed | kid | 從看到東西到飛走,果蠅只要 18 毫秒——眨一次眼的十分之一。 | N |
| escape-speed | kid | 人類的膝跳反射大概要 20 到 30 毫秒,而那還只是敲一下就踢,中間完全沒有思考。 | N/U |
| escape-speed | more | 果蠅在我們完成一個單突觸反射的時間裡,跑完了光轉換、1,771 根柱子的平行運算、運動特徵抽取、決策與起飛。 | C |
| escape-speed | more | 兩個祕訣:體型(果蠅 3 毫米,人類膝反射弧來回約 1 公尺),以及最後兩跳用電突觸(間隙連接)直接導電,跳過了化學突觸的延遲。 | N/C |
| escape-speed | more | 註:兩個數字量的終點不同(起飛 vs 肌電訊號),不宜直接比大小。(自我警示,仍與 kid 的並列比較並存) | S |
| escape-speed | facts | 18 ms 視覺刺激→起飛(paper, Fotowat et al. 2009) | N |
| escape-speed | facts | 0.93 ms 巨纖維→跳躍肌(paper, Augustin et al. 2019) | N |
| escape-is-decision | kid | 你可能以為這麼快一定是「碰到就跳」的反射。其實不是 | U |
| escape-is-decision | kid | 果蠅有兩種逃法,一種快但亂,一種慢 0.2 秒但會先擺好姿勢決定往哪逃。牠會選。 | N/C |
| escape-is-decision | more | 三個證據:①巨纖維線性整合速度與大小兩路輸入後才跨閾值;②反應會習慣化,重複刺激後衰減、有自發恢復、可被新刺激去習慣化;③短模式與長模式由巨纖維相對於平行迴路的放電時序決定,而且巨纖維可以否決進行中的長模式,強制切成短跳。 | C |
| escape-is-decision | facts | ~200 ms 長模式的準備期(paper, Card & Dickinson 2008) | N |
| escape-is-decision | facts | 兩種模式,由放電時序選擇(paper, von Reyn et al. 2014) | S |
| model-vs-real | kid | 真果蠅的巨纖維到跳躍肌只要 0.93 毫秒,因為那兩個細胞之間是「直接通電」的。 | N/C |
| model-vs-real | kid | 我們的模型每一步都固定要 1.8 毫秒,而且沒有做直接通電這件事——所以模型跑完那一步,比真果蠅跑完整段還慢。 | N/C |
| model-vs-real | more | 巨纖維與下游是混合突觸:化學突觸加上由 Shaking-B innexin 構成的間隙連接。 | S |
| model-vs-real | more | 我們的模型只有化學突觸,而且延遲是一個常數,所以結構上不可能比 1.8 毫秒快。這不是參數沒調好,是模型裡缺了那個機制。 | C/S |
| model-vs-real | facts | 1.8 ms 模型每個突觸的固定延遲(paper, Shiu et al. 2024) | N |
| model-vs-real | facts | Shaking-B 構成間隙連接的蛋白(paper, Augustin et al. 2019) | S |
| mushroom-body | kid | 果蠅大部分的腦是「出生就接好、一輩子不變」的。只有一個小地方可以改,叫蘑菇體 | U |
| mushroom-body | kid | 牠靠那裡記住「這個味道上次讓我不舒服」。 | S |
| mushroom-body | more | 可改變的突觸是 KC→MBON 的 61,210 條,佔全腦 1.5 千萬條連線的 0.04%。 | N |
| mushroom-body | more | 學習規則反直覺:KC 與該區室的多巴胺神經元同時活躍時,那條突觸被壓抑而非增強——學習是雕刻不是堆疊。 | C |
| mushroom-body | more | 另外兩顆 APL 神經元對全部 4,064 顆 KC 做回饋抑制,權重高達 42-45(全腦平均 2.05),強制只有約 5% 同時活躍。 | N/C |
| mushroom-body | facts | 61,210 可塑突觸(measured, scripts/mb_circuit_stats.py) | N |
| mushroom-body | facts | 0.04% 佔全腦連線比例(measured, scripts/mb_circuit_stats.py) | N |
| why-fly | kid | 因為牠剛剛好。夠簡單,所以科學家能把每一條線都畫出來;又夠複雜,牠會看、會聞、會飛、會記住事情。 | C/U |
| why-fly | kid | 人腦有八百六十億個神經細胞,現在還畫不完。 | N/U |
| why-fly | more | 果蠅是第一個被完整重建的成年動物腦。 | U |
| why-fly | more | MaleCNS 包含腦與腹神經索,166,691 顆神經元全部經過人工校對與標註,而且免費公開(CC-BY 4.0)。 | N/U |
| why-fly | more | 它的價值不只在果蠅本身:它是第一次有機會檢驗「知道全部接線,能不能解釋行為」這個問題。 | S |
| why-fly | facts | 166,691 完整重建的神經元(paper, Berg et al. 2026)——**與 body-overview/eight-senses/optic-lobe 等卡使用的 165,122 不同數字**,且與頁面 title「140,024」又不同 | N |
| why-fly-history | kid | 科學家從 1910 年就開始養果蠅做研究,到現在超過一百年。 | N |
| why-fly-history | kid | 牠好養、長得快(最快 7 天就從卵變成大人)、腦又小到可以用顯微鏡一片一片切完。 | N/U |
| why-fly-history | kid | 人類生病相關的基因,每 100 個裡有 77 個在果蠅身上找得到對應的。所以研究牠,常常也是在研究我們自己。 | N/C |
| why-fly-history | more | 1910 年 Morgan 發表果蠅白眼突變的性連鎖遺傳(Science 32:120-122),果蠅從此成為遺傳學的主力。 | N/C |
| why-fly-history | more | 世代時間在 25°C 約 9 天、28-29°C 最快 7 天。 | N |
| why-fly-history | more | 1993 年 Brand 與 Perrimon 的 GAL4/UAS 系統讓人能在任何一群指定細胞裡開關基因。 | N/U |
| why-fly-history | more | 腦約十萬到十六萬顆神經元,小到能用電子顯微鏡逐片切完再重建整顆腦。 | N |
| why-fly-history | more | Reiter 等人 2001 年比對 929 個人類疾病基因,714 個(77%)在果蠅基因組找得到同源序列。 | N/S |
| why-fly-history | facts | 1910 Morgan 的果蠅遺傳學論文(paper;source 自陳「引文經 FlyBase FBrf0000547 核對,原文未親讀」——二手轉引) | N/S |
| why-fly-history | facts | 7-9 天 卵到成蟲 28°C/25°C(paper,Bloomington 頁 + Ashburner 經 BioNumbers 100521,二手轉引) | N/S |
| why-fly-history | facts | 1993 GAL4/UAS 系統(paper, Brand & Perrimon 1993) | N/S |
| why-fly-history | facts | 77% 人類疾病基因在果蠅有同源 714/929(paper, Reiter et al. 2001,摘要親讀) | N/S |
| vs-mammal | kid | 最大的差別不是大小,是「有沒有在學」。果蠅腦幾乎整顆都是天生接好的,牠一出生就會飛、會逃、會理毛。 | U |
| vs-mammal | kid | 我們出生時幾乎什麼都不會,全部要學——連走路都要學一年。 | U |
| vs-mammal | more | 哺乳類皮質的可塑性是分散在整個結構裡的,而果蠅把可塑性集中在 0.04% 的一小塊。 | N/C |
| vs-mammal | more | 這是兩種不同的賭注:果蠅賭「環境夠可預測,先天接線就夠用」,哺乳類賭「環境難預測,值得花時間學」。兩種都活了幾億年。 | U/C |
| fly-vs-human-vision | kid | 科學家研究猴子的腦,是量腦表面的面積:大約一半是管視覺的。 | N/S |
| fly-vs-human-vision | kid | 人類沒有人算出一個總數,只知道最主要的視覺區佔腦表面大約 2%。 | U/N |
| fly-vs-human-vision | kid | 數顆數和量面積是兩種尺,所以沒辦法說誰比較多。但三種動物都告訴你同一件事:看東西是腦裡超級大的工程。 | C/U |
| fly-vs-human-vision | more | 果蠅:視葉 89,390 顆 + 視覺投射神經元 9,201 顆,佔 165,122 顆的 60%(神經元顆數,我們量的)。 | N |
| fly-vs-human-vision | more | 獼猴:「以視覺為主或純視覺的皮質佔皮質表面積約一半(52%)」(Van Essen 2003,皮質面積,講的是獼猴)。 | N/S |
| fly-vs-human-vision | more | 人類:初級視覺皮質 V1 約 21 cm²、佔大腦皮質 2.2%,沒有全部視覺相關皮質的總百分比。 | N/S |
| fly-vs-human-vision | more | 人腦神經元總數 861 ± 81 億(Azevedo et al. 2009)。 | N/S |
| fly-vs-human-vision | facts | 60% 果蠅視覺神經元佔比(measured) | N |
| fly-vs-human-vision | facts | 52% 獼猴視覺皮質佔皮質面積(paper,自陳「講獼猴非人類」) | N/S |
| fly-vs-human-vision | facts | 2.2% 人類 V1 佔大腦皮質面積(paper) | N/S |
| fly-vs-human-vision | facts | 861±81 億 人腦神經元總數(paper, Azevedo et al. 2009) | N/S |
| vs-llm | kid | AI 的本事存在「數字」裡,那些數字是訓練出來的。果蠅的本事存在「接線」裡,那些線是演化出來的。AI 可以重新訓練變成別的樣子,果蠅不行——牠的線改不了。 | C/U |
| vs-llm | more | 硬接線連接組相當於凍結的基礎模型,蘑菇體相當於掛上去的一層 LoRA(0.04% 的可訓練比例,數量級上真的接近),多巴胺神經元相當於訓練訊號。 | S |
| vs-llm | more | 比喻有兩處會走鐘:果蠅腦沒有前向傳遞的層次結構,它是遞迴動力系統;而且它沒有目標函數——那個目標在演化裡,不在腦裡。 | U/S |
| whats-next | kid | 第一個被完整畫出來的是一種小線蟲,只有大約 300 顆神經細胞,1986 年就完成了。 | N |
| whats-next | kid | 然後是果蠅的幼蟲,再來是成年的果蠅——先是雌的,現在是這隻雄的。 | N |
| whats-next | kid | 小鼠和人類的腦太大,目前只畫完一小塊,大概一粒沙那麼大的立方體。 | U |
| whats-next | more | 線蟲 C. elegans 302 顆(White et al. 1986);果蠅幼蟲 3,016 顆神經元、54.8 萬突觸(Winding et al. 2023);成年雌果蠅 FlyWire 約 13-14 萬顆(Dorkenwald et al. 2024);雄果蠅全中樞神經系統 166,691 顆(Berg et al. 2026,本站資料)。 | N/S |
| whats-next | more | 局部:小鼠視皮質 1 mm³ MICrONS 約 12 萬顆神經元、5.23 億突觸(2025);人類顳葉 1 mm³ H01 約 5.7 萬顆細胞、1.5 億突觸(Shapson-Coe et al. 2024)。 | N/S |
| whats-next | more | 進行中:斑馬魚幼魚全腦(2017 年已有全腦電顯資料,突觸解析度重建仍在做)、小鼠全腦(NIH BRAIN CONNECTS,2023 起)。 | S |
| whats-next | facts | 302 線蟲神經元,第一個完整連接組,1986(todo,自陳「原頁被擋,數字為二手轉引」) | N/S |
| whats-next | facts | 166,691 雄果蠅中樞神經系統/本站(paper, bioRxiv 前導版親讀) | N/S |
| whats-next | facts | 120,000 / 5.23 億 小鼠 1mm³ 神經元/突觸(paper,官方專案頁親讀) | N/S |
| whats-next | facts | 57,000 / 1.5 億 人類 1mm³ 細胞/突觸(paper, Shapson-Coe et al. 2024) | N/S |
| whats-next | facts | 2023 起 小鼠全腦計畫 BRAIN CONNECTS(todo,自陳「官方頁被重導向,為二手轉引」) | N/S |
| why-sudden | kid | 它在偷偷充電。偵測器的訊號跨過接點跑到巨纖維身上,每一份只推高一點點,巨纖維的電壓從 −52 一格一格往上爬。 | N/C |
| why-sudden | kid | 爬到 −45 那條線的瞬間,它才啪一聲放電——那就是你看到的「突然」。 | N/C |
| why-sudden | more | 訊號的傳遞是電→化學→電:偵測器的動作電位是電,到了突觸不會跳過去,而是釋放乙醯膽鹼,飄過約 20 奈米的縫、黏上巨纖維的受體、打開離子通道,在對面重新產生一個小電壓變化。 | S |
| why-sudden | more | 每個突觸只給 0.275 mV,靜息到閾值差 7 mV,而電壓同時以 20 ms 的時間常數往下漏。 | N |
| why-sudden | more | 311 顆偵測器 × 每條約 50 個突觸的輸入,讓它在第一批輸入落地(延遲 1.8 ms)後約 1.5 ms 就跨線。 | N/C |
| why-sudden | more | 右上角的電壓計是引擎原樣輸出的膜電壓,不是示意。 | S |
| why-sudden | facts | 3.3 ms 巨纖維跨過閾值的時刻(measured, escape.trace.csv) | N |
| why-sudden | facts | 0.275 mV 每個突觸的貢獻(paper, Shiu et al. 2024) | N |
| why-sudden | facts | 1.8 ms 突觸延遲(paper, Shiu et al. 2024) | N |
| tried-critical-point | kid | 論文給的「每個接點推多大力」是在另一隻(雌的)果蠅腦上調出來的。我們把它套到這隻雄果蠅腦上,再把力道調小 13% 試試:同樣隨機戳 25 顆細胞,原本會有 12 萬次放電,調小後只剩 1,700 次。 | N/S |
| tried-critical-point | kid | 這顆腦剛好站在「一點就著」的邊緣上,論文的數值正好落在邊緣的上面。 | S |
| tried-critical-point | more | 掃 w_syn:0.275(論文值)對 25 顆隨機刺激給 121,592 次放電,0.240 給 1,747,兩者之間有相變;0.179(第三方專案用的 0.65 增益)落在安全區。 | N |
| tried-critical-point | more | 侷限:刺激是隨機神經元非真實感覺族群,只測 100 Hz × 300 ms,k 取樣粗(5/25/200/2000)。後果:單次數字不能當生理量。 | S |
| tried-critical-point | facts | 121,592 → 1,747 放電數,w_syn 0.275→0.240(measured, scripts/phase_sweep.py) | N |
| tried-critical-point | facts | 0.275 mV 論文的唯一自由參數(paper, Shiu et al. 2024) | N |
| tried-bistable | kid | 我們什麼都不改,只換模擬用的亂數,同一組刺激跑六次:結果從 1,076 次放電到 23,872 次都有。 | N |
| tried-bistable | kid | 這不是程式壞掉,是站在邊緣的系統本來就這樣——輕輕一推,有時候倒、有時候不倒。 | C |
| tried-bistable | kid | 所以這個網站上每個數字都是跑很多次以後才寫上去的。 | U |
| tried-bistable | more | w_syn 0.120、k=50,六個種子:23,872 / 1,144 / 1,076 / 11,654 / 4,655 / 1,081,變異係數 1.26。 | N |
| tried-bistable | more | 遠離臨界點才可重現(w 0.179、k=25 六次 CV 0.08)。 | N/C |
| tried-bistable | more | phase_sweep 那張每格只跑一次的表,過渡區全部不可信,已在腳本 docstring 標明。 | S |
| tried-bistable | facts | CV 1.26 六次結果的變異係數(measured, verification_log.md) | N |
| tried-bistable | facts | 22× 最大/最小(measured, verification_log.md) | N |
| tried-visual-frontend | kid | 我們一開始想讓訊號真的從眼睛走到底。結果從眼睛的柱子餵進去,負責偵測「有東西撲來」的細胞幾乎沒反應。可是如果直接餵那些偵測器,後面一路到巨纖維、到肌肉全都正常。所以斷的那一段在眼睛和偵測器之間。 | N/C |
| tried-visual-frontend | kid | 這就是為什麼畫面上前奏那段是洋紅色的:那一步不是模型算的,是我們接上去的。 | S |
| tried-visual-frontend | more | 刺激視覺柱:LC4 只到 1.23 Hz、LPLC2 0。直接刺激 LC4+LPLC2 共 311 顆:巨纖維 283.80 ± 0.45 Hz、跳躍肌 73.0、翅膀下壓肌 114.9;對照隨機 311 顆:巨纖維 0.00。 | N |
| tried-visual-frontend | more | 斷點在運動偵測那一級(髓質運動路徑),與第三方專案自承的限制一致,我們獨立量化。 | S |
| tried-visual-frontend | more | 網站硬性規定:「眼睛看到→偵測器啟動」必須標示為注入。 | U/S |
| tried-visual-frontend | facts | 1.23 Hz / 0 從視覺柱餵:LC4/LPLC2(measured) | N |
| tried-visual-frontend | facts | 283.8 Hz 直接餵偵測器:巨纖維(measured) | N |
| tried-pulse-length | kid | 第一版刺激給了 25 毫秒,結果整個畫面同時亮,看不出訊號一站一站傳。改成 3 毫秒,跳躍肌一下都沒動。 | N |
| tried-pulse-length | kid | 6 毫秒剛剛好:偵測器先亮、巨纖維 3.3 毫秒接到、跳躍肌 14.4 毫秒動、翅膀肌 15.7 毫秒動。 | N |
| tried-pulse-length | more | 三版對照(6 ms 出貨):25 ms → 偵測器 0-32 ms、巨纖維 3.3-31.9、全部重疊;3 ms → 巨纖維 5 次、TTMn 沒放電、PSI 沒放電;6 ms → 巨纖維 7 次、TTMn 14.4 ms 一次、DLMn 15.7-249.1、PSI 沒放電。 | N |
| tried-pulse-length | more | 要有接力,脈衝必須比傳遞(3-13 ms)短。 | C |
| tried-pulse-length | more | 6 ms 版 TTMn 只放電 1 次、巨纖維 7 次,統計極薄,字幕只寫首次時刻不寫速率。 | S |
| tried-pulse-length | facts | 25/3/6 ms 三版脈衝長度(measured, build_scenario.py) | N |
| tried-pulse-length | facts | 14.4/15.7 ms 跳躍肌/翅膀肌首次放電(measured, escape.csv) | N |
| next-fix-model | kid | 我們發現模型缺三樣東西:第一,眼睛到偵測器那段為什麼斷了;第二,真果蠅有「直接通電」的接點,所以比模型快,模型沒有;第三,模型一旦點燃就停不下來,真果蠅會停。 | N/C |
| next-fix-model | kid | 這三個都還沒有人做,誰先做誰就知道答案。 | U |
| next-fix-model | more | ①視覺前端:LC4 從視覺柱只收到 1.23 Hz,要追髓質運動路徑(T4/T5)為何靜默 | N |
| next-fix-model | more | ②電突觸:巨纖維到跳躍肌實際 0.93 ms,模型固定 1.8 ms 化學延遲 | N |
| next-fix-model | more | ③停止機制:600 ms 仍在放電,候選是放電後適應、慢抑制或神經調節 | N |
| next-fix-model | facts | 0.93 vs 1.8 ms 真果蠅 vs 模型:GF→跳躍肌(paper) | N |
| next-fix-model | facts | 3 尚未做的實驗(measured) | N |
| next-new-stories | kid | 這隻是雄果蠅,牠的觸角上沒有嚐甜味的細胞,卻有聞「另一隻果蠅味道」的細胞,所以下一個最自然的故事是求偶。 | N/C |
| next-new-stories | kid | 腦裡唯一能改的小地方叫蘑菇體,可以拿來做「學會討厭一種味道」的實驗。還可以拿這隻雄的跟另一隻雌的腦比一比,看逃跑的線路一不一樣。這些都還沒做。 | S |
| next-new-stories | more | MaleCNS 的受器標註只有 ppk23/ppk25/IR52b(費洛蒙),沒有糖受器,所以「嚐糖」在這隻腦上做不了,「聞到雌蠅」可以。 | N/U |
| next-new-stories | more | KC→MBON 61,210 條可塑突觸,規則是多巴胺同時活躍時壓抑而非增強;可以模擬氣味制約,但引擎目前沒有可塑性項。 | N/C |
| next-new-stories | more | FlyWire 是雌腦,逃跑迴路的 LC4/LPLC2→巨纖維收斂比與突觸數可以逐一對照。 | S |
| next-new-stories | more | 現在是預錄播放,換成瀏覽器內即時模擬(WASM)使用者才能自己選刺激;前端播放層與資料層已切開,為此預留。 | S |
| next-new-stories | facts | 61,210 可塑突觸(學習實驗的場地)(measured) | N |
| next-new-stories | facts | ppk23/ppk25/IR52b 這隻腦標註的受器種類(無糖受器)(measured) | N/U |
| stage t=-24 | stage | 這段是我們畫的示意,不是模型算的——模型的視覺前端算不出逼近。只有物體影像蓋到的那一小塊視野會被觸動,影像越來越大、邊緣反應最強。區塊放在眼睛的官方定義中心(hex 18,19);哪個方向是正前方尚待確認 | S/N(自陳未決) |
| stage t=0 | stage | 有東西朝果蠅撲過來;這一步是我們注入的——模型的視覺前端算不出逼近。偵測器只被餵 6 ms | N/S |
| stage t=1 | stage | 偵測器正在放電,巨纖維要到 3.3 ms 才收到。中間沒有別的神經細胞——偵測器直接接到巨纖維,兩顆細胞交接訊號的那個接點叫突觸,訊號跨過去要 1.8 ms。巨纖維的電壓正在從 −52 往 −45 爬,爬過那條線它才會放電。 | N/U |
| stage t=3 | stage | 311 顆逼近偵測器全部接到左右各一顆巨纖維上;首次放電 3.3 ms | N/U |
| stage t=8 | stage | 刺激 6 ms 就停,偵測器 12 ms 前全部安靜;一群往下送命令的神經細胞(DNp03、AN19B001 等)接手 | N |
| stage t=14 | stage | 跳躍肌 14.4 ms(走巨纖維直連)、翅膀下壓肌 15.7 ms(走 AN19B001)。訊號已穿過那段只有神經線、完全沒有細胞的脖子。從管肌肉的神經細胞到肌肉這一段,我們的資料裡沒有:畫面上的琥珀色線是我們畫的,只有亮起來的時機是真的 | N/S |
| stage t=30 | stage | 教科書裡的中繼站 PSI 在這個情境裡完全沒放電(被抑制壓住)。翅膀肌會一直放電到模擬盡頭:我們跑到 600 ms 它還在。這個模型一旦點燃就沒有機制讓它停,真果蠅不是這樣。模擬只播到 250 ms,後面那段收尾是我們加的,不是模型算的 | N/S |
| stage t=250 | stage | 模型跑到 600 ms 都還在放電,真的果蠅這時也還在飛。這一段是我們畫的收尾,讓畫面回到靜止:神經細胞的光和翅膀都是我們慢慢關掉的,不是模擬算出來的 | S |
| index.html #prov | legend | 發光 ＝ 真實神經元位置與活動 | S |
| index.html #prov | legend | 洋紅 ＝ 模型算不出,我們注入的 | S |
| index.html #prov | legend | 線稿 ＝ 我們畫的身體(比例對位神經系統,腹部為示意) | S |
| index.html #prov | legend | 琥珀 ＝ 神經→肌肉,連接組沒有,我們畫的(時機來自真實運動神經元) | S |
| index.html #pip | legend | pipTitle:「果蠅身體 · 我們畫的」 | S |
| index.html #pip | legend | pipNote:「動作方向與時機來自真實放電;幅度是示意——連接組沒有肌肉與物理」 | S |

## 額外觀察(超出交辦範圍但落在 index.html 內,一併記錄供主線裁決)
`<title>` 標籤(非 #prov / PiP,但同在 index.html):「果蠅腦 — 140,024 顆神經元」——這個數字**既不等於**
body-overview/optic-lobe/eight-senses 等卡用的 165,122,**也不等於** why-fly/whats-next 用的 166,691,
三個數字同時出現在同一個交付物裡,無一處互相對照或解釋差異。因超出交辦的「只看 #prov 與 PiP」範圍,未列入上表,但因是全站唯一在瀏覽器分頁就看得到的數字,重要性可能最高,故在此標出留主線裁決。

---

**總條數:238 條**(`grep -c '^|'` 得 240,扣表頭與分隔線各 1 行 = 238 筆宣稱)
**各類型條數(以每行類型欄逐行計,一行標兩種類型時兩邊各記一次,故總和 >238):數字(N)標記 ≈150 行;全稱(U)標記 ≈45 行;因果(C)標記 ≈45 行;來源(S)標記 ≈95 行**
（此為對類型欄逐行掃描的估計,非精確去重值,精確分佈需再對表格跑一次機器統計)
**檔案路徑**:audit/claims_independent.md

**最容易被小孩追問、卡片答不出來的 5 條**:
1. `<title>` 的 140,024 vs 卡片內 165,122 / 166,691 三個神經元總數同站並存,小孩問「到底幾個」答不出來(見上方額外觀察)。
2. hex-columns:「14 種細胞型每型在每根柱子裡恰好一顆」——小孩問「有沒有例外」,卡片只給「各型總數 1,732-1,773 對 1,771 柱」這個粗略吻合,不是逐柱驗證過「零例外」。
3. escape-two-muscles:卡片先說教科書 GF→PSI→DLMn「完全吻合」,又說本模擬 PSI「從頭到尾沒放電」——小孩問「所以 PSI 到底有沒有用」,兩段之間沒有橋接解釋。
4. never-stops / next-fix-model:反覆承認模型「不會自己停」且「停止機制」列為三個未解實驗之一——小孩問「那牠到底為什麼會停」,誠實答案是「不知道」,對小孩層不友善。
5. stage t=-24:自陳「哪個方向是正前方尚待確認」——小孩問「牠面對哪裡」,字幕自己承認没確定。

**MLD**
- M:第一遍讀 cards.json 時把「數字型宣稱」與純敘述性解剖描述混在一起導致初稿條目膨脹,後來收窄到「必須帶數字/全稱詞/因果連接詞/來源語彙」才收斂到可控行數;另外 more 與 facts 常常是同一個數字重複出現(如 61,210、165,122),我把它們當成獨立行分別列出而未去重合併,可能讓下游做差集時誤判「重複覆蓋」為「兩條宣稱」。
- L:33 張卡的 kid/more 幾乎每句都可拆成一條宣稱,萃取量遠大於直覺預期(200+ 條);下次同類任務應一開始就設「僅拆到含可否證要素的子句」的規則,而不是先拆全句再篩選,可省一半來回。
- D:希望能拿到一份「這個網站總共引用幾個不同的神經元總數版本」的機器 grep 結果(如 `grep -o '16[0-9],[0-9]\{3\}\|140,024' **/*.json index.html`)當起點,而不是純人工逐卡比對數字——這類跨檔案數字一致性檢查用 grep 遠比人讀快,且不會漏。
