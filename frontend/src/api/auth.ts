import http from './http'
import type { ApiResponse, UserInfo } from '../types'

export interface LoginParams {
  username: string
  password: string
}

export interface TokenData {
  access_token: string
  token_type: string
}

/** 登录 */
export function loginApi(params: LoginParams) {
  return http.post<any, ApiResponse<{ access_token: string; token_type: string }>>('/auth/login', params)
}

/** 获取当前用户信息 */
export function getMeApi() {
  return http.get<any, ApiResponse<UserInfo>>('/auth/me')
}
