import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App111 from './App111.vue'
import router from './router'

const app = createApp(App111)

app.use(createPinia())
app.use(router)

app.mount('#app')
