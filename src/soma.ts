/* 讀 public/data/soma.bin 並建成點雲。
 * 檔案格式見 scripts/export_soma.py 的 docstring:
 *   [0:4] uint32 n | [4:16] float32×3 origin | [16:28] float32×3 scale
 *   [28:] n × (int16 x, int16 y, int16 z, uint8 group, uint8 pad)
 */
import * as THREE from 'three';

export const GROUPS = [
  { key: 'intrinsic',  zh: '中間神經元', en: 'Interneurons',   color: 0x46565a, size: 1.0 },
  { key: 'sensory',    zh: '感覺(輸入)', en: 'Sensory (in)',   color: 0x2eff6e, size: 3.2 },
  { key: 'motor',      zh: '運動(輸出)', en: 'Motor (out)',    color: 0xff3b24, size: 3.0 },
  { key: 'descending', zh: '下行(指令)', en: 'Descending',     color: 0xffa021, size: 2.6 },
  { key: 'ascending',  zh: '上行(回饋)', en: 'Ascending',      color: 0x2fd8ea, size: 2.2 },
  { key: 'optic',      zh: '視葉(含視覺投射)', en: 'Optic lobe + visual projection',     color: 0x2a5ea8, size: 0.95 },
];

export interface SomaCloud {
  points: THREE.Points;
  n: number;
  brightness: Float32Array;     // 之後放電播放就寫這個陣列
  attrBrightness: THREE.BufferAttribute;
  /** ③注入層:「眼睛看到東西」的示意亮度。與 brightness 分開,shader 以洋紅渲染,
   *  永遠不得與真實放電(綠)混同——規範 docs/visual_provenance.md。 */
  inj: Float32Array;
  attrInj: THREE.BufferAttribute;
  center: THREE.Vector3;
  radius: number;
  size: THREE.Vector3;   // 包圍盒尺寸(µm):神經系統是細長形,用包圍球取景會離太遠
  /** 抽樣間隔。手機模式 >1,此時情境資料的原始索引要除以它才對得上點雲。 */
  stride: number;
  /** 原始總點數(未抽樣)。情境檔的 nPoints 必須等於這個值。 */
  nAll: number;
  /** 任意**原始**索引 → 場景座標(已套與點雲完全相同的量化/翻轉/置中變換)。
   *  線層用它取節點位置:手機抽樣時約一半節點不在點雲裡,線不能依賴抽樣結果。 */
  posOfOriginal(i: number): [number, number, number];
}

/** 取得原始位元組。優先讀 .bin;取不到就退回 .json(內含 base64)。
 *  理由:Artifact 平台只服務標準 web 媒體型別,application/octet-stream 發不上去,
 *  所以同一份資料要備一個 JSON 版。一般靜態主機仍走較小的 .bin。 */
async function fetchBytes(url: string): Promise<ArrayBuffer> {
  const r = await fetch(url);
  if (r.ok) return r.arrayBuffer();
  const alt = url.replace(/\.bin$/, '.json');
  const rj = await fetch(alt);
  if (!rj.ok) throw new Error(`讀不到 ${url} 也讀不到 ${alt}`);
  const { b64 } = await rj.json() as { b64: string };
  const bin = atob(b64);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  return out.buffer;
}

