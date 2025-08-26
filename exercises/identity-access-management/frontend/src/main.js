import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import { vueKeycloak } from '@josempgon/vue-keycloak'


const app = createApp(App)

app.use(vueKeycloak, {
  config: {
    url: 'http://localhost:8080',
    realm: 'master',
    clientId: 'secret-frontend',
  },
  initOptions: {
    onLoad: 'login-required'
  }
})

app.mount('#app')
