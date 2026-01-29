import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
// 引入自动导入插件
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    // 自动导入 Vue 相关函数 (如 ref, reactive, onMounted)
    AutoImport({
      imports: ['vue', 'vue-router'],
      resolvers: [ElementPlusResolver()],
    }),
    // 自动导入 Element Plus 组件 (如 ElButton, ElInput)
    Components({
      resolvers: [ElementPlusResolver()],
    }),
  ],
  resolve: {
    // 配置路径别名，@ 代表 src 目录
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000, // 前端运行端口
    open: true, // 自动打开浏览器
    proxy: {
      // 配置跨域代理 (为后续对接 Django 做准备)
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      // rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})