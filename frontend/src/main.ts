import '@fontsource/plus-jakarta-sans/400.css'
import '@fontsource/plus-jakarta-sans/500.css'
import '@fontsource/plus-jakarta-sans/600.css'
import '@fontsource/plus-jakarta-sans/700.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import PrimeVue from 'primevue/config'
import { AppPreset } from './theme.ts'
import 'primeicons/primeicons.css'
import './assets/main.css'
import ToastService from 'primevue/toastservice'
import ConfirmationService from 'primevue/confirmationservice'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ToastService)
app.use(ConfirmationService)

app.use(PrimeVue, {
  theme: {
    preset: AppPreset,
    options: {
      darkModeSelector: '.my-app-dark',
      cssLayer: {
        name: 'primevue',
        order: 'theme, base, primevue',
      },
    },
  },
})

app.mount('#app')
