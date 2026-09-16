# 透視果蠅 · Fly Explorer

**你看到亮起來的,是一顆真的腦在算。**

把 MaleCNS 雄性果蠅中樞神經系統連接組(140,024 顆有真實三維座標的神經元)做成給國小到國中生看的 3D 網站,
重播我們自己跑出來的逃跑反射模擬:眼睛看到東西撲過來 → 巨纖維放電 → 跳躍肌與翅膀肌的神經細胞動起來。
三條路:**小朋友版**(一步一步捲、有問答)、**專業版**(同一條路,完整數字、出處與模型限制)、**自由探索**(3D 舞台與 33 張說明卡)。中英雙語。

## 狀態(2026-09-16)

| 項目 | 狀態 |
|---|---|
| 3D 點雲、逃跑情境重播、身體線稿、肌肉圖解、電壓計 | 完成 |
| 33 張說明卡(小朋友 / 想知道更多 × 中 / 英),每個數字附出處與標記 | 完成,經一輪 validity-audit(內審 + 獨立冷審)|
| 字幕與介面雙語 | 完成;**英文翻譯尚未經母語者或第二模型複審** |
| 確定性閘門(見下)| 全部 PASS |
| 複眼六角座標「哪個方向是正前方」 | **未驗證**,字幕與卡片都明寫 |
| 模型會不會自己停 | **不會**(跑到 600 ms 仍在放電);250 ms 之後的收尾是我們加的,畫面用洋紅標示 |
| 語音解說 | 未做 |

## 誠實標示

畫面上每樣東西都分得出「資料」與「我們畫的」:

- **發光**(綠)= 真實神經元的位置與模擬的放電。
- **洋紅** = 模型算不出、我們注入的(視覺前端的逼近偵測)或我們加的(結局)。
- **冷灰線稿** = 我們畫的身體,連接組裡沒有。
- **琥珀** = 運動神經元到肌肉那一段,連接組沒有;只有時機是真的。

卡片上的每個數字帶三種標記:● 我們的腳本從資料算出來的;◆ 我們親自讀過的論文;○ 二手轉引、示意或未查證。
規範在 `docs/visual_provenance.md`。

## 模型限制(先講清楚)

- 引擎是 leaky integrate-and-fire(參數沿 Shiu et al. 2024),只有化學突觸,沒有電突觸、沒有神經調節。
- 視覺前端算不出逼近刺激,所以「眼睛看到東西」那一步是注入的。
- 教科書裡巨纖維→PSI→翅膀肌的中繼在這個情境裡沒放電;模擬裡翅膀訊號走了另一條路。卡片照模擬講,並註明與教科書不同。
- 模擬比真果蠅慢,也不會自己停。

## 跑起來

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # dist/
```

手機直式 308 px 是驗收基準。桌機用 `?preset=low` 可以模擬手機路徑。深連結:`?track=kid|more|free`、`?lang=en`、`?cap=0`(無字幕)、`?card=<id>`。

## 閘門(改內容前後都跑)

```bash
python3 scripts/jargon_lint.py          # 小朋友層不得出現術語清單,首次出現要當場解釋(中英)
python3 scripts/audit_numbers.py        # 正文裡每個數字必須在事實欄或 docs/ 找得到(中英)
python3 scripts/audit_claims.py         # 事實欄的來源路徑必須存在,且不得指向未公開的研究倉
python3 scripts/verify_stages.py        # 字幕裡的毫秒數必須等於出貨情境的實際放電時刻(中英)
python3 scripts/retraction_lint.py      # 已撤回的說法不得再出現
python3 scripts/citation_record_lint.py # ◆ 只能給親讀過的文獻
python3 scripts/lang_residue.py         # 英文版四個畫面不得殘留中文(需 vite build + Chrome)
```

每支都有 `--self-test` 或負向案例,證明它擋得住錯的東西。

## 資料與出處

- **連接組**:MaleCNS v1.0,Berg et al. 2026,CC BY 4.0,https://male-cns.janelia.org 。本倉只含衍生資料(座標、出貨情境的放電記錄),原始 1.1 GB 權重表請自行下載。
- **模型**:Shiu et al. 2024 的 LIF 參數。引擎本身在未公開的研究倉;卡片引用的量測腳本已複製到 `scripts/fly/`(見該目錄 README)。
- **數字的出處鏈**:`docs/verification_log.md`、`docs/data_facts.md`、`docs/research_context_cards.md`。

## 授權

程式 MIT(`LICENSE`);內容 CC BY 4.0(`LICENSE-CONTENT.md`);資料 CC BY 4.0(MaleCNS)。

---

## English

An educational 3D site for kids and teens built on the real MaleCNS male fruit-fly connectome (140,024 neurons at their true 3D positions), replaying an escape-reflex simulation we ran ourselves. Three tracks: Kids (scroll-driven, with quizzes), In depth (same path with full numbers, sources and model limits), Explore freely (3D stage + 33 cards). Chinese and English.

**What glows is real data; line art is ours.** Green glow = real neuron positions and simulated spikes. Magenta = injected by us (the model cannot compute looming) or added by us (the ending). Grey line art = the body we drew. Amber = nerve-to-muscle, absent from the connectome. Every number on a card carries a mark: ● measured by our scripts, ◆ from a paper we read first-hand, ○ secondhand or illustrative.

Known limits: leaky integrate-and-fire only (Shiu et al. 2024 parameters), chemical synapses only; the visual front end cannot compute looming; the textbook GF→PSI→wing relay never fires in this scenario; the model is slower than a real fly and never stops on its own. The eye's "which way is forward" convention is unverified. The English translation has not been reviewed by a native speaker.

Data: MaleCNS v1.0 (Berg et al. 2026, CC BY 4.0). Code MIT, content CC BY 4.0.
