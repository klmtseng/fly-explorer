/* 品質分級。結構取自 cyberpunk-room/src/engine/quality.ts:37-132,
 * 欄位換成點雲專案需要的。GPU 簽章判定邏輯原樣保留(它已經在本機與手機上驗證過)。 */
export type Preset = 'ultra' | 'high' | 'medium' | 'low';

export interface Settings {
  preset: Preset;
  pixelRatio: number;
  enableBloom: boolean;
  bloomIntensity: number;
  pointScale: number;      // 點的基礎大小倍率
  maxPoints: number;       // 上限;超過就均勻抽樣(手機保護)
}

const PRESETS: Record<Preset, Omit<Settings, 'preset'>> = {
  ultra:  { pixelRatio: 1.5,  enableBloom: true, bloomIntensity: 1.0, pointScale: 1.0,  maxPoints: 200000 },
  high:   { pixelRatio: 1.0,  enableBloom: true, bloomIntensity: 1.0, pointScale: 1.0,  maxPoints: 200000 },
  medium: { pixelRatio: 1.0,  enableBloom: true, bloomIntensity: 0.8, pointScale: 1.1,  maxPoints: 200000 },
  // cyberpunk-room 實測:四級全開 bloom 都撐得住,連 low 也是。所以這裡不關,只降強度。
  low:    { pixelRatio: 0.62, enableBloom: true, bloomIntensity: 0.6, pointScale: 1.35, maxPoints: 90000 },
};

export interface HardwareInfo {
  gpuVendor: string; gpuArchitecture: string; deviceMemoryGB: number; webgpuAvailable: boolean;
}

export function probeHardware(): HardwareInfo {
  let vendor = '', arch = '';
  try {
    const c = document.createElement('canvas');
    const gl = c.getContext('webgl2') || c.getContext('webgl');
    if (gl) {
      const dbg = (gl as WebGLRenderingContext).getExtension('WEBGL_debug_renderer_info');
      if (dbg) {
        vendor = String((gl as any).getParameter((dbg as any).UNMASKED_VENDOR_WEBGL) ?? '');
        arch   = String((gl as any).getParameter((dbg as any).UNMASKED_RENDERER_WEBGL) ?? '');
      }
    }
  } catch { /* 探測失敗就走保守分級 */ }
  return {
    gpuVendor: vendor, gpuArchitecture: arch,
    deviceMemoryGB: (navigator as any).deviceMemory ?? 4,
    webgpuAvailable: 'gpu' in navigator,
  };
}

export function pickPreset(hw: HardwareInfo): Preset {
  const sig = (hw.gpuVendor + ' ' + hw.gpuArchitecture).toLowerCase();
  const isIntelIGP = /intel/.test(sig) && /(hd|uhd|iris)/.test(sig);
  const isRTX = /(rtx|ada|ampere|turing)/.test(sig);
  const isModernNV = /nvidia|geforce/.test(sig);
  const isAppleSilicon = /apple/.test(sig) && /(m1|m2|m3|m4)/.test(sig);
  const isAMDDiscrete = /(radeon|amd)/.test(sig) && /(rx|navi|rdna)/.test(sig);
  const isMobile = /adreno|mali|powervr|apple gpu/.test(sig)
    || /android|iphone|ipad/i.test(navigator.userAgent);
  if (isRTX && hw.webgpuAvailable && hw.deviceMemoryGB >= 8) return 'ultra';
  if (isModernNV || isAppleSilicon || isAMDDiscrete) return 'high';
  if (isMobile || isIntelIGP || hw.deviceMemoryGB < 4) return 'low';
  return 'medium';
}

export function settingsFor(p: Preset): Settings { return { preset: p, ...PRESETS[p] }; }
