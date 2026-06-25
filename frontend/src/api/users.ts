import http from './http'
import type { ApiResponse } from '../types'

export interface UserRecord {
  id: number
  username: string
  name: string
  role: string
  password_plain: string
  class_id: number | null
  gender?: string | null
  subject?: string | null
  user_type?: string
}

/** 获取所有用户（合并列表） */
export function listUsersApi() {
  return http.get<any, ApiResponse<UserRecord[]>>('/users/')
}

/** 创建教职工 */
export function createStaffApi(data: { username: string; password: string; name: string; role: string; gender?: string; subject?: string }) {
  return http.post<any, ApiResponse<UserRecord>>('/users/staff', data)
}

/** 创建学生 */
export function createStudentApi(data: { username: string; password: string; name: string; gender?: string; class_id?: number }) {
  return http.post<any, ApiResponse<UserRecord>>('/users/students', data)
}

/** 更新教职工 */
export function updateStaffApi(id: number, data: { name?: string; password?: string; gender?: string; subject?: string }) {
  return http.put<any, ApiResponse<UserRecord>>('/users/staff/' + id, data)
}

/** 更新学生 */
export function updateStudentApi(id: number, data: { name?: string; password?: string; gender?: string; class_id?: number }) {
  return http.put<any, ApiResponse<UserRecord>>('/users/students/' + id, data)
}

/** 删除教职工 */
export function deleteStaffApi(id: number) {
  return http.delete<any, ApiResponse<null>>('/users/staff/' + id)
}

/** 删除学生 */
export function deleteStudentApi(id: number) {
  return http.delete<any, ApiResponse<null>>('/users/students/' + id)
}

/** 创建用户（按 role 自动路由） */
export function createUserApi(data: { username: string; password: string; name: string; role: string; gender?: string; subject?: string; class_id?: number }) {
  if (data.role === 'student') {
    return createStudentApi({ username: data.username, password: data.password, name: data.name, gender: data.gender, class_id: data.class_id })
  }
  return createStaffApi({ username: data.username, password: data.password, name: data.name, role: data.role, gender: data.gender, subject: data.subject })
}

/** 删除用户（legacy，带 user_type） */
export function deleteUserApi(id: number, body?: { user_type?: string }) {
  return http.delete<any, ApiResponse<null>>('/users/legacy/' + id, { data: body || {} })
}

/** 更新用户（legacy，带 user_type） */
export function updateUserApi(id: number, data: { name?: string; password?: string; user_type?: string }) {
  return http.put<any, ApiResponse<UserRecord>>('/users/legacy/' + id, data)
}

/** 获取个人资料 */
export function getUserProfileApi() {
  return http.get<any, ApiResponse<any>>('/users/profile')
}

/** 班主任获取班级学生 */
export function getHomeroomStudentsApi() {
  return http.get<any, ApiResponse<{ class_id: number; class_name: string; students: any[] }>>('/users/homeroom/students')
}

/** 班主任更新学生信息 */
export function updateHomeroomStudentApi(studentId: number, data: { name?: string; gender?: string; password?: string }) {
  return http.put<any, ApiResponse<any>>(`/users/homeroom/students/${studentId}`, data)
}

