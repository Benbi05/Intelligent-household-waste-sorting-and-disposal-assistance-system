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
      path: '/ops-login',
      name: 'OpsLogin',
      component: () => import('@/views/login/OpsLoginView.vue'),
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
          meta: { title: '用户管理', requiresAdmin: true },
        },
        {
          path: 'users/:userId',
          name: 'UserDetail',
          component: () => import('@/views/user/UserDetail.vue'),
          meta: { title: '用户详情', requiresAdmin: true },
        },
        {
          path: 'devices',
          name: 'DeviceList',
          component: () => import('@/views/device/DeviceList.vue'),
          meta: { title: '设备管理', requiresAdmin: true },
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
          path: 'delivery-compare',
          name: 'DeliveryCompare',
          component: () => import('@/views/statistics/DeliveryCompare.vue'),
          meta: { title: '投放对比' },
        },
        {
          path: 'rate-compare',
          name: 'RateCompare',
          component: () => import('@/views/statistics/RateCompare.vue'),
          meta: { title: '分类正确率' },
        },
        {
          path: 'device-maintenance',
          name: 'DeviceMaintenance',
          component: () => import('@/views/statistics/DeviceMaintenance.vue'),
          meta: { title: '设备维修' },
        },
        {
          path: 'user-stats',
          name: 'UserStats',
          component: () => import('@/views/statistics/UserStats.vue'),
          meta: { title: '用户统计' },
        },
        {
          path: 'merchants',
          name: 'MerchantAudit',
          component: () => import('@/views/merchant/MerchantAudit.vue'),
          meta: { title: '商家审核', requiresAdmin: true },
        },
        {
          path: 'logs',
          name: 'OperationLog',
          component: () => import('@/views/system/OperationLog.vue'),
          meta: { title: '操作日志', requiresAdmin: true },
        },
        {
          path: 'system/areas',
          name: 'AreaManage',
          component: () => import('@/views/system/AreaManage.vue'),
          meta: { title: '区域管理', requiresAdmin: true },
        },
        {
          path: 'system/roles',
          name: 'RoleManage',
          component: () => import('@/views/system/RoleManage.vue'),
          meta: { title: '角色管理', requiresAdmin: true },
        },
        {
          path: 'ops-dashboard',
          name: 'OpsDashboard',
          component: () => import('@/views/ops/OpsDashboard.vue'),
          meta: { title: '系统监控' },
        },
        {
          path: 'ops-models',
          name: 'OpsModels',
          component: () => import('@/views/ops/ModelManage.vue'),
          meta: { title: 'AI模型管理' },
        },
        {
          path: 'ops-insights',
          name: 'OpsInsights',
          component: () => import('@/views/ops/InsightView.vue'),
          meta: { title: '消费洞察' },
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
  const info = JSON.parse(localStorage.getItem('admin_info') || 'null')
  const role = info?.role || ''

  if (to.meta.requiresAuth !== false && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && token) {
    if (role === 'ops_admin') next({ name: 'OpsDashboard' })
    else next({ name: 'Dashboard' })
  } else if (to.meta.requiresAdmin && role !== 'super_admin') {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

export default router
