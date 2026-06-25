import http from "./http"

// 学生端 API
export function getMyMistakes(params?: { is_mastered?: boolean; subject?: string }) {
  return http.get("/mistakes/my", { params })
}

export function addMistake(data: {
  subject: string
  question_desc: string
  my_answer?: string
  correct_answer?: string
  exam_id?: number
  test_id?: number
}) {
  return http.post("/mistakes/add", data)
}

export function toggleMistakeMastered(id: number) {
  return http.put(`/mistakes/master/${id}`)
}

export function getMistakeStats() {
  return http.get("/mistakes/stats")
}

// 教师端 API
export function getTeacherClassMistakeStats() {
  return http.get("/mistakes/teacher/class-stats")
}

// 管理员端 API
export function getAdminMistakeTrends() {
  return http.get("/mistakes/admin/trends")
}
