# 果蠅腦教育網站 — 說明卡事實查證報告

查證日期:2026-09-15。方法:WebSearch 定位來源 → WebFetch 或 Read(PDF)親讀原文逐字句。
每條標示「親讀」(我自己開啟該 URL 或其 PDF 並看到原文)或「secondhand」(只在摘要/新聞稿/第三方轉述中看到)。
查不到就標「未查證」,不硬掰。

---

## 第一組:為什麼選果蠅

### (a) Morgan 1910 年開始用果蠅做遺傳學

**判定:證實(年份、論文皆對,但正文本身未能親讀,標 secondhand 佐以官方資料庫確認)**

- 逐字引用:「In 1910 Thomas Hunt Morgan and Lilian Vaughan Morgan collected a single male white-eyed mutant from a population of *Drosophila melanogaster* fruit flies」
  URL:https://en.wikipedia.org/wiki/White_(mutation) — secondhand(Wikipedia 轉述,輔助來源)
- 官方文獻資料庫確認引文本身存在且年份正確:
  逐字引用:「Morgan, T.H. (1910). Sex limited inheritance in Drosophila. Science 32(): 120--122.」
  URL:https://flybase.org/reports/FBrf0000547 — 親讀(FlyBase 是果蠅研究官方文獻資料庫,我直接 WebFetch 此頁)
- 原始 1910 Science 論文本身(science.org/doi/10.1126/science.32.812.120、old.esp.org 全文 PDF)因 403/連線失敗未能親讀原句;science.org 頁面回傳 HTTP 403,old.esp.org PDF 連線被拒。
- 結論:年份 1910、論文題名與期刊卷頁(Science 32: 120-122)經 FlyBase 官方資料庫(親讀)與 Wikipedia(secondhand)交叉確認一致,與使用者記憶相符。**未能取得原始論文正文的逐字親讀版本**,卡片若要引用論文原句需再補查。

### (b) 世代時間(約幾天)

**判定:證實**

- 逐字引用:「Shortest development time (egg to adult), 7 days, is achieved at 28 °C.」
  出處:Ashburner, Golic & Hawley (2005) *Drosophila: A Laboratory Handbook*, 2nd ed., p.164,轉引於
  URL:https://bionumbers.hms.harvard.edu/bionumber.aspx?s=n&v=5&id=100521 — 親讀
- 逐字引用(獨立來源交叉確認):「Generation time (from egg to adult) is approximately: 7 days at 29°C, 9 days at 25°C, 11 days at 22°C, 19 days at 18°C.」
  URL:https://bdsc.indiana.edu/information/fly-culture.html(Bloomington Drosophila Stock Center 官方頁面) — 親讀
- 結論:適合給小孩的說法可寫「最快 7 天、常溫(25°C)約 9-10 天」,兩個獨立官方/機構來源數字一致。

### (c) GAL4/UAS 系統原始論文(Brand & Perrimon 1993)

**判定:證實**

- 逐字引用(標題與出處):「Targeted gene expression as a means of altering cell fates and generating dominant phenotypes」,作者 Andrea H. Brand, Norbert Perrimon,期刊 *Development*,Volume 118,Issue 2,Pages 401–415,Year 1993。
  URL:https://journals.biologists.com/dev/article/118/2/401/37970/Targeted-gene-expression-as-a-means-of-altering — 親讀(WebFetch 直接取得該頁的 Citation Information 區塊)
- 摘要開頭逐字引用:「We have designed a system for targeted gene expression that allows the selective activation of any cloned gene in a wide variety of tissue and cell-specific patterns.」
  同上 URL — 親讀
- 結論:與使用者記憶完全相符(Brand & Perrimon 1993, *Development* 118:401-415)。

### (d) 腦小到能用電子顯微鏡逐片切完

**判定:證實(用 hemibrain 論文的 eLife digest 原句;FlyWire 論文用 bioRxiv 前導版親讀,Nature 正式版數字為 secondhand)**

- 逐字引用(eLife 對 Scheffer et al. 2020 的 lay summary/digest):「With about 100,000 neurons – compared to some 86 billion in humans – the fly brain is small enough to study at the level of individual cells.」
  URL:https://elifesciences.org/articles/57443 — 親讀
