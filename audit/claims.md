# 宣稱清單(機器產生,validity-audit 第 1 步)

卡片 34 張,事實 88 條,階段字幕 8 段。

| 卡/階段 | 數值 | 標籤 | 標記 | 來源欄 | 路徑檢查 |
|---|---|---|---|---|---|
| body-overview | 165,122 | 神經元 | measured | ../fly/scripts/io_inventory.py | 缺:../fly/scripts/io_inventory.py(研究倉路徑:公開版必須自足,腳本請複製到 scripts/fly/) |
| body-overview | 140,024 | 畫得進點雲(有細胞本體座標) | measured | scripts/export_soma.py;CLAUDE.md §我們有、別人沒有的東西 | 路徑OK |
| body-overview | 995 µm | 神經系統全長 | measured | scripts/export_soma.py | 路徑OK |
| body-overview | 36% | 佔體長比例 | measured | scripts/export_soma.py | 路徑OK |
| antenna-soma | 0 / 4,868 | 腦內感覺神經元有細胞本體的 | measured | scripts/export_soma.py | 路徑OK |
| eight-senses | 15,912 | 感覺神經元 | measured | scripts/fly/io_inventory.py | 路徑OK |
| eight-senses | 66 | 濕度感覺神經元 | measured | scripts/fly/io_inventory.py | 路徑OK |
| eight-senses | 1,844 | 還沒分到具體感覺的感覺神經元 | measured | scripts/fly/out/io_inventory.json sensory.by_class | 路徑OK |
| optic-lobe | 89,390 | 視葉神經元 | measured | scripts/fly/io_inventory.py | 路徑OK |
| neck-gap | 132 µm | 沒有細胞本體的長度 | measured | scripts/export_soma.py | 路徑OK |
| motor-map | 815 | 運動神經元 | measured | scripts/fly/io_inventory.py | 路徑OK |
| motor-map | 381 | 控制腳的 | measured | scripts/fly/io_inventory.py | 路徑OK |
| wing-beat | 169 Hz | 起飛拍翅頻率 | todo | arXiv:1504.04484(親讀)——但該值是它引用 Chen & Sun 的量測,屬二手轉引;且該文是數值模擬研究,169 Hz 是它的輸入參數,不是本文的觀測 | 非路徑(論文/標註) |
| wing-beat | 134° | 拍幅 | paper | arXiv:1504.04484 | 非路徑(論文/標註) |
| wing-beat | 2.83 mm | 翅長 | paper | arXiv:1504.04484 | 非路徑(論文/標註) |
| wing-beat | 55° | 我們畫的拍翅面傾角 | todo | src/shell.ts STROKE_TILT(示意,無出處) | 路徑OK |
| hex-columns | 892 / 879 | 右眼 / 左眼柱數 | measured | annotation assignedOlHex1/2;scripts/export_hexmap.py | 路徑OK |
| hex-columns | 1,771 | 柱數合計(892 + 879) | measured | scripts/export_hexmap.py(兩眼相加) | 路徑OK |
| hex-columns | 27 | 每柱神經元中位數 | measured | annotation assignedOlHex1/2;scripts/export_hexmap.py | 路徑OK |
| hex-columns | 96.7-99.8% | 12 種細胞型恰好一顆/柱的柱子比例 | measured | audit/_hex_per_column.txt(2026-09-15 逐柱重數,腳本內嵌於該檔) | 非路徑(論文/標註) |
| spikes-hz | 207 Hz | MN9 放電率(模型值,相對指標) | measured | docs/verification_log.md §對既有結論的影響 第 2 點(原始 spike log taskA_real.csv 66 MB 留在研究倉,未隨網站公開) | 路徑OK |
| spikes-hz | 2.2 ms | 不應期 | paper | Shiu et al. Nature 634:210-219 (2024) | 非路徑(論文/標註) |
| calcium-glow | 80 ms | 我們選的顯示衰減常數(示意,非量到的螢光常數) | todo | scripts/render_glow_test.py(顯示參數) | 路徑OK |
| shuffle-control | 207.00 → 0.00 Hz | 真實 → 打亂 | measured | scripts/fly/shuffle_csr.py | 路徑OK |
| shuffle-control | 0.388% | 打亂後保留的原始連線 | measured | scripts/fly/shuffle_csr.py | 路徑OK |
| no-spontaneous | 0 | 不給輸入時的模型放電數 | measured | docs/verification_log.md(模型沒有自發活動) | 路徑OK |
| no-spontaneous | — | 真果蠅腦有持續自發活動(常識,未引文獻) | todo | 未引文獻 | 非路徑(論文/標註) |
| no-learning | 0 | 模擬過程中被更新的連線強度 | measured | docs/verification_log.md §模型沒有學習機制(逐檔搜尋引擎原始碼,無任何寫回權重的程式碼) | 路徑OK |
| no-learning | 61,210 | 資料裡負責學習的那些連線(KC→MBON) | measured | scripts/fly/mb_circuit_stats.py;輸出 audit/_mb_stats.txt | 路徑OK |
| no-learning | 570 | 被逐檔搜尋過的引擎原始碼行數 | measured | docs/verification_log.md §模型沒有學習機制 | 路徑OK |
| never-stops | 599.8 ms | 最後一次放電(模擬盡頭) | measured | docs/verification_log.md §模型不會自己停(600 ms 探測) | 路徑OK |
| never-stops | 562 ms | 翅膀肌最後放電 | measured | docs/verification_log.md §模型不會自己停 | 路徑OK |
| escape-converge | 309 / 311 → 2 | 直接連到巨纖維的偵測器(權重 ≥2) | measured | public/data/escape_edges.json(出貨連線檔)重算:LC4 126/126 貢獻 6,362 個突觸、LPLC2 183/185 貢獻 4,860;無任一顆同時連兩顆巨纖維;scripts/fly/escape_path.py | 路徑OK |
| escape-converge | LC4=速度, LPLC2=大小 | 各自編碼什麼 | paper | Ache et al. Curr Biol (2019) | 非路徑(論文/標註) |
| escape-two-muscles | 90 | 巨纖維→跳躍肌運動神經元 突觸 | measured | scripts/fly/escape_path.py | 路徑OK |
| escape-two-muscles | 0 | 巨纖維→翅膀肌運動神經元 直連 | measured | scripts/fly/escape_path.py | 路徑OK |
| escape-two-muscles | 15.7 ms | 模擬裡翅膀肌運動神經元首次放電(走 AN19B001) | measured | runs/build/escape.csv;docs/verification_log.md §DLMn 首波 | 路徑OK |
| escape-two-muscles | 0 次 | PSI 在本情境的放電 | measured | runs/build/escape.csv | 路徑OK |
| muscle-link | 26 | 連線起點:真實運動神經元 | measured | scripts/export_edges.py(nodesByStage wing/jump) | 路徑OK |
| muscle-link | 0 | 資料集裡的肌肉 | measured | annotation superclass 清單(scripts/fly/io_inventory.py) | 路徑OK |
| escape-speed | 18 ms | 燈熄 → 巨纖維放電 | paper | Fotowat et al. J Neurophysiol 102(2):875-885 (2009),PMC3817277 全文親讀 | 非路徑(論文/標註) |
| escape-speed | 25 ms | 燈熄 → 起飛 | paper | 同上 | 非路徑(論文/標註) |
| escape-speed | 6 ms | 影像達 54° → 起飛(逼近刺激) | paper | 同上 | 非路徑(論文/標註) |
| escape-speed | 0.93 ms | 巨纖維→跳躍肌 | paper | Augustin et al. eNeuro 6(2) ENEURO.0423-18.2019,bioRxiv 全文親讀 | 非路徑(論文/標註) |
| escape-speed | 0.1-0.4 s | 人眨一次眼(常識,未引文獻) | todo | 未引文獻 | 非路徑(論文/標註) |
| escape-is-decision | ~200 ms | 長模式的準備期 | paper | Card & Dickinson, Curr Biol 18(17):1300-1307 (2008),摘要經 Europe PMC 親讀(PMID 18760606) | 非路徑(論文/標註) |
| escape-is-decision | 兩種模式 | 由放電時序選擇 | paper | von Reyn et al. Nat Neurosci 17:962-970 (2014),摘要經 Europe PMC 親讀(PMID 24908103) | 非路徑(論文/標註) |
| model-vs-real | 0.93 ms | 真果蠅:巨纖維→跳躍肌(含神經肌肉接合 0.35 ms) | paper | Augustin et al. eNeuro 6(2) ENEURO.0423-18.2019,bioRxiv 全文親讀 | 非路徑(論文/標註) |
| model-vs-real | 1.8 ms | 模型每個突觸的固定延遲 | paper | Shiu et al. Nature 634:210-219 (2024) | 非路徑(論文/標註) |
| model-vs-real | Shaking-B | 構成間隙連接的蛋白 | paper | Augustin et al. eNeuro 6(2) ENEURO.0423-18.2019,bioRxiv 全文親讀 | 非路徑(論文/標註) |
| mushroom-body | 61,210 | 可塑連線(KC→MBON,463,640 個突觸) | measured | scripts/fly/mb_circuit_stats.py;輸出 audit/_mb_stats.txt(2026-09-15 重跑) | 路徑OK |
| mushroom-body | 0.24% | 佔全腦 25.6M 條連線 | measured | 61,210 / 25,600,000(Berg et al. 2026 edges);docs/data_facts.md | 路徑OK |
| why-fly | 166,691 | 完整重建的神經元 | paper | Berg et al. Cell 189(18):5504-5526 (2026) | 非路徑(論文/標註) |
| why-fly | 861 ± 81 億 | 人腦神經元總數 | paper | Azevedo et al. J Comp Neurol 513:532-541 (2009),摘要經 Europe PMC 親讀 | 非路徑(論文/標註) |
| why-fly-history | 1910 | Morgan 的果蠅遺傳學論文 | todo | Morgan T.H. Science 32:120-122 (1910);引文經 FlyBase FBrf0000547 親讀核對,論文原文未親讀 | 非路徑(論文/標註) |
| why-fly-history | 7-9 天 | 卵到成蟲(28°C / 25°C) | paper | Bloomington Drosophila Stock Center fly-culture 頁(親讀:7 天 29°C / 9 天 25°C) | 非路徑(論文/標註) |
| why-fly-history | 1993 | GAL4/UAS 系統 | paper | Brand & Perrimon, Development 118:401-415 (1993) | 非路徑(論文/標註) |
| why-fly-history | 77% | 人類疾病基因在果蠅有同源(714/929) | paper | Reiter et al. Genome Res 11:1114-1125 (2001),摘要親讀 | 非路徑(論文/標註) |
| vs-mammal | 約 1 年 | 人類學會走路(常識,未引文獻) | todo | 未引文獻 | 非路徑(論文/標註) |
| fly-vs-human-vision | 60% | 果蠅視覺神經元佔比(顆數) | measured | scripts/fly/io_inventory.py | 路徑OK |
| fly-vs-human-vision | 52% | 獼猴視覺皮質佔皮質面積 | paper | Van Essen, in The Visual Neurosciences (2003),PDF 親讀;講獼猴非人類 | 非路徑(論文/標註) |
| fly-vs-human-vision | 2.2% | 人類 V1 佔大腦皮質面積 | paper | Van Essen, in The Visual Neurosciences (2003),PDF 親讀,人類章節(V1 = 21 cm², 2.2%) | 非路徑(論文/標註) |
| fly-vs-human-vision | 861 ± 81 億 | 人腦神經元總數 | paper | Azevedo et al. J Comp Neurol 513:532-541 (2009),摘要經 Europe PMC 親讀 | 非路徑(論文/標註) |
| vs-llm | 0.24% | 可塑連線比例(對照 LoRA 數量級) | measured | 61,210 / 25.6M;scripts/fly/mb_circuit_stats.py | 路徑OK |
| whats-next | 302 | 線蟲神經元(第一個完整連接組,1986) | todo | White et al. Phil Trans R Soc B (1986);原頁被擋,數字為二手轉引 | 非路徑(論文/標註) |
| whats-next | 3,016 / 548,000 | 果蠅幼蟲連接組 神經元 / 突觸 | paper | Winding et al. Science 379(6636):eadd9330 (2023);PMC7614541 摘要親讀,原句「comprising 3016 neurons and 548,000 synapses」 | 非路徑(論文/標註) |
| whats-next | 166,691 | 雄果蠅中樞神經系統(本站) | paper | Berg et al. Cell 189(18) (2026);bioRxiv 前導版親讀 | 非路徑(論文/標註) |
| whats-next | 120,000 / 5.23 億 | 小鼠 1 mm³ 神經元 / 突觸 | paper | microns-explorer.org/cortical-mm3(官方專案頁親讀) | 非路徑(論文/標註) |
| whats-next | 57,000 / 1.5 億 | 人類 1 mm³ 細胞 / 突觸 | paper | Shapson-Coe et al. Science 384:eadk4858 (2024),Research Article Summary 親讀 | 非路徑(論文/標註) |
| whats-next | 2023 起 | 小鼠全腦計畫 BRAIN CONNECTS | todo | NIH BRAIN Initiative 官方頁被重導向,為二手轉引 | 非路徑(論文/標註) |
| why-sudden | 3.3 ms | 巨纖維跨過閾值的時刻 | measured | runs/build/escape.trace.csv(引擎 --trace-out) | 路徑OK |
| why-sudden | 0.275 mV | 每個突觸的貢獻 | paper | Shiu et al. Nature 634:210-219 (2024) | 非路徑(論文/標註) |
| why-sudden | 1.8 ms | 突觸延遲 | paper | Shiu et al. Nature 634:210-219 (2024) | 非路徑(論文/標註) |
| why-sudden | −52 → −45 mV | 靜息電位 → 閾值(模型參數) | paper | Shiu et al. Nature 634:210-219 (2024) | 非路徑(論文/標註) |
| why-sudden | 11,222 / 36 | 偵測器→巨纖維突觸總數 / 每顆平均 | measured | public/data/escape_edges.json 重算(6,362 + 4,860) | 路徑OK |
| tried-critical-point | 1,747 vs 117,208 | 同一格(w_syn 0.24, k=25)兩次單跑的放電數 | measured | scripts/phase_sweep.py;public/data/phase_sweep.json table[1].counts[1];docs/verification_log.md §臨界點 | 路徑OK |
| tried-critical-point | 1.26 | 雙穩態測試的變異係數(同參數換種子跑六次) | measured | docs/verification_log.md §雙穩態:臨界點附近單次試驗無意義 | 路徑OK |
| tried-critical-point | 0.275 mV | 論文的唯一自由參數 | paper | Shiu et al. Nature 634:210-219 (2024) | 非路徑(論文/標註) |
| tried-bistable | CV 1.26 | 六次結果的變異係數(w 0.120, k=50) | measured | docs/verification_log.md §雙穩態 | 路徑OK |
| tried-bistable | 22× | 最大/最小 | measured | docs/verification_log.md §雙穩態 | 路徑OK |
| tried-visual-frontend | 1.23 Hz / 0 | 從視覺柱餵:LC4 / LPLC2 | measured | scripts/visual_pathway_test.py;docs/verification_log.md | 路徑OK |
| tried-visual-frontend | 283.8 Hz | 直接餵偵測器:巨纖維 | measured | scripts/visual_pathway_test.py;docs/verification_log.md | 路徑OK |
| tried-pulse-length | 25 / 3 / 6 ms | 三版脈衝長度(出貨 6) | measured | scripts/build_scenario.py T_STIM;docs/verification_log.md §脈衝長度 | 路徑OK |
| tried-pulse-length | 14.4 / 15.7 ms | 跳躍肌 / 翅膀肌的運動神經元首次放電 | measured | runs/build/escape.csv | 路徑OK |
| next-fix-model | 0.93 vs 1.8 ms | 真果蠅 vs 模型:巨纖維→跳躍肌 | paper | Augustin et al. eNeuro 6(2) ENEURO.0423-18.2019,bioRxiv 全文親讀 | 非路徑(論文/標註) |
| next-fix-model | 3 | 尚未做的實驗 | measured | docs/verification_log.md 各節的「侷限」 | 路徑OK |
| next-new-stories | 61,210 | 可塑連線(學習實驗的場地) | measured | scripts/fly/mb_circuit_stats.py;輸出 audit/_mb_stats.txt | 路徑OK |
| next-new-stories | ppk23/ppk25/IR52b | 這隻腦標註的受器種類(無糖受器) | measured | scripts/fly/receptor_types.py;docs/data_facts.md §最大未知(receptorType 欄位) | 路徑OK |
| stage@-24ms | (無數字) | 眼睛看到有東西撲過來 | injected | scripts/export_hexmap.py;github.com/reiserlab/male-drosophila-visual-system-connectome-code 的 docs/coordinate-systems.md(外部);docs/verification_log.md §六角座標慣例 | 路徑OK |
| stage@0ms | 6 ms | 有東西朝果蠅撲過來 | injected | docs/verification_log.md §視覺路徑 go/no-go;build_scenario.py T_STIM | 路徑OK |
| stage@1ms | 3.3 ms; 1.8 ms | 訊號在突觸上,還沒到巨纖維 | measured | 引擎 --trace-out(runs/build/escape.trace.csv);scripts/fly/escape_path.py | 路徑OK |
| stage@3ms | 311 顆; 309 顆; 3.3 ms | 巨纖維放電了 | measured | scripts/build_scenario.py → runs/build/escape.csv | 路徑OK |
| stage@8ms | 6 ms; 12 ms | 偵測器開始暗下去,命令往下走 | measured | scripts/trace_drivers.py;runs/build/escape.csv | 路徑OK |
| stage@14ms | 14.4 ms; 15.7 ms | 跳躍肌與翅膀肌動了 | measured | runs/build/escape.csv | 路徑OK |
| stage@30ms | 600 ms; 562 ms; 250 ms | 視葉已經安靜,肌肉還在動——而且不會自己停 | measured | docs/verification_log.md §模型不會自己停;runs/build/escape.csv | 路徑OK |
| stage@250ms | 600 ms | 我們加的結局:讓牠停下來 | injected | docs/verification_log.md §模型不會自己停、§我們加的結局;src/main.ts EPILOGUE | 路徑OK |

路徑缺失:1
- body-overview: ../fly/scripts/io_inventory.py(研究倉路徑:公開版必須自足,腳本請複製到 scripts/fly/)
