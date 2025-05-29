import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // 환경별 API URL 설정
  const apiTarget = mode === 'production' 
    ? process.env.VITE_API_BASE_URL || 'https://your-backend-app.onrender.com'
    : 'http://localhost:8000'

  return {
    plugins: [react()],
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
          secure: mode === 'production'
        }
      }
    },
    define: {
      // 클라이언트에서 사용할 수 있도록 환경변수 정의
      __API_BASE_URL__: JSON.stringify(apiTarget)
    },
    build: {
      outDir: 'dist',
      assetsDir: 'assets'
    }
  }
}) 