- 同篇摘要逐字引用:「We provide detailed circuits consisting of neurons and their chemical synapses for most of the central brain」;摘要另段:「around 25,000 neurons」「about 20 million chemical synapses」(hemibrain = 中央腦一部分,非全腦)
  同上 URL — 親讀
- FlyWire(Dorkenwald et al.)全腦論文,bioRxiv 前導版(2023-06-30)逐字引用:「Here, we present the first neuronal wiring diagram of a whole adult brain, containing 5×10^7 chemical synapses between ∼130,000 neurons reconstructed from a female *Drosophila melanogaster*.」
  URL:https://www.biorxiv.org/content/10.1101/2023.06.27.546656v1 — 親讀
- 正式發表版(*Nature* 634:124-138, 2024,DOI 10.1038/s41586-024-07558-y)常被引用的精確數字「139,255 個神經元、54.5 百萬個突觸連接」,多個獨立次級來源一致(Princeton 新聞稿、ScienceNews、PubMed 摘要合成),但 Nature.com 原頁因需登入被 403 擋下,**未能親讀 Nature 正式版摘要原句**,此精確數字標 secondhand。
- 結論:「腦小到能被完整電顯重建」的說法有 eLife 原句佐證(親讀);具體神經元數字前導版(~130,000,親讀)與正式版(139,255,secondhand)略有差異,卡片若寫精確數字建議標注「約 13.9 萬」並附正式版 DOI。

### (e) 果蠅與人類基因同源比例(約 60%/75% 疾病基因)

**判定:與記憶不符 — 正確數字是 77%(929 個中 714 個,非 60% 或 75%)**

- 逐字引用(直接讀取論文第一頁 PDF 影像,摘要原文):「We performed a systematic BLAST analysis of 929 human disease gene entries associated with at least one mutant allele in the Online Mendelian Inheritance in Man (OMIM) database against the recently completed genome sequence of *Drosophila melanogaster*. … Our analysis identified 714 distinct human disease genes (77% of disease genes searched) matching 548 unique *Drosophila* sequences.」
  出處:Reiter LT, Potocki L, Chien S, Gribskov M, Bier E (2001) *Genome Research* 11(6): 1114-1125. DOI 10.1101/gr.169101
  URL(PDF 原文):https://www.ncbs.res.in/sitefiles/A%20systemic%20analysis%20of%20human%20disease%20associated%20gene%20sequences%20in%20Drosophila%20melanogaster.pdf — **親讀**(直接用 Read 工具開啟 PDF 影像看到論文首頁與摘要全文)
  註:genome.cshlp.org 官方頁面本身因需登入被重導向擋下,改用上述機構典藏 PDF 副本親讀,PDF 抬頭明載「Downloaded from genome.cshlp.org」,可信為同一篇論文的忠實複本。
- **重要踩雷紀錄**:WebFetch 工具第一次「總結」同一份 PDF 時,回報了一個錯誤數字「Drosophila homologs for 177 (75%) of the 237 human disease genes」——這個數字在論文原文裡根本不存在,是 WebFetch 摘要模型的幻覺。改用 Read 工具直接看 PDF 影像後才抓到真正的摘要文字(929/714/77%)。此教訓已寫入回報末尾 MLD。
- 結論:使用者記憶「約 60%/75%」與原文不符,原文實際數字是 **77%(929 個 OMIM 疾病基因中,714 個在果蠅有同源序列,對應 548 個獨特果蠅基因)**。卡片若要用這個數字,應寫「77%」並註明「Reiter et al. 2001, Genome Research」,不要寫 60% 或 75%。

---

## 第二組:整個腦連接組計畫盤點

