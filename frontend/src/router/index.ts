import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

export const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: '登录' }
  },
  {
    path: '/student',
    name: 'Student',
    component: () => import('../views/student/Layout.vue'),
    meta: { title: '学生端', role: 'student' },
    children: [
      {
        path: '',
        redirect: '/student/learn'
      },
      {
        path: 'learn',
        name: 'StudentLearn',
        component: () => import('../views/student/Learn.vue'),
        meta: { title: '学习' }
      },
      {
        path: 'life',
        name: 'StudentLife',
        component: () => import('../views/student/Life.vue'),
        meta: { title: '生活' }
      },
      {
        path: 'profile',
        name: 'StudentProfile',
        component: () => import('../views/student/Profile.vue'),
        meta: { title: '我的' }
      }
    ]
  },
  {
    path: '/teacher',
    name: 'Teacher',
    component: () => import('../views/teacher/Layout.vue'),
    meta: { title: '教师端', role: 'teacher' },
    children: [
      {
        path: '',
        redirect: '/teacher/teach'
      },
      {
        path: 'teach',
        name: 'TeacherTeach',
        component: () => import('../views/teacher/Teach.vue'),
        meta: { title: '教学' }
      },
      {
        path: 'manage',
        name: 'TeacherManage',
        component: () => import('../views/teacher/Manage.vue'),
        meta: { title: '管理' }
      },
      {
        path: 'profile',
        name: 'TeacherProfile',
        component: () => import('../views/teacher/Profile.vue'),
        meta: { title: '我的' }
      }
    ]
  },
  {
    path: '/admin',
    name: 'Admin',
    component: () => import('../views/admin/Layout.vue'),
    meta: { title: '管理端', role: 'admin' },
    children: [
      {
        path: '',
        redirect: '/admin/users'
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('../views/admin/Users.vue'),
        meta: { title: '用户管理' }
      },
      {
        path: 'edu',
        name: 'AdminEdu',
        component: () => import('../views/admin/Edu.vue'),
        meta: { title: '教务' }
      },
      {
        path: 'books',
        name: 'AdminBooks',
        component: () => import('../views/admin/Books.vue'),
        meta: { title: '图书' }
      },
      {
        path: 'logistics',
        name: 'AdminLogistics',
        component: () => import('../views/admin/Logistics.vue'),
        meta: { title: '后勤' }
      },
      {
        path: 'data',
        name: 'AdminData',
        component: () => import('../views/admin/Data.vue'),
        meta: { title: '数据' }
      },
      {
        path: 'settings',
        name: 'AdminSettings',
        component: () => import('../views/admin/Settings.vue'),
        meta: { title: '设置' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: { title: '404' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('token')
  if (to.path === '/login') {
    next()
    return
  }
  if (!token && to.path !== '/login') {
    next('/login')
    return
  }
  document.title = (to.meta.title as string) || '智慧学生管理系统'
  next()
})

export default router
