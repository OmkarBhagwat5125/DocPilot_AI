import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath } from 'url'
import path from 'path'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

export default defineConfig({
  plugins: [react()],
  envDir: path.resolve(__dirname, '../'), // Load env vars from project root (.env)
  server: {
    port: 3000
  },
  build: {
    outDir: 'dist',
    sourcemap: false
  }
})