| 物種/計畫 | 使用者給的數字 | 查證結果 | 逐字引用 | URL / 親讀狀態 |
|---|---|---|---|---|
| C. elegans (White et al. 1986) | 302 顆神經元 | **證實**(次級來源交叉確認,原始 Royal Society 頁面 403 無法親讀) | 「the hermaphrodite nervous system has a total complement of 302 neurons」(WebSearch 對 royalsocietypublishing.org/doi/10.1098/rstb.1986.0056 摘要的合成引述,非我親自 WebFetch 到) | secondhand;原始頁 https://royalsocietypublishing.org/doi/10.1098/rstb.1986.0056 回傳 403,PubMed 頁面只顯示 cookie 提示。另有 Wikipedia 交叉確認引用同一篇 |
| 果蠅幼蟲 (Winding et al. 2023 Science) | 約 3,016 顆 | **證實** | 「which contains 3016 neurons and 548,000 synapses」 | 親讀,https://www.eurekalert.org/news-releases/981772(期刊發布的官方新聞稿,轉引論文摘要句) |
| 成年雌果蠅 FlyWire (Dorkenwald et al. 2024 Nature) | 約 139,255 顆 | **證實(前導版數字略有出入,見上方(d)節說明)** | 前導版:「∼130,000 neurons」;正式版精確數 139,255 為多方 secondhand 一致引用 | bioRxiv 親讀(見上);Nature 正式版 403 無法親讀 |
| MaleCNS (Berg et al. 2026 Cell) | 166,691 顆 | **證實,與主對話已驗數字完全一致** | 「We now present the connectome of the entire *Drosophila* male central nervous system. This contains 166,691 neurons spanning the brain and ventral nerve cord, fully proofread and comprehensively annotated including fruitless and doublesex expression and 11,691 cell types.」 | 親讀,https://www.biorxiv.org/content/10.1101/2025.10.09.680999v1(bioRxiv 前導版,2025-10-09;正式版 *Cell* 189(18), 2026-09-03,DOI 見 cell.com/cell/fulltext/S0092-8674(26)00942-6,未另外親讀正式版但標題/期刊/數字與前導版一致) |
| 小鼠 1mm³ MICrONS (Nature 2025) | 約 20 萬顆神經元/5 億突觸 | **與記憶不完全相符 — 官方頁數字是「20萬+顆細胞、12萬顆神經元、5.23億個突觸」** | 「The anatomical data contains more than an estimated 200,000 cells, and 120,000 neurons」;「Automated synapse detection measured more than 523 million synapses.」 | 親讀,https://www.microns-explorer.org/cortical-mm3(官方 MICrONS 專案頁) |
| 人類 H01 1mm³ (Shapson-Coe et al. 2024 Science) | 約 5.7 萬顆細胞 | **證實** | Research Article Summary 圖說逐字:「1.4 petabytes of EM data」「150 M synapses」「57,000 cells」;正文:「We reconstructed thousands of neurons, more than a hundred million synaptic connections, and all of the other tissue elements that comprise human brain matter」 | **親讀**(用 Read 工具直接看 Science 官方 Research Article Summary 頁面影像),出處:Shapson-Coe et al., *Science* 384, eadk4858 (2024), DOI: 10.1126/science.adk4858,PDF: https://dmg5c1valy4me.cloudfront.net/wp-content/uploads/2024/05/09142702/science.adk4858.pdf |
| 斑馬魚幼魚全腦 | (未指定數字,查其性質) | **查無「完整突觸解析度全腦連接組」,已有的是「全腦電顯資料集/投射體(projectome)」,非全突觸連接組** | 「Here we present ssEM data for a complete 5.5 days post-fertilisation larval zebrafish brain. … The resulting dataset can be analysed to reconstruct neuronal processes, allowing us to, for example, survey all the myelinated axons (the projectome).」 | 親讀(Read PDF),Hildebrand et al. 2017 *Nature* / bioRxiv 前導版 https://www.biorxiv.org/content/10.1101/134882.full.pdf(DOI 10.1101/134882)。後續 Svara et al. 2022 據 WebSearch 合成摘要聲稱做到全腦突觸解析度重建(次級來源,未親讀原文,標「未查證」) |
| 小鼠全腦連接組正式計畫 (NIH BRAIN CONNECTS) | 2023 起 | **證實** | 「In 2023, the NIH launched the $150 million BRAIN Initiative Connectivity Across Scales (BRAIN CONNECTS) program, funding 11 projects over 5 years」(WebSearch 對 NIH/NINDS 官方頁與新聞稿的合成引述) | secondhand;官方頁 https://braininitiative.nih.gov/funding-opportunies/brain-initiative-connectivity-across-scales-brain-connects-comprehensive-0 重導向到 nih.gov/brain 首頁,grants.nih.gov RFA 頁面(RFA-NS-22-048)403 無法親讀原文公告 |
| 2025-2026 新的全腦連接組發表/宣布 | (查新) | **有,列出如下** | 見下 | 見下 |

