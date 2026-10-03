<script setup lang="ts">
import { RouterView } from 'vue-router'
import Toast from 'primevue/toast'
import AppNavbar from '@/components/AppNavbar.vue'
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <AppNavbar />
    <main>
      <RouterView />
    </main>
    <Toast />
  </div>
</template>