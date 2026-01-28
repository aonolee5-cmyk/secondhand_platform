import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

// 引入 Element Plus 的图标
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
// 引入 Element Plus 样式 (虽然有自动导入，但基础样式建议全局引入)
import 'element-plus/dist/index.css'

const app = createApp(App)

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.mount('#app')