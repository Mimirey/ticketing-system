import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { Permission } from '@/constant/permissions'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    guestOnly?: boolean
    permission?: Permission
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
          meta: { permission: 'ticket:create' },
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
          meta: { permission: 'activity-log:view' },
        },
        {
          path: 'profile',
          name: 'profile',
          component: () => import('@/views/ProfileView.vue'),
        },
        {
          path: 'tickets/:id(\\d+)',
          name: 'ticket-detail',
          component: () => import('@/views/TicketDetailView.vue'),
          props: (route) => ({ id: Number(route.params.id) }),
        },
        {
          path: 'companies',
          name: 'companies',
          component: () => import('@/views/CompanyView.vue'),
          meta: { permission: 'master:manage' },
        },
        {
          path: 'applications',
          name: 'applications',
          component: () => import('@/views/ApplicationView.vue'),
          meta: { permission: 'master:manage' },
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

  if (to.meta.permission && !auth.can(to.meta.permission)) {
    return { name: 'tickets' }
  }
})

export default router
