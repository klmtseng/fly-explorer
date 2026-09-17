import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
import { EffectComposer, RenderPass, EffectPass, BloomEffect, ToneMappingEffect, ToneMappingMode } from 'postprocessing';
import { probeHardware, pickPreset, settingsFor } from './quality';
import { loadSoma, GROUPS } from './soma';
import { loadScenario, applyFrame, type Scenario } from './scenario';
import { loadEdges, type EdgeLayer } from './edges';
import { buildMuscles, type Muscles } from './muscles';
import stagesJson from '../content/stages.json';
import { createCards, srcText, storedLang } from './cards';
import { createLab } from './lab';
import tracksJson from '../content/tracks.json';
import { loadGauge, type Gauge } from './gauge';
import { buildShell } from './shell';
import { createPip, type Pip } from './pip';

const hw = probeHardware();
// ?preset=low|medium|high|ultra 強制品質檔:給無頭測試重現手機路徑(pixelRatio≠1),也讓使用者可手動降級
const _qp = new URLSearchParams(location.search).get('preset');
const S = settingsFor((['low','medium','high','ultra'] as const).includes(_qp as any) ? (_qp as any) : pickPreset(hw));

const renderer = new THREE.WebGLRenderer({
  antialias: S.preset !== 'low',
  powerPreference: 'high-performance',
  preserveDrawingBuffer: true,   // 截圖驗收需要,否則 drawImage(canvas) 讀回全黑
});
renderer.setPixelRatio(Math.min(window.devicePixelRatio, S.pixelRatio));
renderer.setSize(innerWidth, innerHeight);
renderer.setClearColor(0x000000, 1);  // 純黑:AgX 會抬升暗部,給 0x07090a 會被提成灰
renderer.domElement.style.touchAction = 'none';   // CSS 之外再設一次,避免被覆寫
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(45, innerWidth / innerHeight, 0.5, 8000);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.rotateSpeed = 0.7;
// 明確指定觸控手勢,不依賴預設值:單指旋轉、雙指縮放與平移。
// 使用者實機回報單指與雙指都轉不動,所以每一層都寫死。
// 兩指改 DOLLY_ROTATE(捏合縮放 + 兩指旋轉並存)。
// 使用者實機回報單指與兩指都轉不動——但兩指**縮放**是有效的,代表兩指事件確實
// 傳得到頁面,而原本 TWO 設成 DOLLY_PAN 本來就不含旋轉,所以「兩指轉不動」是設定造成的。
// 單指在 iframe 裡可能被宿主當成捲動攔走,那條路不可靠,所以把旋轉掛到可靠的兩指上。
controls.touches = { ONE: THREE.TOUCH.ROTATE, TWO: THREE.TOUCH.DOLLY_ROTATE };
controls.mouseButtons = { LEFT: THREE.MOUSE.ROTATE, MIDDLE: THREE.MOUSE.DOLLY, RIGHT: THREE.MOUSE.PAN };
controls.enableRotate = true;
// iOS Safari 在 iframe 裡會把單指拖曳當成捲動父頁。canvas 已設 touch-action:none,
// 這裡再擋一層 touchmove 的預設行為。
renderer.domElement.addEventListener('touchmove', e => e.preventDefault(), { passive: false });
// iOS Safari 的原生捏合縮放(gesture 事件)會搶走雙指:整頁被放大而不是果蠅被拉近。touch-action:none 不是每版都擋得住,再擋一層。
for (const ev of ['gesturestart', 'gesturechange', 'gestureend']) document.addEventListener(ev, e => e.preventDefault(), { passive: false });

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
// AgX 而非 ACES:cyberpunk-room 對「暗底+發光」場景實測過,ACES 會把暗部壓成死黑
// (近黑像素 15.0%→0.0%、暗部標準差 1.17→3.69)。我們正是那種場景。
const bloom = new BloomEffect({ intensity: S.bloomIntensity, luminanceThreshold: 0.12, luminanceSmoothing: 0.25, mipmapBlur: true });
bloom.blendMode.opacity.value = S.enableBloom ? 1 : 0;
composer.addPass(new EffectPass(camera, bloom, new ToneMappingEffect({ mode: ToneMappingMode.AGX })));

const $ = (id: string) => document.getElementById(id)!;

const TITLE = { zh: '透視果蠅 — 真的那一顆腦', en: 'Fly Explorer — a real fly connectome' };
/** 只換靜態文字(data-en/data-zh)、標題與 html lang。不碰 pip/gauge/圖例,所以可以在載入任何資料之前呼叫,
 *  首屏就是對的語言,不會先閃一秒另一種語言。完整的 applyLang() 在資料就緒後再跑一次。 */
function applyStaticLang(l: 'zh' | 'en') {
  document.documentElement.lang = l === 'en' ? 'en' : 'zh-Hant';
  document.title = TITLE[l];
  document.querySelectorAll<HTMLElement>('[data-en]').forEach(el => {
    if (el.dataset.zh === undefined) el.dataset.zh = el.textContent ?? '';
    el.textContent = l === 'en' ? el.dataset.en! : el.dataset.zh;
  });
}
applyStaticLang(storedLang());

