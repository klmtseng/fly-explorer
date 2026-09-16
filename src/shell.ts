/* 半透明果蠅外殼(④我們畫的)。
 *
 * 規範(docs/visual_provenance.md):線稿為主、絕不發光、普通混合——跟資料層(發光的點與線)
 * 刻意相反的視覺語言。實體小視窗可加**平塗淡色**(tint),仍是普通混合、不進 bloom,不會被誤認成資料。
 *
 * 比例分兩種來源,各自標示:
 *  ● 實測(docs/verification_log.md):沿身體前後軸,腦佔 CNS 全長前 27%、空脖子 13%、腹神經索 59%;
 *    腦寬 ≈ 730µm。頭與胸以此對位到真實神經系統。
 *  ◆ 文獻(docs/verification_log.md §果蠅身體比例):體長 ≈ 2.5 mm、翅膀靜止時平貼背上、身體黃褐、
 *    複眼磚紅、腹部橫向黑環(Wikipedia "Drosophila melanogaster");翅長 2.83 mm、平均翅弦 0.85 mm、
 *    腳長 1.24 mm、起飛拍翅 169 Hz、拍幅 134°(arXiv:1504.04484,引 Chen & Sun)。
 *  ○ 腹部長度與翅長/體長比是上述區間內的取值(兩來源不是同一批果蠅),為示意。
 *
 * 座標系與點雲相同:X 左右、Y 背腹(向上=背)、Z 前後(向後為正),原點在 CNS 包圍盒中心。
 */
import * as THREE from 'three';
import type { SomaCloud } from './soma';

export const SHELL_COLOR = 0x9AA8C4;

/** 文獻比例(出處見檔頭)。wingOverBody 是區間取值(○),其餘直接來自文獻(◆)。 */
export const FLY = {
  wingOverBody: 0.90,     // ○ 翅長/體長:2.83/2.5 ≈ 1.13 與翼展 4 mm 推得的 ≈0.6 之間取 0.9
  chordOverWing: 0.30,    // ◆ 0.85 / 2.83
  legOverBody: 0.50,      // ◆ 1.24 / 2.5
  flapHz: 169,            // ◆ 起飛時的拍翅頻率
  strokeDeg: 134,         // ◆ 拍幅(前後總角度)
};

/** 顏色(◆ Wikipedia 文字描述 → 我們挑的具體色值,平塗不發光) */
const TINT = { body: 0xC8A45C, eye: 0xB03A22, ring: 0x2A1E14, wing: 0xE4ECF4 };

/** 給肌肉層對位用的錨點(身體座標系,與點雲相同) */
export interface ShellAnchors {
  thorax: { c: THREE.Vector3; r: THREE.Vector3 };   // 胸腔橢球中心與三軸半徑
  legBase: THREE.Vector3[];                          // 六隻腳的髖關節位置,順序 L1 R1 L2 R2 L3 R3
}

export interface Shell {
  group: THREE.Group;
  anchors: ShellAnchors;
  /** 可動部位,PiP 會驅動 */
  wingL: THREE.Object3D; wingR: THREE.Object3D;
  legs: THREE.Object3D[];            // 6 隻,順序 L1 R1 L2 R2 L3 R3
  proboscis: THREE.Object3D;
  body: THREE.Object3D;              // 頭+胸+腹整體(跳躍時抬升)
}

export interface ShellOpts {
  /** 線稿不透明度。主畫面 0.11(外殼只要「感覺得到有身體」,不壓過資料);PiP 0.55 */
  opacity?: number;
  /** 平塗淡色(僅實體小視窗用;主畫面保持純線稿讓神經元透出來) */
  tint?: boolean;
}

