import { defineConfig } from 'vite';
// base './' :產物用相對路徑。Artifact 與靜態主機都不吃根目錄絕對路徑(/assets/…)。
export default defineConfig({
  base: './',
  build: { assetsInlineLimit: 0 },
});
