/* 實體小視窗(PiP):果蠅身體在現實中會做什麼。
 *
 * 出處規範(docs/visual_provenance.md):
 *   形狀 = ④我們畫的(線稿不發光);驅動它的數字 = ②真實放電(線層節點亮度,全解析度)。
 *   我們只知道「哪條肌肉的神經元在放電」,**不知道**肌肉收縮多少、身體位移多少——
 *   連接組沒有肌肉、沒有物理。所以動作的**幅度是示意**,方向與時機是資料。標籤明寫。
 *
 * 用同一個 WebGLRenderer 以 scissor 在 #pip 方框的螢幕區域再畫一次:獨立場景、獨立相機(側視)。
 */
import * as THREE from 'three';
import { buildShell, animateShell, type Shell } from './shell';
import type { SomaCloud } from './soma';
import type { EdgeLayer } from './edges';

export interface Pip {
  render(renderer: THREE.WebGLRenderer): void;
  /** 每個播放幀呼叫一次:從線層節點亮度算驅動強度(帶包絡,免得 2 顆 TTMn 的單次放電一閃就沒) */
  setFrame(edges: EdgeLayer | null, frameMs: number): void;
  drives: { wing: number; jump: number; proboscis: number };
  setLang(l: 'zh' | 'en'): void;
}

export function createPip(cloud: SomaCloud, box: HTMLElement, readout: HTMLElement): Pip {
  let lang: 'zh' | 'en' = 'zh';
  const RD = { zh: ['翅膀肌神經 DLMn/DVMn', '跳躍肌神經 TTMn', ' · 前奏(注入)'], en: ['wing nerves DLMn/DVMn', 'jump nerves TTMn', ' · prelude (injected)'] };
  const scene = new THREE.Scene();
  // PiP 裡線稿亮一點(它是這個視窗的主角)並加平塗淡色;仍是普通混合、不經 bloom,不發光
  const shell: Shell = buildShell(cloud, { opacity: 0.55, tint: true });
  scene.add(shell.group);

  const bb = new THREE.Box3().setFromObject(shell.group);
  const size = bb.getSize(new THREE.Vector3()), ctr = bb.getCenter(new THREE.Vector3());
  const cam = new THREE.PerspectiveCamera(35, 1.6, 1, 20000);
  const drives = { wing: 0, jump: 0, proboscis: 0 };
  let frameMs = 0;

  function fit() {
    const rect = box.getBoundingClientRect();
    cam.aspect = Math.max(0.5, rect.width / Math.max(1, rect.height));
    // 側後上方 3/4 視角(從 +X 看,抬高約 25°):看得到平貼背上的翅膀、腹部橫環與腳
    const t = Math.tan(THREE.MathUtils.degToRad(cam.fov) / 2);
    // 留邊:垂直要避開標題與頁尾——兩者高度**量實際 DOM**(手機上頁尾會摺成三行,寫死 34px 時果蠅擠進標題裡)
    const footH = box.querySelector('.pipFoot')?.getBoundingClientRect().height ?? 34;
    const headH = box.querySelector('.pipTitle')?.getBoundingClientRect().height ?? 16;
    const footFrac = footH / Math.max(1, rect.height), headFrac = (headH + 4) / Math.max(1, rect.height);
    const distH = (size.y * 0.80) / (t * Math.max(0.2, 1 - footFrac - headFrac)), distW = (size.z * 0.62) / (t * cam.aspect);
    const d = Math.max(distH, distW);
    // lookAt 目標往下移 → 果蠅在框內上移,落在標題與頁尾之間的正中
    const target = ctr.clone(); target.y -= (footFrac - headFrac) * d * t;
    cam.position.set(target.x + d * 0.88, target.y + d * 0.44, target.z + d * 0.18);
    cam.up.set(0, 1, 0); cam.lookAt(target); cam.updateProjectionMatrix();
  }

  function setFrame(edges: EdgeLayer | null, ms: number) {
    frameMs = ms;
    if (!edges) return;
    const mean = (ids: number[] | undefined) => ids?.length ? ids.reduce((s, i) => s + edges.nodeBright[i], 0) / ids.length : 0;
    const mx   = (ids: number[] | undefined) => ids?.length ? Math.max(...ids.map(i => edges.nodeBright[i])) : 0;
    // 翅:DLMn+DVMn 24 顆取平均;跳躍:TTMn 只有 2 顆且各放電 1 次,取最大值並帶包絡撐住
    const wingNow = mean(edges.nodesByStage['wing']);
    const jumpNow = mx(edges.nodesByStage['jump']);
    drives.wing = Math.max(wingNow * 1.6, drives.wing * 0.90);
    drives.jump = Math.max(jumpNow * 1.2, drives.jump * 0.94);
    drives.wing = Math.min(1, drives.wing); drives.jump = Math.min(1, drives.jump);
    // 兩個讀數各自一個 span:桌機同一行、手機各佔一行(CSS 切換),免得在窄框裡折成三行擠掉果蠅
    readout.innerHTML =
      `<span class="rd">${RD[lang][0]} ${(drives.wing * 100).toFixed(0)}%</span><span class="sep"> · </span>` +
      `<span class="rd">${RD[lang][1]} ${(drives.jump * 100).toFixed(0)}%${frameMs < 0 ? RD[lang][2] : ''}</span>`;
  }

  function render(renderer: THREE.WebGLRenderer) {
    const rect = box.getBoundingClientRect();
    if (rect.width < 40 || rect.height < 40) return;
    fit();
    // 翅膀拍動相位用**模擬時間**推進,不用牆鐘:暫停時停住、拖曳時一致。
    // 果蠅翅膀拍動約 200 Hz = 週期 5 ms(文獻常值,本專案未親驗)→ 1ms/幀下每 5 幀一拍。
    animateShell(shell, drives, frameMs / 1000);
    // ⚠️ setViewport/setScissor 吃 **CSS 像素**,three.js 內部會再乘 devicePixelRatio。
    // 第一版餵了裝置像素:桌機 DPR=1 無感,手機 DPR=3 把 PiP 畫到螢幕外、且主畫面 viewport 被弄壞
    // (使用者實機「連線後沒有反應」;DPR=3 無頭截圖重現)。用 CSS 像素,並存/還原原本的 viewport 與 scissor。
    const cssH = renderer.domElement.clientHeight || window.innerHeight;
    const x = rect.left, y = cssH - rect.bottom, w = rect.width, h = rect.height;
    const savedVp = new THREE.Vector4(), savedSc = new THREE.Vector4();
    renderer.getViewport(savedVp); renderer.getScissor(savedSc);
    const savedScTest = renderer.getScissorTest();
    renderer.setScissorTest(true);
    renderer.setViewport(x, y, w, h); renderer.setScissor(x, y, w, h);
    renderer.setClearColor(0x0c1210, 1); renderer.clear(true, true, false);
    renderer.render(scene, cam);
    renderer.setViewport(savedVp); renderer.setScissor(savedSc); renderer.setScissorTest(savedScTest);
    renderer.setClearColor(0x000000, 1);
  }
  return { render, setFrame, drives, setLang(l) { lang = l; } };
}
