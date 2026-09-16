/* 肌肉,與「運動神經元 → 肌肉」那一段(④ 我們畫的)。
 *
 * 連接組裡沒有肌肉,也沒有運動神經元接到肌肉的那個接點(神經肌肉接合)。畫面上若只有神經元亮、
 * 翅膀卻動了,中間就缺一段——使用者看出來了。這裡把缺的那段畫出來,並用**不同顏色**明說它不是資料:
 *   琥珀色 MUSCLE_COLOR、線稿、普通混合、在 bloom 之後另開一個 scene 直接畫(所以不會發光)。
 *   **時機**跟著真實運動神經元的亮度(②:DLMn/DVMn 24 顆、TTMn 2 顆,位置是它們真實的細胞體座標);
 *   **形狀與位置**是示意(○):胸腔裡的肌肉走向按教科書畫——
 *     DLM(背縱肌)沿前後軸躺在背側、DVM(背腹肌)上下走、TTM(跳躍肌)從背板斜下到中腳基部。
 *   出處規範 docs/visual_provenance.md ④。
 */
import * as THREE from 'three';
import type { EdgeLayer } from './edges';
import type { ShellAnchors } from './shell';

export const MUSCLE_COLOR = 0xE8A34A;

export interface Muscles {
  group: THREE.Group;
  /** 每幀:用線層的節點亮度(全解析度)更新肌肉與連線的濃淡 */
  update(nodeBright: Float32Array): void;
}

export function buildMuscles(a: ShellAnchors, edges: EdgeLayer): Muscles {
  const { c, r } = a.thorax;
  const base = new THREE.Color(MUSCLE_COLOR);

  // ---- 肌纖維(每側:DLM ×3、DVM ×2、TTM ×1),每條畫成兩根平行線讓它比神經連線「粗」一點
  type Fiber = { from: THREE.Vector3; to: THREE.Vector3; kind: 'wing' | 'jump'; sx: number; nodes: number[] };
  const fibers: Fiber[] = [];
  for (const sx of [-1, 1]) {
    for (let k = 0; k < 3; k++) fibers.push({ kind: 'wing', sx, nodes: [],
      from: new THREE.Vector3(sx * r.x * (0.12 + 0.11 * k), c.y + r.y * (0.66 - 0.09 * k), c.z - r.z * 0.72),
      to:   new THREE.Vector3(sx * r.x * (0.12 + 0.11 * k), c.y + r.y * (0.66 - 0.09 * k), c.z + r.z * 0.72) });
    for (let k = 0; k < 2; k++) fibers.push({ kind: 'wing', sx, nodes: [],
      from: new THREE.Vector3(sx * r.x * 0.46, c.y + r.y * 0.78, c.z + r.z * (-0.35 + 0.55 * k)),
      to:   new THREE.Vector3(sx * r.x * 0.58, c.y - r.y * 0.55, c.z + r.z * (-0.30 + 0.55 * k)) });
    const legT2 = a.legBase[sx < 0 ? 2 : 3];                // 腳順序 L1 R1 L2 R2 L3 R3 → 中腳
    fibers.push({ kind: 'jump', sx, nodes: [],
      from: new THREE.Vector3(sx * r.x * 0.30, c.y + r.y * 0.84, c.z), to: legT2.clone() });
  }
  // ---- 把真實運動神經元(細胞體座標)分派到同側的肌纖維:翅膀 24 顆輪流配 5 條、跳躍 2 顆配 TTM
  const assign = (ids: number[] | undefined, kind: 'wing' | 'jump') => {
    const cnt: Record<number, number> = { [-1]: 0, [1]: 0 };
    for (const k of ids ?? []) {
      const sx = edges.npos[k * 3] < 0 ? -1 : 1;
      const pool = fibers.filter(f => f.kind === kind && f.sx === sx);
      pool[cnt[sx]++ % pool.length].nodes.push(k);
    }
  };
  assign(edges.nodesByStage['wing'], 'wing');
  assign(edges.nodesByStage['jump'], 'jump');

  // ---- 幾何:肌纖維(兩根平行線)+ 連線(細胞體 → 纖維中點)
  const fPos: number[] = [], lPos: number[] = [];
  const links: { node: number; fiber: number }[] = [];
  fibers.forEach((f, fi) => {
    // 單線(2026-09-16 使用者:太搶眼、要細)。第一版每條纖維畫兩條平行線充當「粗」,WebGL 線寬固定 1px,
    // 想細只能拿掉那條平行線、再把不透明度與亮度上限壓低。
    fPos.push(f.from.x, f.from.y, f.from.z, f.to.x, f.to.y, f.to.z);
    const mid = f.from.clone().lerp(f.to, 0.5);
    for (const k of f.nodes) { lPos.push(edges.npos[k * 3], edges.npos[k * 3 + 1], edges.npos[k * 3 + 2], mid.x, mid.y, mid.z); links.push({ node: k, fiber: fi }); }
  });
  const mkLines = (pos: number[]) => {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
    const col = new THREE.BufferAttribute(new Float32Array(pos.length), 3); col.setUsage(THREE.DynamicDrawUsage);
    g.setAttribute('color', col);
    // 普通混合、不寫深度、不測深度:它是畫在 bloom 之後的圖解層,永遠在上面,而且不會發光
    return new THREE.LineSegments(g, new THREE.LineBasicMaterial({ vertexColors: true, transparent: true, opacity: 0.45,
      blending: THREE.NormalBlending, depthWrite: false, depthTest: false }));
  };
  const fiberLines = mkLines(fPos), linkLines = mkLines(lPos);
  const group = new THREE.Group(); group.add(fiberLines, linkLines); group.name = 'muscles';

  const setSeg = (attr: THREE.BufferAttribute, seg: number, k: number) => {
    // 濃淡用「顏色往黑收」表現:普通混合下等同不透明度;不用加色、不用亮度疊加
    const cr = base.r * k, cg = base.g * k, cb = base.b * k;
    attr.setXYZ(seg * 2, cr, cg, cb); attr.setXYZ(seg * 2 + 1, cr, cg, cb);
  };
  function update(nodeBright: Float32Array) {
    const fa = fiberLines.geometry.getAttribute('color') as THREE.BufferAttribute;
    const la = linkLines.geometry.getAttribute('color') as THREE.BufferAttribute;
    fibers.forEach((f, fi) => {
      let act = 0; for (const k of f.nodes) act = Math.max(act, nodeBright[k]);   // 取最大:24 顆輪流放電,平均會被稀釋
      const kk = 0.10 + 0.50 * Math.min(1, act * 1.5);          // 靜止極淡,全力也只到六成:它是圖解,不能壓過資料
      setSeg(fa, fi, kk);
    });
    links.forEach((l, li) => setSeg(la, li, 0.06 + 0.54 * Math.min(1, nodeBright[l.node] * 1.5)));
    fa.needsUpdate = true; la.needsUpdate = true;
  }
  update(new Float32Array(edges.nNodes));
  return { group, update };
}