export function buildShell(cloud: SomaCloud, opts: ShellOpts = {}): Shell {
  const lineOpacity = opts.opacity ?? 0.11;
  const mat = () => new THREE.LineBasicMaterial({
    color: SHELL_COLOR, transparent: true, opacity: lineOpacity, depthWrite: false,
    blending: THREE.NormalBlending,    // 不加色:線稿不發光
  });
  const tintMat = (color: number, opacity: number, vertexColors = false) => new THREE.MeshBasicMaterial({
    color: vertexColors ? 0xffffff : color, transparent: true, opacity, depthWrite: false,
    blending: THREE.NormalBlending, side: THREE.DoubleSide, vertexColors,
  });

  /** 橢球的經緯環(不用 EdgesGeometry:三角網格太密,像網不像手繪) */
  function ellipsoidRings(rx: number, ry: number, rz: number, nLat = 2, nLong = 3, seg = 48): THREE.LineSegments {
    const pts: number[] = [];
    const push = (a: THREE.Vector3, b: THREE.Vector3) => pts.push(a.x, a.y, a.z, b.x, b.y, b.z);
    for (let i = 1; i <= nLat; i++) {                       // 緯圈(繞 Z)
      const phi = Math.PI * i / (nLat + 1), r = Math.sin(phi), z = Math.cos(phi) * rz;
      for (let s = 0; s < seg; s++) {
        const t0 = s / seg * Math.PI * 2, t1 = (s + 1) / seg * Math.PI * 2;
        push(new THREE.Vector3(Math.cos(t0) * rx * r, Math.sin(t0) * ry * r, z),
             new THREE.Vector3(Math.cos(t1) * rx * r, Math.sin(t1) * ry * r, z));
      }
    }
    for (let j = 0; j < nLong; j++) {                       // 經線(過 Z 軸)
      const th = Math.PI * j / nLong;
      for (let s = 0; s < seg; s++) {
        const p0 = s / seg * Math.PI * 2, p1 = (s + 1) / seg * Math.PI * 2;
        push(new THREE.Vector3(Math.cos(th) * Math.sin(p0) * rx, Math.sin(th) * Math.sin(p0) * ry, Math.cos(p0) * rz),
             new THREE.Vector3(Math.cos(th) * Math.sin(p1) * rx, Math.sin(th) * Math.sin(p1) * ry, Math.cos(p1) * rz));
      }
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute(pts, 3));
    return new THREE.LineSegments(g, mat());
  }
  /** 橢球平塗(tint 模式才加)。bands 給的話依 z 位置上色(腹部黑環)。 */
  function ellipsoidFill(rx: number, ry: number, rz: number, color: number, opacity: number,
                         bands?: (zz: number) => boolean): THREE.Mesh {
    const g = new THREE.SphereGeometry(1, 28, 18);
    g.scale(rx, ry, rz);
    if (bands) {
      const pos = g.getAttribute('position'), col = new Float32Array(pos.count * 3);
      const base = new THREE.Color(color), dark = new THREE.Color(TINT.ring);
      for (let i = 0; i < pos.count; i++) {
        const c = bands(pos.getZ(i) / rz) ? dark : base;
        col[i * 3] = c.r; col[i * 3 + 1] = c.g; col[i * 3 + 2] = c.b;
      }
      g.setAttribute('color', new THREE.BufferAttribute(col, 3));
    }
    const m = new THREE.Mesh(g, tintMat(color, opacity, !!bands));
    m.renderOrder = -1;                                    // 先畫平塗,線稿疊在上面
    return m;
  }
  function polyline(points: THREE.Vector3[]): THREE.Line {
    const g = new THREE.BufferGeometry().setFromPoints(points);
    return new THREE.Line(g, mat());
  }

  const L = cloud.size.z;                 // CNS 全長(µm)
  const z0 = -L / 2;                      // CNS 最前端(腦前緣)
  const brainZ = z0 + L * 0.135;          // 腦中心(前 27% 的中點)
  const vncZ0  = z0 + L * 0.40;           // 腹神經索起點
  const W = cloud.size.x;                 // 腦寬 ≈ 730µm

  const group = new THREE.Group();
  const body = new THREE.Group(); group.add(body);

  // 頭:包住腦與視葉;複眼在頭的兩側(視葉正外側)
  const headRz = L * 0.20;
  const head = ellipsoidRings(W * 0.58, W * 0.46, headRz);
  head.position.set(0, 0, brainZ); body.add(head);
  if (opts.tint) { const f = ellipsoidFill(W * 0.58, W * 0.46, headRz, TINT.body, 0.26); f.position.copy(head.position); body.add(f); }
  for (const sx of [-1, 1]) {
    const eye = ellipsoidRings(W * 0.16, W * 0.30, L * 0.15, 2, 3, 32);
    eye.position.set(sx * W * 0.52, 0, brainZ); body.add(eye);
    if (opts.tint) { const f = ellipsoidFill(W * 0.16, W * 0.30, L * 0.15, TINT.eye, 0.55); f.position.copy(eye.position); body.add(f); }
  }
  // 觸角(頭前方兩根)
  for (const sx of [-1, 1]) body.add(polyline([
    new THREE.Vector3(sx * W * 0.10, W * 0.05, brainZ - L * 0.18),
    new THREE.Vector3(sx * W * 0.22, W * 0.12, brainZ - L * 0.34)]));
  // 口器(頭前下方,可動)
  const proboscis = new THREE.Group();
  proboscis.add(polyline([new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, -W * 0.18, -L * 0.06), new THREE.Vector3(0, -W * 0.30, -L * 0.04)]));
  proboscis.position.set(0, -W * 0.30, brainZ - L * 0.10); body.add(proboscis);
  // 脖子:兩條線把頭胸接起來(那 132µm 只有軸突)
  for (const sx of [-1, 1]) body.add(polyline([
    new THREE.Vector3(sx * W * 0.16, 0, brainZ + L * 0.17), new THREE.Vector3(sx * W * 0.20, 0, vncZ0 - L * 0.02)]));
  // 胸:包住腹神經索的胸段
  const thoraxZ = vncZ0 + L * 0.30, thoraxRz = L * 0.36;
  const thorax = ellipsoidRings(W * 0.55, W * 0.52, thoraxRz, 3, 4);
  thorax.position.set(0, W * 0.04, thoraxZ); body.add(thorax);
  if (opts.tint) { const f = ellipsoidFill(W * 0.55, W * 0.52, thoraxRz, TINT.body, 0.26); f.position.copy(thorax.position); body.add(f); }
  // 腹:CNS 資料到此為止。長度取文獻體長比例(腹約佔體長一半,○ 示意);雄性:末端整段深色,前面三道橫環(◆)
  const abdRz = L * 0.52, abdZ = thoraxZ + thoraxRz + L * 0.42;
  const abdomen = ellipsoidRings(W * 0.50, W * 0.44, abdRz, 3, 3);
  abdomen.position.set(0, -W * 0.02, abdZ); body.add(abdomen);
  if (opts.tint) {
    const f = ellipsoidFill(W * 0.50, W * 0.44, abdRz, TINT.body, 0.30,
      zz => zz > 0.62 || [-0.45, -0.1, 0.25].some(c => Math.abs(zz - c) < 0.05));
    f.position.copy(abdomen.position); body.add(f);
  }
  // 體長(頭前緣到腹末端)——翅膀與腳的尺寸都以它為基準(◆ 文獻比例)
  const headFront = brainZ - headRz, tail = abdZ + abdRz, B = tail - headFront;

  // 六隻腳:從胸下方,三對對應 T1/T2/T3;每隻三節,可動(繞髖關節)。總長 ≈ 0.5 體長(◆)
  const legs: THREE.Object3D[] = [];
  const legZ = [thoraxZ - thoraxRz * 0.55, thoraxZ, thoraxZ + thoraxRz * 0.55];
  const legLen = B * FLY.legOverBody;
  for (let i = 0; i < 3; i++) for (const sx of [-1, 1]) {
    const leg = new THREE.Group();
    const dz = (i - 1) * legLen * 0.25;
    // 三節:腿節向外、脛節向下、跗節貼地;三段長度 0.40/0.45/0.15 體長比例
    leg.add(polyline([
      new THREE.Vector3(0, 0, 0),
      new THREE.Vector3(sx * legLen * 0.36, -legLen * 0.16, dz * 0.6),
      new THREE.Vector3(sx * legLen * 0.50, -legLen * 0.58, dz * 1.2),
      new THREE.Vector3(sx * legLen * 0.54, -legLen * 0.72, dz * 1.4)]));
    leg.position.set(sx * W * 0.25, -W * 0.30, legZ[i]);
    body.add(leg); legs.push(leg);
  }
  // 翅膀:翅根在胸背側。幾何以「指向側面(+X / −X)」建,前緣在 −Z 側;
  // 靜止時繞 Y 軸轉到指向後方平貼背上(◆),拍動時繞同一軸前後掃(拍幅 134°,◆)。
  const S = B * FLY.wingOverBody, C = S * FLY.chordOverWing / 0.79;   // 平均弦 0.30 ⇒ 最大弦 ≈ 0.38
  const outline: [number, number][] = [[0, 0], [0.30, -0.04], [0.70, -0.03], [1.00, 0.12], [0.92, 0.28],
                                       [0.70, 0.38], [0.40, 0.36], [0.12, 0.22], [0, 0.06]];
  const veins: [number, number][] = [[1.00, 0.12], [0.95, 0.24], [0.80, 0.34], [0.50, 0.37]];
  const mkWing = (sx: number) => {
    const wg = new THREE.Group();
    const P = (u: number, v: number) => new THREE.Vector3(sx * u * S, 0, v * C);
    wg.add(polyline([...outline.map(([u, v]) => P(u, v)), P(0, 0)]));
    for (const [u, v] of veins) wg.add(polyline([P(0, 0), P(u, v)]));           // 縱脈(示意 4 條)
    if (opts.tint) {
      const sh = new THREE.Shape(outline.map(([u, v]) => new THREE.Vector2(sx * u * S, v * C)));
      const g = new THREE.ShapeGeometry(sh); g.rotateX(Math.PI / 2);            // XY 平面 → XZ 平面
      const m = new THREE.Mesh(g, tintMat(TINT.wing, 0.12)); m.renderOrder = -1; wg.add(m);
    }
    wg.position.set(sx * W * 0.30, W * 0.50, thoraxZ - thoraxRz * 0.15);
    return wg;
  };
  const wingL = mkWing(-1), wingR = mkWing(1); body.add(wingL, wingR);
  const anchors: ShellAnchors = {
    thorax: { c: thorax.position.clone(), r: new THREE.Vector3(W * 0.55, W * 0.52, thoraxRz) },
    legBase: legs.map(l => l.position.clone()),
  };
  const shell = { group, wingL, wingR, legs, proboscis, body, anchors };
  animateShell(shell, { wing: 0, jump: 0, proboscis: 0 }, 0);      // 擺成靜止姿勢(翅膀向後平貼)

  group.name = 'shell';
  return shell;
}