export async function loadSoma(url: string, maxPoints: number): Promise<SomaCloud> {
  const buf = await fetchBytes(url);
  const dv = new DataView(buf);
  const nAll = dv.getUint32(0, true);
  const scale = dv.getFloat32(16, true);
  const body = new DataView(buf, 28);

  // 手機保護:超過上限就等間隔抽樣(不是截斷,免得整個腹神經索不見)
  const stride = nAll > maxPoints ? Math.ceil(nAll / maxPoints) : 1;
  const n = Math.ceil(nAll / stride);

  const pos = new Float32Array(n * 3);
  const col = new Float32Array(n * 3);
  const siz = new Float32Array(n);
  const bri = new Float32Array(n);
  const c = new THREE.Color();
  const box = new THREE.Box3();
  const v = new THREE.Vector3();

  for (let i = 0, j = 0; i < nAll && j < n; i += stride, j++) {
    const o = i * 8;
    // 量化單位 → 微米(推定 8 nm/voxel,見 export_soma.py 的待確認註記)
    const x = body.getInt16(o, true)     * scale * 8 / 1000;
    const y = body.getInt16(o + 2, true) * scale * 8 / 1000;
    const z = body.getInt16(o + 4, true) * scale * 8 / 1000;
    const g = body.getUint8(o + 6);
    pos[j*3] = x; pos[j*3+1] = -y; pos[j*3+2] = z;   // Y 軸翻轉:資料的 Y 往腹側增加
    const G = GROUPS[g] ?? GROUPS[0];
    c.setHex(G.color);
    col[j*3] = c.r; col[j*3+1] = c.g; col[j*3+2] = c.b;
    siz[j] = G.size;
    bri[j] = 0;
    box.expandByPoint(v.set(x, -y, z));
  }

  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position',   new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('pcolor',     new THREE.BufferAttribute(col, 3));
  geo.setAttribute('psize',      new THREE.BufferAttribute(siz, 1));
  const attrBrightness = new THREE.BufferAttribute(bri, 1);
  attrBrightness.setUsage(THREE.DynamicDrawUsage);
  geo.setAttribute('brightness', attrBrightness);
  const inj = new Float32Array(n);
  const attrInj = new THREE.BufferAttribute(inj, 1);
  attrInj.setUsage(THREE.DynamicDrawUsage);
  geo.setAttribute('inj', attrInj);

  const mat = new THREE.ShaderMaterial({
    uniforms: { uScale: { value: 1.0 }, uPixelRatio: { value: 1.0 }, uRest: { value: 0.55 }, uCalcium: { value: 1.0 } },
    transparent: true, depthWrite: false, blending: THREE.AdditiveBlending,
    vertexShader: `
      attribute vec3 pcolor; attribute float psize; attribute float brightness; attribute float inj;
      uniform float uScale; uniform float uPixelRatio;
      varying vec3 vColor; varying float vBright; varying float vInj;
      void main(){
        vColor = pcolor;
        // gamma < 1 抬高中間調:放電後的衰減尾巴留得住,才有「漸淡」而不是「瞬間消失」
        vBright = pow(clamp(brightness, 0.0, 1.0), 0.55);
        vInj = clamp(inj, 0.0, 1.0);
        vec4 mv = modelViewMatrix * vec4(position, 1.0);
        // 尺寸跟著亮度大幅變化,這是「點亮」最直接的視覺訊號
        gl_PointSize = psize * uScale * uPixelRatio * (300.0 / -mv.z) * (1.0 + vBright * 3.4 + vInj * 2.6);
        gl_Position = projectionMatrix * mv;
      }`,
    fragmentShader: `
      varying vec3 vColor; varying float vBright; varying float vInj; uniform float uRest; uniform float uCalcium;
      void main(){
        vec2 d = gl_PointCoord - vec2(0.5);
        float r = length(d) * 2.0;
        if (r > 1.0) discard;

        // 鈣成像模式(uCalcium=1):**全部**神經元用同一種淡綠,就像真實的 GCaMP 基礎螢光
        //   —— 活體成像裡所有表達指示劑的細胞都有底色,活躍的才變亮。
        //   族群色在這個模式關掉:使用者實機看過後認為那讓畫面像「黑夜裡點蠟燭」,
        //   而不像神經活動。訊號傳到哪改由位置與階段標籤說明。
        vec3 baseHue = mix(vColor, vec3(0.42, 0.86, 0.60), uCalcium);
        vec3 hot     = mix(vColor, vec3(0.72, 1.0, 0.80), uCalcium);

        vec3 dim = baseHue * uRest;
        vec3 lit = baseHue * 1.6;
        vec3 col = mix(dim, lit, smoothstep(0.0, 0.5, vBright));
        col = mix(col, hot * 2.2, smoothstep(0.68, 1.0, vBright));

        // ③注入示意:洋紅,與真實放電的綠完全分開的色相。規範:資料會發光是綠,注入的是洋紅。
        col = mix(col, vec3(0.85, 0.32, 0.62) * 2.1, vInj);
        float core = mix(2.2, 1.0, max(vBright, vInj));
        float a = pow(1.0 - r, core);
        gl_FragColor = vec4(col, a * (0.14 + vBright * 1.0 + vInj * 0.9));   // 底 0.055→0.14:基礎螢光要看得見結構
      }`,
  });

  const points = new THREE.Points(geo, mat);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const radius = size.length() / 2;
  points.position.sub(center);          // 置中,方便 OrbitControls 繞著轉
  const posOfOriginal = (i: number): [number, number, number] => {
    const o = i * 8;
    return [ body.getInt16(o, true)     * scale * 8 / 1000 - center.x,
            -body.getInt16(o + 2, true) * scale * 8 / 1000 - center.y,
             body.getInt16(o + 4, true) * scale * 8 / 1000 - center.z ];
  };
  return { points, n, brightness: bri, attrBrightness, inj, attrInj, center, radius, size, stride, nAll: nAll, posOfOriginal };
}
