import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    guestOnly?: boolean
    roles?: string[]
  }
}

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/',
      component: () => import('@/layouts/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: { name: 'tickets' } },
        {
          path: 'tickets',
          name: 'tickets',
          component: () => import('@/views/TicketListView.vue'),
        },
        {
          path: 'tickets/new',
          name: 'ticket-create',
          component: () => import('@/views/TicketFormView.vue'),
        },
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/DashboardView.vue'),
        },
        {
          path: 'activity-log',
          name: 'activity-log',
          component: () => import('@/views/ActivityLogView.vue'),
          meta: { roles: ['PM_IT'] }, // SESUAIKAN
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/ProfileView.vue'),
        },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: { name: 'tickets' } },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return {
      name: 'login',
      query: to.fullPath !== '/' ? { redirect: to.fullPath } : undefined,
    }
  }

  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { name: 'tickets' }
  }

  if (to.meta.roles && !to.meta.roles.includes(auth.user?.role ?? '')) {
    return { name: 'tickets' }
  }
})

export default router