**2025-2026 新進展(次級來源,WebSearch 合成,未逐一親讀原始公告)**:
- 斑馬魚「Fish2」:Harvard/HHMI Janelia/Google Research 團隊正在完成人工驗證過的全腦突觸解析度連接組(進行中,尚未發表完整論文)。
- 蚊子:2026年8月,Greg Jefferis 與 Elizabeth Marin 獲 Wellcome Discovery Award,將產製雌性埃及斑蚊(*Aedes aegypti*)全腦連接組(剛獲經費,尚未有資料集)。
- 小鼠:Google Research 與合作者於 2023 年 9 月宣布規模最大的連接組計畫,目標是海馬迴等區域,屬於 NIH BRAIN CONNECTS 架構下的一部分,進行中。
- 上述三項均為「進行中/剛啟動」而非「已完成發表」,標「未查證是否已有完整資料集發表」,不誇大為「已完成」。

---

## 第三組:視覺在腦中的佔比

### 「約一半的靈長類皮質參與視覺」

**判定:證實是講獼猴(macaque),不是人類;出處是 Van Essen 2003,不是 Felleman & Van Essen 1991 本身給出這個百分比數字**

- 逐字引用(親讀,直接用 Read 工具看 PDF 影像):「Cortex that is predominantly or exclusively visual (blue shading) occupies about half (52%) of cortical surface area (as measured on the fiducial surface rather than on the flat map, which contains significant distortions). This greatly exceeds the amount devoted to other modalities: somatosensory (green, 10%), auditory (red, 3%), motor (magenta, 8%), and olfactory (brown, 1%).」
  出處:David C. Van Essen (2003) “Organization of Visual Areas in Macaque and Human Cerebral Cortex”,收錄於 *Visual Neurosciences* (Chalupa & Werner, eds.),submitted 2002-03-20
  URL:https://www.cns.nyu.edu/csh/csh04/Articles/Vanessen-03.pdf — **親讀**
  **這段文字明確是描述圖1的獼猴皮質圖(Figure 1 shows the estimated extent of visual cortex in the macaque)**,不是人類。
- 該圖的邊界劃分依據 Felleman & Van Essen 1991 的分析(原文:「The dotted lines on the flat map represent the estimated boundary between regions dominated by different modalities, based on the analysis of Felleman and Van Essen (1991).」),所以「52%/約一半」這個具體百分比數字是 **Van Essen 2003 算出來的,引用 1991 年論文的皮質區劃分方法**,不是 1991 年論文本身寫出「一半」這個字。使用者記憶把這句話的出處指向 Felleman & Van Essen 1991,**與原文不完全相符**——1991 年論文(*Cerebral Cortex* 1:1-47)本身我沒有找到「一半」的逐字句(原始 PDF 過大無法親讀,故此點對 1991 年論文本身標「未查證」);但確定 52% 這個數字、以及它是講獼猴不是人類,來自 Van Essen 2003 且已親讀原文。
- **人類的對應整體百分比:查無**。同一篇 Van Essen 2003 論文的「人類」章節(第8頁)只給**逐區域**的數字,例如:「The estimated surface area of V1 on the atlas map … is 21 cm², or 2.2% of cerebral cortex. This is about one-sixth of its fractional occupancy on the macaque atlas.」(人類 V1 佔 2.2% 皮質面積,對照獼猴 V1 佔 13%)——**親讀確認,同一 URL**。論文全文沒有給出人類「視覺皮質佔全部皮質」的單一總百分比,只有逐區比較。這點對卡片設計很關鍵:**不能直接把「獼猴 52%」套用成「人類也約一半」**,原始文獻本身沒有算出人類的對應總數。

### 人類視覺皮質佔大腦皮質比例(可親讀數字)

