import http from "./http"

// 学生端 API
export function getMyAttendanceLogs() {
  return http.get("/attendance/my/logs")
}

export function getMyAttendanceStats() {
  return http.get("/attendance/my/stats")
}

export function getMyLeaves() {
  return http.get("/attendance/my/leaves")
}

export function createMyLeaveRequest(data: {
  start_date: string
  end_date: string
  reason: string
}) {
  return http.post("/attendance/my/leaves", data)
}

// 教师端 API
export function getTeacherClassLogs() {
  return http.get("/attendance/teacher/class-logs")
}

export function takeRollCall(data: {
  class_id: number
  date: string
  period: number
  records: { student_id: number; status: string; reason?: string }[]
}) {
  return http.post("/attendance/teacher/roll-call", data)
}

export function getTeacherLeaves() {
  return http.get("/attendance/teacher/leaves")
}

export function approveLeaveRequest(id: number, data: { status: string; feedback?: string }) {
  return http.put(`/attendance/teacher/leaves/${id}`, data)
}

// 管理员端 API
export function getAdminAttendanceStats() {
  return http.get("/attendance/admin/stats")
}
