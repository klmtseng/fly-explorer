# scripts/fly — 從研究倉複製過來的量測腳本

網站卡片的事實欄引用這四支腳本與一份輸出。研究倉(`fly`,含 1.1 GB 連接組原始資料)不公開,
所以把**產生數字的那幾支腳本原樣複製**到這裡(來源 commit `9602714`,2026-09-16 複製),讓每個數字仍指得出產生它的程式。

| 檔案 | 產生哪些數字 |
|---|---|
| `io_inventory.py` → `out/io_inventory.json` | 感覺/運動神經元清冊(15,912 / 815、各類感覺計數) |
| `escape_path.py` | 巨纖維→TTMn 90 個突觸、巨纖維→DLMn 0 條邊、PSI 路徑邊數 |
| `mb_circuit_stats.py` | 蘑菇體可塑突觸 61,210 條等 |
| `shuffle_csr.py` | 保度數打亂對照(真實 207 Hz vs 打亂三 seed 0) |
| `receptor_types.py` | 標註檔 receptorType 三種值的計數(見 docs/data_facts.md) |

**重跑需要原始資料**:MaleCNS v1.0 的 `connectome-weights-male-cns-v1.0-minconf-0.5.feather`(1.1 GB)與
`body-annotations-male-cns-v1.0-minconf-0.5.feather`,自 https://male-cns.janelia.org/download/ 下載(CC-BY 4.0),
放到腳本開頭 `DATA` 指的位置。沒有原始資料時,這些腳本只是「數字從哪來」的可讀憑證。
