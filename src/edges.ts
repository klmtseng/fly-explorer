/* 逃跑路徑的**真實連線**。
 *
 * 資料:public/data/escape_edges.json(scripts/export_edges.py),1,774 條連接組裡真實存在的
 * 前向邊(偵測器 → 下行 → premotor → 肌肉)。族群清單來自 trace_drivers.py 的實測追蹤。
 *
 * 出處規範(docs/visual_provenance.md):
 *   連線本身 = 資料(①),可以發光;但「畫成直線」是示意——真實軸突不是直線。
 *   所以線很細、底色很淡,發光只跟著**來源端的真實放電**走,不加任何假的流動動畫。
 *   兩端顏色各取自己端點的亮度 → 訊號經過時線會從來源端往目的端變亮,那是資料驅動的視覺,不是特效。
 *   興奮性(權重>0)綠白、抑制性(權重<0)偏青,方便看出哪些線在壓制。
 */
import * as THREE from 'three';
import type { SomaCloud } from './soma';

export interface EdgeLayer {
  lines: THREE.LineSegments;
  nodeBright: Float32Array;           // 每個節點的當前亮度(全解析度,由 applyFrame 側錄)
  npos: Float32Array;                 // 每個節點的細胞體座標(xyz 連續),給肌肉層畫「神經→肌肉」連線用
  watch: Map<number, number>;         // 原始 soma 索引 → 節點序號
  update(): void;                     // 每幀把 nodeBright 推進頂點顏色
  nEdges: number; nNodes: number;
  /** 各階段(detect/descend/premotor/jump/wing)的節點序號,PiP 用來把真實放電換成驅動強度 */
  nodesByStage: Record<string, number[]>;
}

export async function loadEdges(url: string, cloud: SomaCloud): Promise<EdgeLayer> {
  const j = await (await fetch(url)).json() as {
    nodes: { i: number; t: string; s: string }[]; edges: [number, number, number][] };
  const N = j.nodes.length, E = j.edges.length;

  const npos = new Float32Array(N * 3);
  const watch = new Map<number, number>();
  j.nodes.forEach((nd, k) => {
    const [x, y, z] = cloud.posOfOriginal(nd.i);
    npos[k*3] = x; npos[k*3+1] = y; npos[k*3+2] = z;
    watch.set(nd.i, k);
  });

  const pos = new Float32Array(E * 6);
  const col = new Float32Array(E * 6);
  const sign = new Float32Array(E);
  j.edges.forEach(([a, b, w], k) => {
    pos.set(npos.subarray(a*3, a*3+3), k*6);
    pos.set(npos.subarray(b*3, b*3+3), k*6+3);
    sign[k] = w >= 0 ? 1 : -1;
  });
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const colAttr = new THREE.BufferAttribute(col, 3); colAttr.setUsage(THREE.DynamicDrawUsage);
  geo.setAttribute('color', colAttr);

  // opacity 壓低:1,774 條線在加色混合下大量重疊,第一版 opacity 1 + REST 0.045 直接飽和成一團白,
  // 點雲整個被蓋掉(截圖第 0 幀無活動就已全白)。
  const mat = new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.18,
    blending: THREE.AdditiveBlending, depthWrite: false });
  const lines = new THREE.LineSegments(geo, mat);

  const nodeBright = new Float32Array(N);
  const nodesByStage: Record<string, number[]> = {};
  j.nodes.forEach((nd, k) => { (nodesByStage[nd.s] ||= []).push(k); });
  const EXC = new THREE.Color(0.45, 0.95, 0.62), INH = new THREE.Color(0.30, 0.75, 0.85);
  const REST = 0.004;   // 靜止時線幾乎看不見,只留一點結構——它是示意的直線,不該搶戲
  // 偵測器→下行那一束佔 88% 的邊(1,559/1,774),再壓一半,讓真正的傳導鏈(下行→premotor→肌肉)看得見
  const bundle = new Float32Array(E);
  j.edges.forEach(([a, b], k) => { bundle[k] = (j.nodes[a].s === 'detect') ? 0.30 : 0.8; });

  function update() {
    for (let k = 0; k < E; k++) {
      const [a, b] = j.edges[k];
      const base = sign[k] > 0 ? EXC : INH;
      // 來源端加權比目的端高:偵測器→巨纖維是單突觸,放電後 1.8ms 才到對面。
      // 那 3ms 裡線只亮來源那一頭,就是「訊號在突觸上、還沒到」——使用者實機看到這段像跳幀,
      // 因為來源端原本太暗看不見,巨纖維一亮整束才「砰」出來。
      const ba = (REST + Math.pow(nodeBright[a], 0.6) * 1.35) * bundle[k];  // 來源端:跟著來源放電
      const bb = (REST + Math.pow(nodeBright[b], 0.6) * 0.7)  * bundle[k];  // 目的端:跟著目的放電 → 方向感
      col[k*6]   = base.r * ba; col[k*6+1] = base.g * ba; col[k*6+2] = base.b * ba;
      col[k*6+3] = base.r * bb; col[k*6+4] = base.g * bb; col[k*6+5] = base.b * bb;
    }
    colAttr.needsUpdate = true;
  }
  update();
  return { lines, nodeBright, npos, watch, update, nEdges: E, nNodes: N, nodesByStage };
}
