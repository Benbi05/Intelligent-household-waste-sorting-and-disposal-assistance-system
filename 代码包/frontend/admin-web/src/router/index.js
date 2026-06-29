import { createRouter, createWebHashHistory } from 'vue-router'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/login/LoginView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/',
      component: () => import('@/components/layout/MainLayout.vue'),
      redirect: '/dashboard',
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/dashboard/DashboardView.vue'),
          meta: { title: '仪表盘' },
        },
        {
          path: 'users',
          name: 'UserList',
          component: () => import('@/views/user/UserList.vue'),
          meta: { title: '用户管理' },
        },
        {
          path: 'users/:userId',
          name: 'UserDetail',
          component: () => import('@/views/user/UserDetail.vue'),
          meta: { title: '用户详情' },
        },
        {
          path: 'devices',
          name: 'DeviceList',
          component: () => import('@/views/device/DeviceList.vue'),
          meta: { title: '设备管理' },
        },
        {
          path: 'rules',
          name: 'PointRule',
          component: () => import('@/views/point/PointRule.vue'),
          meta: { title: '积分规则' },
        },
        {
          path: 'rules/history',
          name: 'RuleHistory',
          component: () => import('@/views/point/RuleHistory.vue'),
          meta: { title: '规则历史' },
        },
        {
          path: 'categories',
          name: 'CategoryManage',
          component: () => import('@/views/point/CategoryManage.vue'),
          meta: { title: '品类管理' },
        },
        {
          path: 'statistics',
          name: 'Statistics',
          component: () => import('@/views/statistics/StatisticsView.vue'),
          meta: { title: '数据统计' },
        },
        {
          path: 'merchants',
          name: 'MerchantAudit',
          component: () => import('@/views/merchant/MerchantAudit.vue'),
          meta: { title: '商家审核' },
        },
        {
          path: 'logs',
          name: 'OperationLog',
          component: () => import('@/views/system/OperationLog.vue'),
          meta: { title: '操作日志' },
        },
        {
          path: 'system/areas',
          name: 'AreaManage',
          component: () => import('@/views/system/AreaManage.vue'),
          meta: { title: '区域管理' },
        },
        {
          path: 'system/roles',
          name: 'RoleManage',
          component: () => import('@/views/system/RoleManage.vue'),
          meta: { title: '角色管理' },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/login',
    },
  ],
})

// 鉴权守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('admin_token')

  if (to.meta.requiresAuth !== false && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && token) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