**判定:查無單一權威總百分比數字**(見上,Van Essen 2003 只給逐區域比例,未給人類視覺總皮質佔比)。若卡片需要一個人類數字,目前查到最接近的僅是「人類 V1 佔 2.2% 皮質面積」這一個分區數字,不能等同「全部視覺相關皮質佔比」。**建議卡片誠實寫成**:「科學家估計獼猴猴腦裡,大約一半的大腦皮質參與處理視覺(Van Essen 2003);人類的視覺相關腦區分布更廣、範圍還在持續研究中,目前沒有一個公認的總百分比。」

### 人類腦神經元總數 86×10⁹

**判定:證實(數字對,但精確度有學界爭議,附帶不確定範圍)**

- 逐字引用(轉引自 2025 年一篇檢視論文對 Azevedo et al. 2009 摘要的直接引述):「We find that the adult male human brain contains on average 86.1 ± 8.1 billion NeuN-positive cells ("neurons").」
  出處:Azevedo FA, Carvalho LR, Grinberg LT, et al. (2009) "Equal numbers of neuronal and nonneuronal cells make the human brain an isometrically scaled-up primate brain." *Journal of Comparative Neurology* 513(5): 532-541.
  URL:https://pmc.ncbi.nlm.nih.gov/articles/PMC11884752/ — **secondhand**(這是 2025 年一篇回顧論文《Eighty-six billion and counting》裡對 Azevedo 原文的逐字轉引,我沒能直接開到 Azevedo 2009 原始論文本身,Wiley 頁面只給摘要頁未含此句,researchgate/academia.edu 版本本次未進一步親讀)
  該回顧論文並指出這個數字的統計爭議:僅用 4 個樣本點算出的 86.1 billion,若用嚴謹的 95% 信賴區間計算,合理範圍應是 **73.1 billion 至 99.0 billion**。
- 結論:86×10⁹(常寫作「約860億」)這個數字確實出自 Azevedo et al. 2009,與使用者記憶相符,可以用在卡片上,但嚴謹起見可以加註「±8 billion」或「估計範圍」字樣,不寫成絕對精確值。

### 結論寫法建議(給卡片設計參考,非查證項目本身)

果蠅的「60%」是**神經元顆數佔比**(視葉+視覺投射神經元 / 全部神經元);
獼猴的「52%/約一半」是**大腦皮質表面積佔比**(視覺為主的皮質區域 / 全部大腦皮質表面積),且講的是獼猴不是人類,人類沒有對應的單一總百分比數字。
兩者口徑完全不同(顆數 vs. 面積;昆蟲全腦 vs. 靈長類新皮質的一部分),**不能直接說「果蠅 60% ≈ 獼猴一半,所以差不多」**。卡片上誠實的寫法建議:「果蠅和靈長類動物都把很大一部分的腦拿來處理視覺,但因為量的方式不一樣(果蠅算的是神經細胞的數量,靈長類算的是腦表面積),没有辦法直接比較兩個數字誰大誰小——但都說明了視覺對這些動物有多重要。」

---

## 與主對話記憶不符的清單(重點摘要)

1. **(e) 果蠅-人類疾病基因同源比例**:記憶寫「約 60%/75%」,**Reiter et al. 2001 原文親讀確認實際數字是 77%**(929 個 OMIM 疾病基因中 714 個/77% 在果蠅有同源序列,對應 548 個獨特果蠅基因)。60% 於原文中查無出處。
2. **「約一半靈長類皮質參與視覺」的出處**:記憶認為可能出自 Felleman & Van Essen 1991,**實際「52%/一半」這個具體百分比數字親讀確認出自 Van Essen 2003**(該文引用 1991 年的皮質區劃分方法算出),且明確講的是**獼猴**,人類沒有對應的單一總百分比(只有逐區域數字,如人類 V1=2.2%)。
3. **MICrONS 小鼠數字**:記憶寫「約20萬顆神經元/5億突觸」,官方頁面親讀顯示應拆成「>20萬顆細胞、其中12萬顆神經元、5.23億個突觸」——顆細胞數與神經元數不是同一件事,記憶把兩者混在一起了。
4. **FlyWire 精確神經元數**:bioRxiv 前導版親讀是「約13萬(∼130,000)」,常被引用的精確數字「139,255」只在 secondhand 來源(Nature 官方頁 403 無法親讀)中確認,兩者屬於前導版與正式版之差,非錯誤但需註明。

