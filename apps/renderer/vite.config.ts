// DEF: Vite-Konfig mit Alias & Monorepo-Freigaben
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { resolve } from 'node:path'
import { calcKwp, computePVFlow } from '@kakerlake/core'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@kakerlake/core': resolve(__dirname, '../../packages/core/dist/index.js'),
    },
    // Bei PNPM/Monorepo manchmal nötig:
    preserveSymlinks: true,
  },
  server: {
    // Erlaubt Zugriff außerhalb des Renderer-Ordners (monorepo)
    fs: {
      allow: [
        __dirname,
        resolve(__dirname, '../../'), // monorepo root
      ],
    },
  },
  optimizeDeps: {
    // Falls Vite die Dist-ESM erneut scannen muss
    include: ['@kakerlake/core'],
  },
})