(async () => {
  const t0 = performance.now();
  const cloud = await loadSoma('data/soma.bin', S.maxPoints);
  scene.add(cloud.points);
  const loadMs = performance.now() - t0;

  // 預設側視圖:身體前後軸(Z)水平、背腹軸(Y)垂直——文獻呈現果蠅 CNS 的標準角度。
  // 稍微偏角度讓兩側視葉有前後差,完全側面會疊在一起看不出深度。
  const DIR = new THREE.Vector3(0.92, -0.12, 0.36).normalize();

  // ④ 肌肉層(宣告放在外殼之前:setShell 會讀它,放後面是 TDZ,整頁載入失敗——本專案第二次):琥珀色,畫在 bloom 之後的獨立 scene(不發光)。連接組沒有「運動神經元→肌肉」這段,
  // 只畫神經元亮、翅膀卻動了,中間缺一段——使用者指出。形狀示意,時機來自真實運動神經元放電。
  let muscles: Muscles | null = null;
  const muscleScene = new THREE.Scene();
  // ④ 外殼:線稿不發光,預設顯示,可切換。規範 docs/visual_provenance.md
  const shell = buildShell(cloud);
  scene.add(shell.group);
  const shellBtn = document.getElementById('mShell')!;
  const setShell = (on: boolean) => { shell.group.visible = on; if (muscles) muscles.group.visible = on; shellBtn.setAttribute('aria-pressed', String(on)); };
  shellBtn.addEventListener('click', () => { setShell(!shell.group.visible); fitCamera(); });
  setShell(true);
  // 字幕開關:body.nocap 由 CSS 收掉字幕與計數;狀態存 localStorage;預設開(第一次來的人要靠字幕知道畫面在演什麼)
  const capBtn = document.getElementById('mCap')!;
  const setCap = (on: boolean) => { document.body.classList.toggle('nocap', !on); capBtn.setAttribute('aria-pressed', String(on)); try { localStorage.setItem('fly.cap', on ? '1' : '0'); } catch { /* ignore */ } };
  capBtn.addEventListener('click', () => { setCap(document.body.classList.contains('nocap')); if (!userMoved) fitCamera(); });
  { let on = true; try { on = localStorage.getItem('fly.cap') !== '0'; } catch { /* ignore */ }
    const q = new URLSearchParams(location.search).get('cap'); if (q !== null) on = q !== '0';   // ?cap=0:錄影/嵌入/無頭截圖用
    setCap(on); }
  // 取景用的包圍盒:身體可見時是整隻果蠅(含腹部與腳),否則只有神經系統。
  // 兩者都以 CNS 包圍盒中心為原點(shell 與點雲同座標系),所以只換 half-size。
  const shellBox = new THREE.Box3().setFromObject(shell.group);
  const cloudBox = new THREE.Box3(cloud.size.clone().multiplyScalar(-0.5), cloud.size.clone().multiplyScalar(0.5));
  /** 取景用的真實包圍盒(不是對原點對稱的那種:腳向下、翅膀向後都不對稱,對稱盒會浪費三成畫面) */
  function fitBox(): THREE.Box3 {
    return shell.group.visible ? cloudBox.clone().union(shellBox) : cloudBox.clone();
  }
  /** 主畫面沒被面板蓋住的區域(CSS px)。
   *  手機直式:上方面板堆疊橫跨整個寬度,取景要從它的底緣算到播放器頂緣,不然果蠅躲在 PiP 後面
   *  (使用者實機「稍微移動就不見了」)。桌機:面板只佔左側一欄,不擋中央,從畫面頂端算起。 */
  function viewRect() {
    const H = renderer.domElement.clientHeight || innerHeight, W = renderer.domElement.clientWidth || innerWidth;
    const topEl = document.getElementById('top')!.getBoundingClientRect();
    const top = topEl.width > W * 0.6 ? topEl.bottom : 0;
    // 下緣 = 所有「真的顯示中」的底部元件裡最高的那個:播放列、引導導覽列、橫跨全寬的紙。
    // 「顯示中」用 getClientRects().length 判(display:none 會是 0)——引導模式用 CSS class 藏播放列,
    // hidden 屬性仍是 false,舊寫法讀到 (0,0) 的矩形,可見區域塌成畫面頂端,果蠅被推出視窗上緣(2026-09-16 截圖)。
    const shown = (el: HTMLElement | null) => !!el && el.getClientRects().length > 0;
    let bot = H;
    for (const id of ['player', 'trackNav']) { const el = document.getElementById(id); if (shown(el)) bot = Math.min(bot, el!.getBoundingClientRect().top); }
    const sheet = document.getElementById('sheet');
    if (shown(sheet) && sheet!.getBoundingClientRect().width > W * 0.6) bot = Math.min(bot, sheet!.getBoundingClientRect().top);
    // 水平:桌機的紙是右欄,把右欄扣掉(手機的紙橫跨全寬,已在上面算成下緣)
    let left = 0, right = W;
    if (shown(sheet) && sheet!.getBoundingClientRect().width <= W * 0.6) right = Math.min(right, sheet!.getBoundingClientRect().left);
    const wFrac = Math.max(0.3, (right - left) / W), cx = (left + right) / 2;
    if (bot - top < H * 0.3) return { cy: (top + bot) / 2, hFrac: 0.3, cx, wFrac };   // 面板疊太多:保底,寧可與文字重疊
    return { cy: (top + bot) / 2, hFrac: (bot - top) / H, cx, wFrac };
  }
  type Pose = { dist: number; target: THREE.Vector3 };
  const UP = new THREE.Vector3(0, 1, 0);
  /** 某個包圍盒的取景姿態(相機距離 + 注視點;注視點含「落在可見區域中央」的位移),方向固定 DIR。
   *  精確擬合:把包圍盒八個角點投影到相機基底上算所需距離——相機不正對座標軸時,
   *  螢幕水平方向是 X 與 Z 的混合,只估 Z 會算得太近(實測桌面版因此溢出畫面)。
   *  方向一律「身體橫躺、頭在右」跟實體小視窗一致(使用者要求;原本直式螢幕會轉成頭朝上,
   *  但那樣主畫面跟 PiP 的動作對不起來)。直式時果蠅受寬度限制會小,靠預設運鏡推近補。 */
  type VR = { cy: number; hFrac: number; cx: number; wFrac: number };
  function poseFor(box: THREE.Box3, vrOverride?: VR): Pose {
    const right = new THREE.Vector3().crossVectors(UP, DIR).normalize();
    const up = new THREE.Vector3().crossVectors(DIR, right).normalize();
    const t = Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2);
    const ctr = box.getCenter(new THREE.Vector3()), h = box.getSize(new THREE.Vector3()).multiplyScalar(0.5);
    const vr = vrOverride ?? viewRect();
    let dist = 0;
    for (let i = 0; i < 8; i++) {
      const p = new THREE.Vector3(
        (i & 1 ? 1 : -1) * h.x, (i & 2 ? 1 : -1) * h.y, (i & 4 ? 1 : -1) * h.z);
      const depth = p.dot(DIR);
      const needV = depth + Math.abs(p.dot(up)) / (t * vr.hFrac);
      const needH = depth + Math.abs(p.dot(right)) / (t * camera.aspect * vr.wFrac);
      dist = Math.max(dist, needV, needH);
    }
    dist *= 1.12;                                   // 留一點邊
    // 讓目標中心落在可見區域的中央,不是整個視窗的中央:相機看向中心上方/下方一點,目標就在畫面上移/下移
    const H = renderer.domElement.clientHeight || innerHeight;
    const shiftDown = (vr.cy - H / 2) / (H / 2) * dist * t;           // 正值 = 目標要往下
    const W2 = renderer.domElement.clientWidth || innerWidth;
    const shiftRight = (vr.cx - W2 / 2) / (W2 / 2) * dist * t * camera.aspect;   // 正值 = 目標要往右(桌機右欄開著時往左讓)
    return { dist, target: ctr.clone().addScaledVector(up, shiftDown).addScaledVector(right, -shiftRight) };
  }
  function applyPose(p: Pose) {
    controls.target.copy(p.target);
    camera.position.copy(DIR).multiplyScalar(p.dist).add(p.target);
    controls.minDistance = p.dist * 0.08;
    controls.maxDistance = p.dist * 3.5;
    // 裁切面跟著取景距離走:原本 far 寫死 8000,取景改成只用可見區域後距離變 8,400+,
    // 果蠅一半在 far 之外——無頭截圖只剩腹部、神經元全消失。far 要蓋到 maxDistance 加物體本身。
    camera.near = p.dist * 0.01; camera.far = p.dist * 5; camera.updateProjectionMatrix();
    controls.update();
  }
  /** 預設視角:整隻果蠅置中。也是「歸位」鈕與 resize 的落點;會取消進行中的運鏡。 */
  function fitCamera() {
    camera.up.copy(UP); controls.object.up.copy(UP);
    cine = null; userMoved = false;
    applyPose(poseFor(fitBox()));
  }
  // 預設運鏡(使用者要求):按下播放時先置中看整隻,再用 6 秒慢慢推近到神經系統,讓人看到它在動。
  // 只是預設走位——使用者一拖曳/滾輪/捏合畫面,或按 歸位/＋/－,就停下來交還控制。
  // 推近沿「目前視線」做,所以自轉中、或使用者已經轉過的角度都保留。
  // 使用者動過視角(拖曳/滾輪/＋－)或運鏡已落地後,視窗 resize 不再重置視角——
  // iOS Safari 網址列收合就會發 resize,原本每次都把使用者轉好的角度打回預設(無頭截圖時也被它打回)。
  let userMoved = false;
  let cine: { t0: number; from: Pose; to: Pose; dur: number } | null = null;
  function startCinematic() {
    fitCamera();
    if (!shell.group.visible) return;               // 沒外殼時整隻就是神經系統,沒得推
    const to = poseFor(cloudBox); to.dist *= 1.3;          // 落點留三成距離:神經系統填滿畫面時透視太強、外殼環圈變得比資料還搶眼(無頭截圖)
    cine = { t0: performance.now(), from: poseFor(fitBox()), to, dur: 6000 };
  }
  function tickCinematic(now: number) {
    if (!cine) return;
    const u = Math.min(1, (now - cine.t0) / cine.dur);
    const e = u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;     // ease in-out cubic
    const dir = camera.position.clone().sub(controls.target).normalize();
    const dist = THREE.MathUtils.lerp(cine.from.dist, cine.to.dist, e);
    controls.target.copy(cine.from.target).lerp(cine.to.target, e);
    camera.position.copy(controls.target).addScaledVector(dir, dist);
    if (u >= 1) { cine = null; userMoved = true; }          // 運鏡落點視同使用者自己調過的視角,resize 不再重置
  }
  for (const ev of ['pointerdown', 'wheel']) renderer.domElement.addEventListener(ev, () => { cine = null; userMoved = true; }, { passive: true });
  /** 面板出現後的重新取景:運鏡進行中就不動(否則載入時排的 rAF 會把剛開始的運鏡取消) */
  const refit = () => { if (!cine && !userMoved) fitCamera(); };
  fitCamera();
  addEventListener('resize', refit);
  // 歸位鈕:轉歪了、拉遠了,一鍵回到預設視角並置中(使用者實機要求)
  document.getElementById('mHome')!.addEventListener('click', fitCamera);
  // 自轉與 ＋/－:觸控在宿主頁面(iframe)裡不一定可靠,給一組不靠手勢也能看各角度、拉近拉遠的按鈕
  const spinBtn = document.getElementById('mSpin')!;
  controls.autoRotateSpeed = 1.2;                       // 每圈 50 秒,慢到看得清楚
  spinBtn.addEventListener('click', () => { controls.autoRotate = !controls.autoRotate; spinBtn.setAttribute('aria-pressed', String(controls.autoRotate)); });
  let hudRefresh: (() => void) | null = null;
  let labRef: { setLang(l: 'zh' | 'en'): void } | null = null;   // applyLang 早於 lab 建立,用可空參照接   // 載入後 HUD 的字串由這個閉包重畫(語言切換時再叫一次)
  const cards = createCards();
  // ---- 介面雙語:靜態文字用 data-en(原中文存進 data-zh),動態字串走 T 表;語言切換時整頁重套 ----
  const T = {
    // 大字的分母是 MaleCNS 連接組的神經元總數 166,691;分子是有三維座標、畫得出來的 140,024(docs/data_facts.md)
    zh: { neurons: ' / 166,691 顆神經元', sub: (ms: number) => `MaleCNS v1.0 · 有三維座標的 / 連接組全部 · 載入 ${ms} ms`, sampled: (n: string, k: number) => ` · 手機模式:從 ${n} 顆等間隔抽樣 1/${k}`,
          inj: '注入', end: '結局', ours: '我們加的結局', lit: (n: string) => `畫出 ${n} 顆神經細胞(示意)`, dim: (k: string) => `亮度 ×${k}(我們調的,不是模擬)`,
          fSampled: (a: string, k: number, b: string) => `本幀畫出 ${a} 顆(手機抽樣 1/${k},實際放電約 ${b} 顆)`, fLive: (a: string) => `本幀 ${a} 顆神經元在放電`,
          next: '下一步 ', toFree: '去自由探索 ', replay: '重播', play: '播放', fail: '載入失敗' },
    en: { neurons: ' / 166,691 neurons', sub: (ms: number) => `MaleCNS v1.0 · with 3D coordinates / whole connectome · loaded in ${ms} ms`, sampled: (n: string, k: number) => ` · phone mode: every ${k}th of ${n}`,
          inj: 'injected', end: 'ending', ours: 'our added ending', lit: (n: string) => `${n} nerve cells drawn (illustrative)`, dim: (k: string) => `brightness ×${k} (set by us, not simulated)`,
          fSampled: (a: string, k: number, b: string) => `${a} drawn this frame (phone sampling 1/${k}; about ${b} actually firing)`, fLive: (a: string) => `${a} neurons firing this frame`,
          next: 'Next ', toFree: 'Explore freely ', replay: 'Replay', play: 'Play', fail: 'Failed to load' },
  };
  const lg = () => cards.lang, tx = () => T[lg()];
  const stZh = (st: { zh: string; en?: string }) => lg() === 'en' && st.en ? st.en : st.zh;
  const stSub = (st: { sub: string; sub_en?: string }) => lg() === 'en' && st.sub_en ? st.sub_en : st.sub;
  function applyLang() {
    applyStaticLang(lg());
    $('legend').innerHTML = GROUPS.map(g =>
      `<div><i style="background:#${g.color.toString(16).padStart(6,'0')}"></i>${g[lg()]}</div>`).join('');
    pip.setLang(lg()); gauge?.setLang(lg()); hudRefresh?.(); labRef?.setLang(lg());
  }
  { const orig = cards.setLang; cards.setLang = (l) => { orig(l); applyLang(); if (track === 'kid' || track === 'more') { const y = scrolly.scrollTop; buildScrolly(); scrolly.scrollTop = y; onScroll(); } else if (scn) showFrame(Number($p('scrub').value)); }; }
  const dolly = (f: number) => {                         // 沿視線把相機拉近/推遠,受 min/maxDistance 夾住
    const off = camera.position.clone().sub(controls.target);
    const len = THREE.MathUtils.clamp(off.length() * f, controls.minDistance, controls.maxDistance);
    camera.position.copy(controls.target).addScaledVector(off.normalize(), len); controls.update();
  };
  document.getElementById('mZoomIn')!.addEventListener('click', () => { cine = null; userMoved = true; dolly(0.75); });
  document.getElementById('mZoomOut')!.addEventListener('click', () => { cine = null; userMoved = true; dolly(1 / 0.75); });
  (cloud.points.material as THREE.ShaderMaterial).uniforms.uPixelRatio.value = renderer.getPixelRatio();
  (cloud.points.material as THREE.ShaderMaterial).uniforms.uScale.value = S.pointScale;

  hudRefresh = () => {
    // 大字固定是資料集的口徑(有座標的 140,024 / 連接組全部 166,691),不放抽樣後的數——
    // 手機抽樣 1/2 時原本大字直接變成 70,012,而解釋那行在手機是關掉的(VA 2026-09-16 冷審)
    $('count').textContent = cloud.nAll.toLocaleString() + tx().neurons;
    const sampled = cloud.stride > 1;
    $('sub').textContent = tx().sub(Number(loadMs.toFixed(0))) + (sampled ? tx().sampled(cloud.nAll.toLocaleString(), cloud.stride) : '');
    const dn = document.getElementById('drawn')!;
    dn.textContent = sampled ? (lg() === 'en' ? `drawing ${cloud.n.toLocaleString()} of them on this device`
                                              : `這台裝置畫出其中 ${cloud.n.toLocaleString()} 顆`) : '';
    dn.hidden = !sampled;
  };
  hudRefresh();
  // 兩種著色模式。鈣成像=全部同一種淡綠(真實活體成像的樣子,預設);
  // 功能分色=按族群上色,看得出訊號傳到哪一類神經元。圖例跟著模式切換,
  // 否則會出現「圖例宣稱的顏色畫面上根本沒有」的情況。
  const mat = cloud.points.material as THREE.ShaderMaterial;
  function setMode(calcium: boolean) {
    mat.uniforms.uCalcium.value = calcium ? 1 : 0;
    document.getElementById('legend')!.hidden = calcium;
    document.getElementById('mCal')!.setAttribute('aria-pressed', String(calcium));
    document.getElementById('mGrp')!.setAttribute('aria-pressed', String(!calcium));
  }
  document.getElementById('mCal')!.addEventListener('click', () => setMode(true));
  document.getElementById('mGrp')!.addEventListener('click', () => setMode(false));
  setMode(true);


  // ---- 情境播放 ----
  // 逐段標示。第一段是**注入**的:模型的視覺前端實測傳不過去
  // (刺激視覺柱只驅動 LC4 到 1.23Hz、LPLC2 為 0),所以這一步是我們直接給的,
  // 不是算出來的。規範見 docs/visual_provenance.md。
  // 階段時間點**取自實測**,不是猜的。來源:scripts/build_scenario.py 產生的
  // runs/build/escape.csv,各族群首次/末次放電時刻(見 docs/verification_log.md)。
  // 第一段標為注入:模型視覺前端實測傳不過去(LC4 只收到 1.23Hz、LPLC2 為 0)。
  type Stage = { t: number; zh: string; sub: string; injected?: boolean; src: string; en?: string; sub_en?: string };
  // 階段標籤來自 content/stages.json(單一來源,受 jargon_lint 檢查),不在程式碼裡硬寫。
  // 直接打包 content/stages.json:先前是手動複製一份到 public/data/,結果改了原檔網站還在讀舊的
  // (結局字幕整段對不上才發現)。單一來源,沒有第二份可以過期。
  const STAGES: Stage[] = (stagesJson as { stages: Stage[] }).stages;
  // 說明卡抽屜:兩層兩語,依階段掛點出小籤;全部卡片在索引。內容打包自 content/cards.json
  document.getElementById('chips')!.hidden = false;



  let scn: Scenario | null = null, playing = false, frame = 0, speed = 0.02, lastT = 0;
  let stopAt: number | null = null;          // 引導版:播到這一幀就停
  let edgeLayer: EdgeLayer | null = null;
  // 實體小視窗:果蠅身體在現實中做什麼(形狀我們畫的,動作由真實放電驅動,幅度示意)
  const pipBox = document.getElementById('pip')!;
  const pip: Pip = createPip(cloud, pipBox, document.getElementById('pipRead')!);
  pipBox.hidden = false; requestAnimationFrame(refit);
  let gauge: Gauge | null = null;
  try { gauge = await loadGauge('data/scenarios/escape_trace.json', document.getElementById('gaugeHost')!); document.getElementById('gaugeHost')!.hidden = false; }
  catch (err) { console.warn('電壓計未載入:', err); }
  applyLang();   // pip/gauge 到齊後跑一次:圖例、PiP 讀數、電壓計標籤都照當前語言(2026-09-16 補:圖例原本只在切語言時才填,開場是空的)
  // ③注入前奏:t<0 的「眼睛看到東西」示意。模型視覺前端算不出逼近,這段是我們畫的,
  // 用洋紅渲染並在時鐘與標籤標示。逼近物體 = 從兩眼中心往外擴的環。
  // 實驗台:目前舞台上播的是哪一個條件。null = 出貨的基準情境。
  // 非基準時字幕必須換掉——基準字幕在講逃跑的時間軸(「跳躍肌與翅膀肌動了」),
  // 套到「隨機 311 顆」那種條件上就是說謊。放電計數器同理(它的累計值只對基準那一次成立)。
  let labCond: { key: string; label: string } | null = null;
  const PRELUDE = 24;                       // 前奏幀數(以 dtMs 計的虛擬毫秒)
  // 結局幀數(我們加的,不是模擬):模型跑到 600 ms 都還在放電、真果蠅這時也還在飛,
  // 使用者仍希望畫面收在靜止——那就明標「我們加的結局」(洋紅,跟前奏同一套標示),把光與翅膀慢慢關掉。
  const EPILOGUE = 60;
  let hexCols: { d: number; i: number[] }[] = [];
  try { hexCols = (await (await fetch('data/hexmap.json')).json()).cols; }
  catch (err) { console.warn('六角柱地圖未載入,前奏停用:', err); }
  function applyPrelude(k: number) {           // k: 0..PRELUDE-1
    cloud.inj.fill(0);
    if (!hexCols.length) return 0;
    // 逼近物體的影像 = 一塊**由小變大的局部區域**,只有影像蓋到的小眼會被觸動,其餘不動。
    // 邊緣最亮(視覺神經對「變化」最敏感),內部較弱;半徑只長到 0.5,不掃到眼睛邊緣。
    // 第一版畫成一圈漣漪掃過整隻眼睛——使用者指出那不是看東西的樣子,他是對的,已改。
    // ⚠️ 區塊中心目前放在各眼的六角中心:哪個方向是「視野前方」尚待文獻確認,
    //    確認前不宣稱方向(見 verification_log §前奏示意的修正)。
    const p = k / (PRELUDE - 1);
    const R = 0.08 + p * 0.42;                   // 影像半徑:0.08 → 0.50
    const rim = 0.07;                            // 邊緣厚度
    let lit = 0;
    for (const c of hexCols) {
      if (c.d > R) continue;                     // 影像外:不反應
      const edge = 1 - Math.min(1, (R - c.d) / rim);   // 越靠邊緣越亮
      const v = 0.35 + 0.65 * edge;
      if (v <= 0) continue;
      for (const oi of c.i) {
        if (oi % cloud.stride) continue;
        const j = oi / cloud.stride; if (j < cloud.inj.length) { cloud.inj[j] = v; lit++; }
      }
    }
    return lit;
  }
  try {
    edgeLayer = await loadEdges('data/escape_edges.json', cloud);
    scene.add(edgeLayer.lines);
    muscles = buildMuscles(shell.anchors, edgeLayer); muscles.group.visible = shell.group.visible; muscleScene.add(muscles.group);
  } catch (err) { console.warn('連線層未載入(不影響點雲與播放):', err); }
  const $p = (id: string) => document.getElementById(id) as HTMLInputElement;

  // 即時放電計數器的資料:每幀累計真實放電數(scripts/export_spike_counts.py,● 我們量的)
  let spikes: number[] | null = null;
  try { spikes = (await (await fetch('data/scenarios/escape_spikes.json')).json()).cumulative; } catch (err) { console.warn('放電計數未載入:', err); }
  try {
    scn = await loadScenario('data/scenarios/escape.bin');
  } catch (err) {
    console.warn('情境未載入(頁面仍可瀏覽點雲):', err);
  }
  if (scn && scn.nPoints !== cloud.nAll) {
    // 這是硬閘門:索引空間對不上會讓錯的神經元亮起來,而那種錯用眼睛看不出來。
    // 不可降級成 warn 繼續播。
    $('count').textContent = '資料不一致,停止播放';
    $('sub').textContent = `情境檔點數 ${scn.nPoints} ≠ 點雲 ${cloud.nAll}`;
    throw new Error(`情境檔點數 ${scn.nPoints} 與點雲 ${cloud.nAll} 不符`);
  }
  if (scn) {
    $p('scrub').max = String(scn.nFrames - 1 + EPILOGUE);
    $p('scrub').min = String(-PRELUDE);
    // 情境模式:靜止點大幅調暗。4,851 個活躍點散在 140,024 個點裡,
    // 背景維持原亮度會把它們完全蓋掉(實測截圖三幀看起來一模一樣才發現)。
    (cloud.points.material as THREE.ShaderMaterial).uniforms.uRest.value = 0.24;   // 0.09 太暗:使用者實機說沒刺激時看不清楚點
    document.getElementById('player')!.hidden = false;
    document.getElementById('stage')!.hidden = false;
    requestAnimationFrame(refit);                 // 面板出現後可見區域變了,重新取景
  }

  function showFrame(f: number) {
    if (!scn) return;
    frame = Math.max(-PRELUDE, Math.min(scn.nFrames - 1 + EPILOGUE, f));
    if (frame < 0) {
      // 前奏:真實放電全清零,只畫洋紅示意
      cloud.brightness.fill(0); cloud.attrBrightness.needsUpdate = true;
      if (edgeLayer) { edgeLayer.nodeBright.fill(0); edgeLayer.update(); muscles?.update(edgeLayer.nodeBright); }
      pip.setFrame(edgeLayer, frame * scn.dtMs);
      gauge?.draw(0);
      const lit = applyPrelude(frame + PRELUDE);
      cloud.attrInj.needsUpdate = true;
      $p('scrub').value = String(frame);
      document.getElementById('clock')!.innerHTML = `<span class="inj">${(frame * scn.dtMs).toFixed(1)} ms · ${tx().inj}</span>`;
      // 文案來自 stages.json(t<0 的那段),不硬寫——硬寫會逃過 jargon_lint(審查 P2 抓過)
      const pre = STAGES.find(x => x.t < 0) ?? STAGES[0];
      document.getElementById('stage')!.innerHTML =
        `<span class="itag">${tx().inj}</span><b class="inj">${stZh(pre)}</b><span class="inj">${stSub(pre)}</span>` +
        `<span class="cnt">${tx().lit(lit.toLocaleString())}</span>` +
        `<span class="src">${srcText(pre.src, lg())}</span>`;
      cards.chipsFor(-24); cards.setSpikes(0, 0, 'prelude');
      return;
    }
    if (frame > scn.nFrames - 1) {
      // 結局(我們加的):最後一幀的真實放電乘上一個遞減係數。資料本身沒被改——escape.bin 不動,
      // 改的是顯示;PiP 的驅動跟著這個係數衰減,翅膀就自己收回靜止姿勢。標示全走洋紅。
      const k = (frame - (scn.nFrames - 1)) / EPILOGUE, decay = Math.pow(1 - k, 2);
      cloud.inj.fill(0); cloud.attrInj.needsUpdate = true;
      gauge?.draw((scn.nFrames - 1) * scn.dtMs);
      applyFrame(scn, scn.nFrames - 1, cloud.brightness, cloud.stride, edgeLayer?.watch, edgeLayer?.nodeBright);
      for (let i = 0; i < cloud.brightness.length; i++) cloud.brightness[i] *= decay;
      cloud.attrBrightness.needsUpdate = true;
      if (edgeLayer) { for (let i = 0; i < edgeLayer.nodeBright.length; i++) edgeLayer.nodeBright[i] *= decay; edgeLayer.update(); muscles?.update(edgeLayer.nodeBright); }
      pip.setFrame(edgeLayer, frame * scn.dtMs);
      $p('scrub').value = String(frame);
      document.getElementById('clock')!.innerHTML = `<span class="inj">${(frame * scn.dtMs).toFixed(1)} ms · ${tx().end}</span>`;   // 短標,完整的「我們加的結局」在字幕標題(手機時鐘欄放不下會折三行)
      const ep = STAGES.find(x => x.t >= scn!.nFrames - 1) ?? STAGES[STAGES.length - 1];
      document.getElementById('stage')!.innerHTML =
        `<span class="itag">${tx().ours}</span><b class="inj">${stZh(ep)}</b><span class="inj">${stSub(ep)}</span>` +
        `<span class="cnt inj">${tx().dim(decay.toFixed(2))}</span>` +
        `<span class="src">${srcText(ep.src, lg())}</span>`;
      cards.chipsFor(250); if (spikes) cards.setSpikes(spikes[spikes.length - 1], (scn.nFrames - 1) * scn.dtMs, 'epilogue');
      return;
    }
    // 前奏的洋紅在 t>=0 後幾幀內淡出,不硬切:注入層的顯示選擇,不碰真資料。
    // 硬切會讓 0ms 那一幀突然全暗(偵測器才剛開始累積亮度),看起來像跳幀。
    if (frame < 6) { const k = Math.pow(0.55, frame + 1); for (let i = 0; i < cloud.inj.length; i++) cloud.inj[i] *= k; }
    else cloud.inj.fill(0);
    cloud.attrInj.needsUpdate = true;
    gauge?.draw(frame * scn.dtMs);
    const nActive = applyFrame(scn, frame, cloud.brightness, cloud.stride,
                               edgeLayer?.watch, edgeLayer?.nodeBright);
    cloud.attrBrightness.needsUpdate = true;
    edgeLayer?.update();
    if (edgeLayer) muscles?.update(edgeLayer.nodeBright);
    pip.setFrame(edgeLayer, frame * scn.dtMs);
    $p('scrub').value = String(frame);
    const ms = frame * scn.dtMs;   // 不假設 dtMs==1
    document.getElementById('clock')!.textContent = ms.toFixed(1) + ' ms';
    if (labCond) {   // 實驗台的非基準條件:只說這是哪個條件、現在第幾毫秒,不套用基準的劇情字幕
      document.getElementById('stage')!.innerHTML =
        `<b>${labCond.label}</b>` +
        `<span>${lg() === 'en' ? 'Lab condition. Same protocol as the replay, only the stimulated set changed. The captions of the standard replay do not apply here.'
                               : '實驗台的條件。協定與重播完全相同,只換了刺激哪些神經元;標準重播的字幕不適用於這一段。'}</span>` +
        `<span class="cnt">${tx().fLive(nActive.toLocaleString())}</span>` +
        `<span class="src">public/data/playground.json</span>`;
      cards.chipsFor(-999); cards.setSpikes(0, ms, 'prelude');
      document.getElementById('spk')!.hidden = true;
      return;
    }
    let st = STAGES[0];
    for (const s2 of STAGES) if (frame >= s2.t) st = s2;
    document.getElementById('stage')!.innerHTML =
      `${st.injected ? `<span class="itag">${tx().inj}</span>` : ''}<b${st.injected ? ' class="inj"' : ''}>${stZh(st)}</b>` +
      `<span${st.injected ? ' class="inj"' : ''}>${stSub(st)}</span>` +
      `<span class="cnt">${cloud.stride > 1
          ? tx().fSampled(nActive.toLocaleString(), cloud.stride, (nActive * cloud.stride).toLocaleString())
          : tx().fLive(nActive.toLocaleString())}</span>` +
      `<span class="src">${srcText(st.src, lg())}</span>`;
    cards.chipsFor(st.t);
    if (spikes) cards.setSpikes(spikes[Math.min(frame, spikes.length - 1)], ms, 'live');
  }

  document.getElementById('play')!.addEventListener('click', () => {
    if (!scn) return;
    if (frame >= scn.nFrames - 1 + EPILOGUE) frame = -PRELUDE;   // 播完(含我們加的結局)才重播;停在 250 ms 再按是繼續進結局
    playing = !playing; lastT = performance.now();
    if (playing && frame === -PRELUDE) startCinematic();   // 從頭播放才走預設運鏡;中途暫停再播不動視角
    document.getElementById('play')!.textContent = playing ? '❚❚' : '▶';
  });
  $p('scrub').addEventListener('input', e => {
    playing = false; document.getElementById('play')!.textContent = '▶';
    showFrame(parseInt((e.target as HTMLInputElement).value, 10));
  });
  $p('speed').addEventListener('change', e => { speed = parseFloat((e.target as HTMLInputElement).value); });
  // ?frame=N 直接跳到某一刻:可分享「看這個瞬間」的連結,也讓無頭截圖驗收得到中段畫面
  const qf = parseInt(new URLSearchParams(location.search).get('frame') ?? '', 10);
  if (scn) showFrame(Number.isFinite(qf) ? qf : -PRELUDE);   // 預設從前奏開始
  // ---- 三分流(2026-09-16):首頁三扇門 → 小朋友版/專業版走同一列步驟(content/tracks.json),自由探索=原本畫面 ----
  type Step = { stage?: number; play?: [number, number]; card: string };
  const STEPS: Step[] = (tracksJson as { steps: Step[] }).steps;
  const home = document.getElementById('home')!, nav = document.getElementById('trackNav')!;
  let track: 'kid' | 'more' | 'free' | null = null, stepI = 0;
  function goStep(i: number) {
    if (!scn) return;
    stepI = Math.max(0, Math.min(STEPS.length - 1, i));
    const st = STEPS[stepI];
    playing = false; stopAt = null; cine = null;
    if (st.play) { showFrame(st.play[0]); stopAt = st.play[1]; playing = true; lastT = performance.now(); document.getElementById('play')!.textContent = '❚❚'; }
    else showFrame(st.stage ?? -PRELUDE);
    cards.open(st.card);
    requestAnimationFrame(() => { userMoved = false; fitCamera(); });   // 紙打開後版面變了,重新取景(把紙算進可見區域)
    document.getElementById('tPos')!.textContent = `${stepI + 1} / ${STEPS.length}`;
    (document.getElementById('tPrev') as HTMLButtonElement).disabled = stepI === 0;
    const next = document.getElementById('tNext') as HTMLButtonElement;
    next.innerHTML = `<span class="tx">${stepI === STEPS.length - 1 ? tx().toFree : tx().next}</span>→`;
  }
  // ---- scrollytelling:舞台釘在背後,#scrolly 疊在上面往上捲;捲動進度 → 幀 + 鏡頭 ----
  const scrolly = document.getElementById('scrolly')!, exitBtn = document.getElementById('exitTrack')!;
  type StepX = Step & { cam?: 'fit' | 'cns' | 'brain' | 'thorax'; side?: 'left' | 'right'; full?: boolean; len?: number; line?: { zh: string; en: string } };
  const TR = tracksJson as { hero: { zh: string; en: string; sub: { zh: string; en: string } }; steps: StepX[] };
  const L = cloud.size.z, z0 = -L / 2;
  const brainBox = new THREE.Box3(new THREE.Vector3(-cloud.size.x / 2, -cloud.size.y / 2, z0), new THREE.Vector3(cloud.size.x / 2, cloud.size.y / 2, z0 + L * 0.27));
  const thoraxBox = new THREE.Box3(new THREE.Vector3(-cloud.size.x / 2, -cloud.size.y / 2, z0 + L * 0.40), new THREE.Vector3(cloud.size.x / 2, cloud.size.y / 2, z0 + L * 0.75));
  const camBox = (c?: string) => c === 'cns' ? cloudBox : c === 'brain' ? brainBox : c === 'thorax' ? thoraxBox : fitBox();
  /** 文字塊在哪一側,果蠅就讓到另一側;手機文字在下方,果蠅往上讓 */
  function vrFor(st: StepX): VR {
    const W = renderer.domElement.clientWidth || innerWidth, H = renderer.domElement.clientHeight || innerHeight;
    if (W <= 560) return st.full ? { cx: W / 2, cy: H * 0.5, wFrac: 1, hFrac: 0.8 } : { cx: W / 2, cy: H * 0.32, wFrac: 1, hFrac: 0.5 };
    if (st.full) return { cx: W / 2, cy: H * 0.55, wFrac: 1, hFrac: 0.8 };
    return st.side === 'left' ? { cx: W * 0.68, cy: H / 2, wFrac: 0.56, hFrac: 0.85 } : { cx: W * 0.32, cy: H / 2, wFrac: 0.56, hFrac: 0.85 };
  }
  let secEls: HTMLElement[] = [], poses: Pose[] = [], activeSec = -1;
  function buildScrolly() {
    const lang = cards.lang;
    let h = `<section class="hero"><h1>${TR.hero[lang]}</h1><p>${TR.hero.sub[lang]}</p><div class="dn">▼</div></section>`;
    let stepNo = 0;                                            // 只數有卡的段;滿版一句不算一步
    TR.steps.forEach((st, i) => {
      const len = (st.len ?? 1.2);
      if (st.full) h += `<section class="sec full" data-i="${i}" style="min-height:${len * 100}vh"><div class="paper"><p class="line">${st.line ? st.line[lang] : ''}</p></div></section>`;
      else h += `<section class="sec ${st.side ?? 'left'}" data-i="${i}" style="min-height:${len * 100}vh"><div class="paper" data-card="${st.card}" data-num="${++stepNo}">${cards.cardHtml(st.card, stepNo)}</div></section>`;
    });
    h += `<section class="end"><button id="toFree">${lang === 'zh' ? '去自由探索 →' : 'Explore freely →'}</button></section>`;
    scrolly.innerHTML = h;
    scrolly.querySelectorAll<HTMLElement>('.paper[data-card]').forEach(el => cards.wireQuiz(el, el.dataset.card!));
    document.getElementById('toFree')!.addEventListener('click', () => enterTrack('free'));
    secEls = Array.from(scrolly.querySelectorAll<HTMLElement>('.sec'));
    poses = TR.steps.map(st => poseFor(camBox(st.cam), vrFor(st)));
    activeSec = -1; scrolly.scrollTop = 0; onScroll();
  }
  const easeIO = (u: number) => u < 0.5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2;
  function onScroll() {
    if (!scn || scrolly.hidden) return;
    const H = scrolly.clientHeight, mid = H * 0.5;
    let cur = -1, p = 0;
    for (let i = 0; i < secEls.length; i++) {
      const r = secEls[i].getBoundingClientRect();
      if (r.top <= mid && r.bottom > mid) { cur = i; p = (mid - r.top) / r.height; break; }
    }
    // 文字塊:紙用 sticky 黏在畫面上整段不動;只有進場(從下方升起)與退場(被段尾推出)時,
    // 按露出畫面外的比例淡出縮小。舊版用「離中線多遠」算,手機上紙固定在下方永遠離中線遠,整段都半透明(使用者 2026-09-16 回報)。
    secEls.forEach(el => {
      const paper = el.firstElementChild as HTMLElement, r = paper.getBoundingClientRect();
      const m = H * 0.07;                                      // 邊緣 7% 當緩衝帶:剛碰到邊就開始淡,退場的滿版大字不會跟下一張紙同時全亮
      const out = Math.min(1, (Math.max(0, m - r.top) + Math.max(0, r.bottom - (H - m))) / Math.max(1, r.height));
      paper.style.opacity = String(1 - out * 0.9); paper.style.transform = `scale(${1 - out * 0.08})`;
    });
    const heroP = Math.min(1, Math.max(0, scrolly.scrollTop / H));
    if (cur < 0) {                                   // 開場:整隻,隨捲動慢慢推近一點
      applyPose({ dist: poses[0].dist * (1.25 - 0.25 * heroP), target: poses[0].target });
      showFrame(-PRELUDE); return;
    }
    const st = TR.steps[cur];
    // 鏡頭:上一段落點 → 本段落點,用前 40% 的進度過渡
    const prev = poses[Math.max(0, cur - 1)], now = poses[cur], e = easeIO(Math.min(1, p / 0.4));
    applyPose({ dist: THREE.MathUtils.lerp(prev.dist, now.dist, e), target: prev.target.clone().lerp(now.target, e) });
    // 時間:play 段用進度當時間軸(前 15% 停在起點,後 15% 停在終點,中間掃過);stage 段固定
    if (st.play) { const q = Math.min(1, Math.max(0, (p - 0.15) / 0.7)); showFrame(Math.round(st.play[0] + q * (st.play[1] - st.play[0]))); }
    else if (cur !== activeSec) showFrame(st.stage ?? -PRELUDE);
    activeSec = cur;
  }
  scrolly.addEventListener('scroll', () => requestAnimationFrame(onScroll), { passive: true });
  function enterTrack(t: 'kid' | 'more' | 'free') {
    track = t; home.hidden = true;
    try { localStorage.setItem('fly.track', t); } catch { /* ignore */ }
    playing = false; stopAt = null; cine = null;
    if (t === 'free') {
      document.body.classList.remove('track', 'kid', 'more'); nav.hidden = true; scrolly.hidden = true; exitBtn.hidden = true;
      controls.enabled = true; cards.close(); userMoved = false; fitCamera(); return;
    }
    cards.setLevel(t); document.body.classList.add('track'); document.body.classList.remove('kid', 'more'); document.body.classList.add(t);
    nav.hidden = true; controls.enabled = false;               // 捲動模式:手勢給捲動,不給旋轉
    scrolly.hidden = false; exitBtn.hidden = false; cards.close();
    requestAnimationFrame(buildScrolly);
  }
  exitBtn.addEventListener('click', () => { scrolly.hidden = true; exitBtn.hidden = true; document.body.classList.remove('track', 'kid', 'more'); controls.enabled = true; home.hidden = false; });
  addEventListener('resize', () => { if (!scrolly.hidden) { poses = TR.steps.map(st => poseFor(camBox(st.cam), vrFor(st))); onScroll(); } });
  home.querySelectorAll<HTMLButtonElement>('[data-track]').forEach(b => b.addEventListener('click', () => enterTrack(b.dataset.track as 'kid' | 'more' | 'free')));
  document.getElementById('tPrev')!.addEventListener('click', () => goStep(stepI - 1));
  document.getElementById('tNext')!.addEventListener('click', () => { if (stepI === STEPS.length - 1) enterTrack('free'); else goStep(stepI + 1); });
  document.getElementById('tHome')!.addEventListener('click', () => { playing = false; stopAt = null; document.body.classList.remove('track'); nav.hidden = true; cards.close(); home.hidden = false; });
  { const qt = new URLSearchParams(location.search).get('track');
    if (qt === 'kid' || qt === 'more' || qt === 'free') enterTrack(qt); }
  { const qs = new URLSearchParams(location.search).get('scroll');
    if (qs && track && track !== 'free') setTimeout(() => { scrolly.scrollTop = Number(qs) * (scrolly.scrollHeight - scrolly.clientHeight); onScroll(); }, 900); }   // 測試用深連結
  { const qc = new URLSearchParams(location.search); const cid = qc.get('card'); const lv = qc.get('level'); const lg = qc.get('lang');
    if (lv === 'kid' || lv === 'more') cards.setLevel(lv); if (lg === 'zh' || lg === 'en') cards.setLang(lg);
    if (cid) cards.open(cid); 
    // ?t=<毫秒>:跳到情境的某一刻(分享「3.3 毫秒巨纖維放電」那種瞬間,也讓截圖可重現)。
    // 允許負值:負的是前奏(注入那段)。超出範圍就夾住,不報錯。
    const tq = qc.get('t');
    if (tq !== null && scn) {
      const ms = Number(tq);
      if (Number.isFinite(ms)) {
        const f = Math.round(ms / scn.dtMs);
        showFrame(Math.max(-PRELUDE, Math.min(scn.nFrames - 1 + EPILOGUE, f)));
      }
    } }   // 測試/分享用深連結
  // ---- 實驗台:換刺激條件,看真的跑過五次的結果;可播的條件會換掉舞台資料 ----
  const lab = createLab(async (key, bin, trace, label) => {
    try {
      const next = await loadScenario(bin);
      if (next.nPoints !== cloud.nAll) throw new Error(`情境檔點數 ${next.nPoints} ≠ 點雲 ${cloud.nAll}`);
      scn = next;
      labCond = key === 'both' ? null : { key, label };
      // 電壓計換成同一次執行的軌跡;基準以外的條件沒有前奏與結局(那兩段是為逃跑故事做的)
      const host = document.getElementById('gaugeHost')!;
      host.innerHTML = ''; gauge = await loadGauge(trace, host); host.hidden = false; gauge.setLang(lg());
      const lo = labCond ? 0 : -PRELUDE, hi = labCond ? scn.nFrames - 1 : scn.nFrames - 1 + EPILOGUE;
      $p('scrub').min = String(lo); $p('scrub').max = String(hi);
      document.getElementById('spk')!.hidden = !!labCond;
      playing = false; stopAt = null; cine = null;
      document.getElementById('play')!.textContent = '▶';
      showFrame(lo);
    } catch (err) {
      console.warn('實驗台情境未載入:', err);
      document.getElementById('stage')!.innerHTML = `<b class="inj">${lg() === 'en' ? 'Could not load that run' : '這個條件的資料載入失敗'}</b>`;
    }
  });
  labRef = lab; lab.setLang(lg());   // applyLang 在 lab 建立前就跑過了,這裡補套一次
  document.getElementById('mLab')!.addEventListener('click', () => { lab.isOpen() ? lab.close() : lab.open(); });
  // 深連結:?lab=1 打開實驗台;?lab=<條件> 直接選那個條件;再加 &labplay=1 就在舞台上播
  { const q = new URLSearchParams(location.search), v = q.get('lab');
    if (v === '1') lab.open(); else if (v) lab.select(v, q.get('labplay') === '1'); }

  if (scn && new URLSearchParams(location.search).get('play') === '1') setTimeout(() => document.getElementById('play')!.click(), 600);   // 測試用:自動播放(延後,等載入時的重新取景先跑完)

  let frames = 0, acc = 0, fps = 0;
  const clock = new THREE.Clock();
  renderer.setAnimationLoop(() => {
    const dt = clock.getDelta();
    acc += dt; frames++;
    if (acc >= 0.5) { fps = frames / acc; frames = 0; acc = 0;
      $('perf').textContent = `${fps.toFixed(0)} fps · ${S.preset} · ${hw.gpuArchitecture.slice(0, 34) || 'gpu 未知'}`;
    }
    if (playing && scn) {
      const now = performance.now();
      const advanced = (now - lastT) * speed / scn.dtMs;
      if (advanced >= 1) {
        lastT = now;
        const nf = frame + Math.floor(advanced);
        if (stopAt !== null && nf >= stopAt) {
          showFrame(stopAt); playing = false; stopAt = null;
          document.getElementById('play')!.textContent = '▶';
        } else if (nf >= scn.nFrames - 1 + EPILOGUE) {
          showFrame(scn.nFrames - 1 + EPILOGUE); playing = false;
          // 模擬在 250 ms 切斷(模型此時仍在放電,探測到 600ms 都沒停),後面 EPILOGUE 幀是我們加的結局,
          // 洋紅明標。按鈕改成「重播」。見 verification_log §模型不會自己停 / §我們加的結局。
          document.getElementById('play')!.textContent = '↺';
          document.getElementById('play')!.setAttribute('aria-label', tx().replay);
        } else showFrame(nf);
      }
    }
    tickCinematic(performance.now());
    controls.update();
    composer.render();
    // 肌肉層在 bloom 之後直接畫到畫面上:不進 composer 所以不發光(④ 規範);autoClear 關掉才不會把主畫面清掉
    renderer.autoClear = false; renderer.render(muscleScene, camera); renderer.autoClear = true;
    pip.render(renderer);   // 主畫面之後再畫 PiP 區域
  });
})().catch(e => { $('count').textContent = '載入失敗 / Failed to load'; $('sub').textContent = String(e); console.error(e); });

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight); composer.setSize(innerWidth, innerHeight);
});
