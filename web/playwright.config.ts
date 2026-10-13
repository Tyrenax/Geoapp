import { defineConfig } from '@playwright/test'

// Recettes sur le build (chemins relatifs, comme servi par `python -m http.server -d dist 8405`).
export default defineConfig({
  testDir: 'tests/e2e',
  timeout: 120_000,
  workers: 2,
  reporter: [['list']],
  use: {
    baseURL: 'http://localhost:4405/',
    viewport: { width: 1600, height: 900 },
    locale: 'fr-FR',
  },
  webServer: {
    command: 'npm run build && npx vite preview --port 4405 --strictPort',
    url: 'http://localhost:4405/',
    reuseExistingServer: false,
    timeout: 180_000,
  },
})
