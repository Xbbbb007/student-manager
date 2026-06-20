import http from './http'
import type { ApiResponse } from '../types'

export interface UserRecord {
  id: number
  username: string
  name: string
  role: string
  password_plain: string
}

/** 获取用户列表 */
export function listUsersApi() {
  return http.get<any, ApiResponse<UserRecord[]>>('/users/')
}

/** 创建用户 */
export function createUserApi(data: { username: string; password: string; name: string; role: string }) {
  return http.post<any, ApiResponse<UserRecord>>('/users/', data)
}

/** 删除用户 */
export function deleteUserApi(id: number) {
  return http.delete<any, ApiResponse<null>>(`/users/${id}`)
}

/** 更新用户 */
export function updateUserApi(id: number, data: { name?: string; password?: string }) {
  return http.put<any, ApiResponse<UserRecord>>(`/users/${id}`, data)
}
