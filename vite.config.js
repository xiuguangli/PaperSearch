import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const isDev = mode === 'development'

  return {
    plugins: [vue()],
    base: isDev ? '/' : '/PaperSearch/', // 开发环境使用根路径，生产环境使用仓库名
    server: {
      fs: {
        // 允许访问上层目录
        allow: ['..']
      },
      // 添加API代理配置
      proxy: {
        '/api': {
          target: 'http://localhost:3001',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '/api')
        }
      }
    },
    define: {
      // 确保 Vue Devtools 在开发环境中可用
      __VUE_PROD_DEVTOOLS__: isDev
    }
  }
})
