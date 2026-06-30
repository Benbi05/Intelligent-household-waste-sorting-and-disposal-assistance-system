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
      path: '/apply',
      name: 'Apply',
      component: () => import('@/views/login/ApplyView.vue'),
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
          path: 'commodities',
          name: 'CommodityList',
          component: () => import('@/views/commodity/CommodityList.vue'),
          meta: { title: '商品管理' },
        },
        {
          path: 'orders',
          name: 'OrderList',
          component: () => import('@/views/order/OrderList.vue'),
          meta: { title: '订单管理' },
        },
        {
          path: 'settings',
          name: 'ShopInfo',
          component: () => import('@/views/settings/ShopInfo.vue'),
          meta: { title: '店铺设置' },
        },
        {
          path: 'sub-accounts',
          name: 'SubAccount',
          component: () => import('@/views/settings/SubAccount.vue'),
          meta: { title: '子账号管理' },
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
  const token = localStorage.getItem('merchant_token')
  const info = JSON.parse(localStorage.getItem('merchant_info') || 'null')
  const status = info?.status || ''

  if (to.meta.requiresAuth !== false && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && token) {
    next({ name: 'Dashboard' })
  } else if (token && status === 'pending') {
    // 审核中的商家不能访问后台
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
