export interface UserInfo {
  id: number
  username: string
  name: string
  role: 'student' | 'teacher' | 'admin'
}

export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}