其餘各項(Morgan 1910 年份、世代時間、Brand & Perrimon 1993、hemibrain「腦小到能逐片重建」的説法、C. elegans 302、幼蟲 3016、MaleCNS 166,691、H01 5.7萬顆/1.5億突觸、Azevedo 860億)皆與主對話記憶**證實相符**。斑馬魚全腦、小鼠全腦計畫細節、2025-2026 新公告屬「查無完整定論」或「secondhand」,已在上方逐項標注,不得當作卡片上的確定事實直接使用。

---

## 反向檢查

指令與輸出原文:

```
$ git status --porcelain
?? docs/research_context_cards.md
```

（僅此一行，符合預期；交辦前 rev-parse HEAD 輸出 cc1d138b14ec7133ed549febcec2a9029f2b083f 與主線給定值一致，未做任何其他檔案變更、未 git add、未 git commit。）

---

## 侷限

- 多個 Nature.com、Science.org、genome.cshlp.org、grants.nih.gov、royalsocietypublishing.org 頁面因登入牆/403 無法親讀,改用 bioRxiv 前導版、機構典藏 PDF、官方新聞稿或次級摘要替代,並在每一條逐項標明「親讀」或「secondhand」,沒有混用。
- WebFetch 工具至少一次對同一份 PDF 產生幻覺數字(Reiter 論文的「177/237/75%」),已改用 Read 工具直接看 PDF 影像逐字核對後推翻,詳見(e)節。這代表 WebFetch 的「摘要」不能直接信任為逐字引用,尤其是 PDF。
- 斑馬魚、小鼠全腦連接組進度、2025-2026 新公告均屬進行中/剛啟動,沒有完整已發表資料集可親讀,標記為「查無/未查證」而非硬掰成「已完成」。
- 人類視覺皮質佔比沒有查到與獼猴 52% 對等的單一總百分比數字,已如實標記「查無」,並在結論建議卡片用誠實、不直接比較兩物種數字的寫法。

---

## MLD

**M(這次做錯/卡住什麼)**:WebFetch 工具對同一份 Reiter 2001 PDF 第一次總結時捏造了一個不存在的數字(177/237/75%),與後來用 Read 工具直接看 PDF 影像得到的真實摘要(929/714/77%)完全對不上;若沒有再用 Read 工具交叉驗證,這個假數字就會被寫進給小孩看的教育卡片。另外多個 Nature/Science/NIH 官方頁面被登入牆擋下,花了不少來回試 PMC/bioRxiv/機構典藏等替代路徑,其中好幾次都猜測性地嘗試了未經確認的 PMC ID(如 PMC11742370),結果命中完全無關的論文——這正是規則裡警告過的「冷 fetch 猜的識別碼」陷阱,雖然此次沒有把它當成正確結果採信,但浪費了來回。

**L(學到什麼可複用)**:WebFetch 對 PDF 的「摘要」不能當成逐字引用的最終依據,尤其是牽涉具體數字時——遇到 WebFetch 因 PDF 過大/加密而回報「無法解析」或給出的數字看起來可疑時,下一步應該直接用 Read 工具把已存到本機的 PDF 當圖片讀,親眼看論文原始排版的摘要文字,比再問一次 WebFetch 可靠很多。另外,官方期刊網站(Nature/Science/genome.cshlp.org)在自動化工具面前普遍設了登入牆,遇到 403 時,bioRxiv 前導版、Research Article Summary 頁面、機構典藏(如 ncbs.res.in、par.nsf.gov)、官方項目頁(如 microns-explorer.org、bdsc.indiana.edu)往往能拿到足夠接近原文的內容,且經常本身就是可以直接 Read 成圖片的完整摘要頁,比硬啃收費牆更有效率。

**D(希望環境/工具多給什麼)**:如果有一個「先查某 DOI/PMID 在 Unpaywall 或 Europe PMC 是否有開放版本」的固定查詢步驟(而不是每次都要 WebSearch 現找替代連結),應該能省下這次任務裡至少三、四輪來回搜尋替代來源的時間。另外,若能知道哪些期刊網域(nature.com、science.org、genome.cshlp.org、grants.nih.gov、royalsocietypublishing.org)已知會擋 WebFetch,可以直接跳過第一次嘗試,省下確定會 403 的那幾次呼叫。
