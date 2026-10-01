import { definePreset } from '@primevue/themes'
import Aura from '@primevue/themes/aura'
    
export const AppPreset = definePreset(Aura, {
  semantic: {
    primary: {
      50: '#eef1fb',
      100: '#dce2f7',
      200: '#bcc7ef',
      300: '#94a4e3',
      400: '#4659bd',
      500: '#2435a0',
      600: '#1d2b82',
      700: '#182367',
      800: '#131b52',
      900: '#0f1542',
      950: '#0a0e2c',
    },
  },
})