const REST_ANGLE = THREE.MathUtils.degToRad(82);                    // 靜止:向後平貼,略外張讓兩翅分得出
const LATERAL_ANGLE = THREE.MathUtils.degToRad(15);                 // 拍動中點:近正側向,略偏後
const HALF_STROKE = THREE.MathUtils.degToRad(FLY.strokeDeg / 2);   // 拍幅一半(◆ 134°/2),在拍翅面內量
// 拍翅面相對身體軸的傾角(○ 示意)。真實果蠅懸停時拍翅面接近水平(翅膀前後掃),起飛/前飛時傾斜;
// 第一版做成純前後掃,使用者看起來像直升機——從側面看,人認得的是上下拍。這裡把 134° 的行程
// 分解成上下(繞身體軸)為主、前後為輔:下拍偏前、上拍偏後。角度本身沒有出處,標 ○。
const STROKE_TILT = THREE.MathUtils.degToRad(55);

/** PiP 驅動:drives 為 0..1 的強度(由真實放電率正規化),幅度是示意。 */
export function animateShell(s: Shell, d: { wing: number; jump: number; proboscis: number }, tSimSec: number) {
  // 翅膀:相位用模擬時間(暫停時停住、拖曳時一致),頻率 169 Hz(◆ 起飛);
  // 本情境 DLMn/DVMn 的平均亮度峰值只有一成左右(24 顆輪流放電、每顆一次,平均被稀釋),
  // 所以 ≈12% 就當全幅——幅度本來就是示意,時機才是資料(PiP 頁尾有寫)
  const k = THREE.MathUtils.clamp((d.wing - 0.02) / 0.10, 0, 1);
  const A = HALF_STROKE * Math.sin(tSimSec * FLY.flapHz * Math.PI * 2) * k;   // 拍翅面內的瞬時角
  const elev = A * Math.sin(STROKE_TILT), sweep = A * Math.cos(STROKE_TILT);   // 上下 / 前後分量
  const yaw = (1 - k) * REST_ANGLE + k * LATERAL_ANGLE + sweep;               // 繞背腹軸:正值 = 指向後
  // Euler 預設 XYZ:先繞 Z(翅膀還指向側面時上下拍),再繞 Y(往後收/前後掃)
  s.wingR.rotation.y = -yaw; s.wingL.rotation.y = yaw;
  s.wingR.rotation.z = 0.04 + elev; s.wingL.rotation.z = -(0.04 + elev);
  // 跳躍:後腳蹬直、身體抬升前傾
  const j = d.jump;
  for (let i = 0; i < 6; i++) {
    const rear = i >= 4 ? 1 : i >= 2 ? 0.35 : 0.1;
    s.legs[i].rotation.x = -j * rear * 0.9;
  }
  s.body.position.y = j * 120; s.body.rotation.x = -j * 0.18;
  // 口器伸出
  s.proboscis.rotation.x = d.proboscis * 0.8;
}
