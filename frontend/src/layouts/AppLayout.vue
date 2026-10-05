<script setup lang="ts">
import { RouterView } from 'vue-router'
import Toast from 'primevue/toast'
import ConfirmDialog from 'primevue/confirmdialog'
import AppNavbar from '@/components/AppNavbar.vue'
</script>

<template>
  <div class="min-h-screen bg-slate-50">
    <AppNavbar />
    <main>
      <RouterView v-slot="{ Component, route }">
        <component :is="Component" :key="route.path" />
      </RouterView>
    </main>
    <Toast /> 
    <ConfirmDialog />
  </div>
</template>