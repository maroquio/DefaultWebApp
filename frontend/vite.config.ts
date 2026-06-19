import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

// Em desenvolvimento o Vite serve o SPA e faz proxy de /api e /static
// para o backend FastAPI (default localhost:8400), mantendo same-origin
// para que o cookie de sessão e o CSRF funcionem sem CORS.
// Porta do backend FastAPI em dev (ver WebSPA/backend/.env -> PORT). Override
// via VITE_BACKEND_URL se necessario.
const BACKEND = process.env.VITE_BACKEND_URL || 'http://127.0.0.1:8400'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5180,
    proxy: {
      // changeOrigin:false preserva o Host do navegador (localhost:5180). Assim,
      // o 307 de barra-final do FastAPI (ex: /api/admin/usuarios -> /api/admin/usuarios/)
      // gera Location na mesma origem, reentrando pelo proxy com o cookie de sessao.
      // Com changeOrigin:true o redirect apontaria para o backend (cross-origin) e o
      // cookie nao seria enviado. Em producao (SPA servido pelo FastAPI) ja e mesma origem.
      '/api': { target: BACKEND, changeOrigin: false },
      '/static': { target: BACKEND, changeOrigin: false },
      '/health': { target: BACKEND, changeOrigin: false },
    },
  },
  preview: {
    port: 5180,
  },
  build: {
    // O backend serve este diretório em produção via SPA_DIST_PATH (../frontend/dist).
    outDir: 'dist',
    emptyOutDir: true,
  },
})
