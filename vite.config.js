import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/forensic-analysis/',
  build: {
    outDir: 'docs',
    emptyOutDir: false, // Don't empty docs folder to preserve splice_frames
    rollupOptions: {
      output: {
        // Preserve the splice_frames directory structure
        assetFileNames: (assetInfo) => {
          if (assetInfo.name && assetInfo.name.includes('splice_frames')) {
            return assetInfo.name;
          }
          return 'assets/[name]-[hash][extname]';
        }
      }
    }
  }
})
