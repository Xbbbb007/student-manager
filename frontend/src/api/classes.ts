import http from './http'
import type { ApiResponse } from '../types'

export interface ClassInfo {
  id: number
  name: string
  section: string        // "小学部" | "初中部"
  grade: string
  homeroom_teacher: string
  homeroom_teacher_id: number | null
  student_count: number
}

export function listClassesApi() {
  return http.get<any, ApiResponse<ClassInfo[]>>('/classes/')
}
