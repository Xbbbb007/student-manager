export interface UserInfo {
  id: number
  username: string
  name: string
  role: string  // "student" | "teacher" | "admin"
  user_type?: string  // "staff" | "student"
}

export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}
