/// <reference types="vitest/config" />
import { svelte } from '@sveltejs/vite-plugin-svelte'
import { cpSync, existsSync, readFileSync, statSync } from 'node:fs'
import { extname, join, normalize, resolve } from 'node:path'
import { defineConfig, type Plugin } from 'vite'

const FIXTURES = resolve(import.meta.dirname, 'fixtures')
const REAL_DATA = resolve(import.meta.dirname, 'public/data/countries.json')

const TYPES: Record<string, string> = {
  '.json': 'application/json',
  '.svg': 'image/svg+xml',
}

/**
 * Fixture de dev : servie sous /fixtures/ par le serveur de dev, et copiée dans dist/ au build
 * tant que les vraies données (public/data/countries.json) ne sont pas là.
 */
function fixtures(): Plugin {
  return {
    name: 'geo-atlas-fixtures',
    configureServer(server) {
      server.middlewares.use('/fixtures', (req, res, next) => {
        const rel = normalize(decodeURIComponent((req.url ?? '/').split('?')[0])).replace(/^([/\\])+/, '')
        const file = join(FIXTURES, rel)
        if (!file.startsWith(FIXTURES) || !existsSync(file) || !statSync(file).isFile()) {
          res.statusCode = 404
          res.end()
          return
        }
        res.setHeader('Content-Type', TYPES[extname(file)] ?? 'application/octet-stream')
        res.end(readFileSync(file))
        void next
      })
    },
    closeBundle() {
      if (!existsSync(REAL_DATA)) cpSync(FIXTURES, resolve(import.meta.dirname, 'dist/fixtures'), { recursive: true })
    },
  }
}

export default defineConfig({
  base: './',
  plugins: [svelte(), fixtures()],
  test: {
    include: ['tests/unit/**/*.test.ts'],
  },
})
