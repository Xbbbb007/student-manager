import { createRouter, createWebHistory } from "vue-router"
import type { RouteRecordRaw } from "vue-router"

export const routes: RouteRecordRaw[] = [
  {
    path: "/",
    redirect: "/login",
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/Login.vue"),
    meta: { title: "登录" },
  },
  {
    path: "/student",
    component: () => import("../views/student/Layout.vue"),
    meta: { title: "学生端", role: "student" },
    children: [
      { path: "", redirect: "/student/learn" },
      { path: "learn", component: () => import("../views/student/Learn.vue"), meta: { title: "学习" } },
      { path: "schedule", component: () => import("../views/student/Schedule.vue"), meta: { title: "课表" } },
      { path: "life", component: () => import("../views/student/Life.vue"), meta: { title: "生活" } },
      { path: "profile", component: () => import("../views/student/Profile.vue"), meta: { title: "我的" } },
    ],
  },
  {
    path: "/teacher",
    component: () => import("../views/teacher/Layout.vue"),
    meta: { title: "教师端", role: "teacher" },
    children: [
      { path: "", redirect: "/teacher/scores" },
      { path: "teach", component: () => import("../views/teacher/Teach.vue"), meta: { title: "教学" } },
      { path: "scores", component: () => import("../views/teacher/ScoresManage.vue"), meta: { title: "成绩管理" } },
      { path: "schedule", component: () => import("../views/teacher/Schedule.vue"), meta: { title: "课表管理" } },
      { path: "manage", component: () => import("../views/teacher/Manage.vue"), meta: { title: "管理" } },
      { path: "profile", component: () => import("../views/teacher/Profile.vue"), meta: { title: "我的" } },
    ],
  },
  {
    path: "/admin",
    component: () => import("../views/admin/Layout.vue"),
    meta: { title: "管理端", role: "admin" },
    children: [
      { path: "", redirect: "/admin/users" },
      { path: "users", component: () => import("../views/admin/Users.vue"), meta: { title: "用户管理" } },
      { path: "edu", component: () => import("../views/admin/Edu.vue"), meta: { title: "教务" } },
      { path: "books", component: () => import("../views/admin/Books.vue"), meta: { title: "图书" } },
      { path: "logistics", component: () => import("../views/admin/Logistics.vue"), meta: { title: "后勤" } },
      { path: "data", component: () => import("../views/admin/Data.vue"), meta: { title: "数据" } },
      { path: "settings", component: () => import("../views/admin/Settings.vue"), meta: { title: "设置" } },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: () => import("../views/NotFound.vue"),
    meta: { title: "404" },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

function getSavedRole(): string | null {
  try {
    const info = localStorage.getItem("userInfo")
    if (info) return JSON.parse(info).role
  } catch {
    /* ignore */
  }
  return null
}

const roleHome: Record<string, string> = {
  student: "/student/learn",
  teacher: "/teacher/scores",
  admin: "/admin/users",
}

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem("token")
  const role = getSavedRole()

  document.title = (to.meta.title as string) || "智慧学生管理系统"

  if (to.path === "/login") {
    if (token && role) {
      next(roleHome[role] || "/")
    } else {
      next()
    }
    return
  }

  if (!token) {
    next("/login")
    return
  }

  if (!role) {
    next("/login")
    return
  }

  const requiredRole = to.meta.role as string | undefined
  if (requiredRole && role !== requiredRole) {
    next(roleHome[role] || "/")
    return
  }

  next()
})

export default router
