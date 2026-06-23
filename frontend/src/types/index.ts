export interface UserInfo {
  id: number
  username: string
  name: string
  role: string
  user_type?: string
  subject?: string | null
  class_id?: number | null
}

export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}
