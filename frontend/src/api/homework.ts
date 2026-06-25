import http from "./http"

// 学生端 API
export function getMyHomework() {
  return http.get("/homework/my")
}

export function submitHomework(homeworkId: number, content: string) {
  return http.post(`/homework/submit/${homeworkId}`, { content })
}

// 教师端 API
export function createHomework(data: {
  title: string
  description?: string
  subject: string
  class_id: number
  due_date: string
}) {
  return http.post("/homework/create", data)
}

export function getTeacherHomeworks() {
  return http.get("/homework/teacher/list")
}

export function getHomeworkSubmissions(homeworkId: number) {
  return http.get(`/homework/${homeworkId}/submissions`)
}

export function gradeSubmission(submissionId: number, grade: number, feedback?: string) {
  return http.put(`/homework/submission/${submissionId}/grade`, { grade, feedback })
}

// 管理员 / 班主任端 API
export function getHomeworkOverview() {
  return http.get("/homework/admin/overview")
}
