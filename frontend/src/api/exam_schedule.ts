import http from "./http"

// 学生端 API
export function getMyExamSchedules() {
  return http.get("/exams-schedule/my")
}

// 教师端 API
export function getTeacherExamSchedules() {
  return http.get("/exams-schedule/teacher/list")
}

export function createExamSchedule(data: {
  name: string
  class_id: number
  subject: string
  exam_date: string
  start_time: string
  end_time: string
  location: string
  status?: string
}) {
  return http.post("/exams-schedule/create", data)
}

export function updateExamSchedule(id: number, data: {
  name: string
  class_id: number
  subject: string
  exam_date: string
  start_time: string
  end_time: string
  location: string
  status?: string
}) {
  return http.put(`/exams-schedule/update/${id}`, data)
}

export function deleteExamSchedule(id: number) {
  return http.delete(`/exams-schedule/delete/${id}`)
}

// 管理员端 API
export function getAdminExamSchedules() {
  return http.get("/exams-schedule/admin/list")
}

export function batchCreateExamSchedules(data: {
  class_ids: number[]
  name: string
  subject: string
  exam_date: string
  start_time: string
  end_time: string
  location: string
}) {
  return http.post("/exams-schedule/admin/batch", data)
}

export function detectExamConflicts() {
  return http.get("/exams-schedule/admin/conflicts")
}

export function submitTest(scheduleId: number, answers: string) {
  return http.post(`/exams-schedule/submit-test/${scheduleId}`, { answers })
}

export function autoGradeTest(scheduleId: number) {
  return http.post(`/exams-schedule/auto-grade/${scheduleId}`)
}

// Re-export for teacher module convenience
export { getHomeworkSubmissions } from "./homework"
