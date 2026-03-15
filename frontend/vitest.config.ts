import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test/setup.ts'],
    include: ['src/test/components/**/*.{test,spec}.{ts,tsx}'],
    exclude: ['e2e/**', 'src/test/e2e/**'],
  },
  resolve: {
    alias: {
      '@': '/Users/sachin/projects/pawpoint/frontend/src',
    },
  },
})
