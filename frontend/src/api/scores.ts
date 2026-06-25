import http from "./http"

// 学生端 API
export function getMyScores() {
  return http.get("/scores/my")
}

export function getClassRanking(examId: number) {
  return http.get(`/scores/ranking/${examId}`)
}

export function getScoreTrend() {
  return http.get("/scores/trend")
}

// 课表 API
export function getScheduleMy() {
  return http.get("/schedule/my")
}

export function getScheduleClass(classId: number) {
  return http.get(`/schedule/class/${classId}`)
}

export function getScheduleTeacher(teacherId: number) {
  return http.get(`/schedule/teacher/${teacherId}`)
}

export function batchUpdateSchedule(classId: number, items: Array<{ day_of_week: number; period: number; subject: string; teacher_id?: number }>) {
  return http.put("/schedule/batch", { class_id: classId, items })
}

// 教师端 API
export function getExams(classId?: number) {
  const params = classId ? { class_id: classId } : {}
  return http.get("/exams/", { params })
}

export function createExam(data: { name: string; class_id: number; exam_date?: string }) {
  return http.post("/exams/", data)
}

export function getClassScores(examId: number, subject: string) {
  return http.get("/scores/class-scores", { params: { exam_id: examId, subject } })
}

export function batchSaveScores(items: Array<{ student_id: number; exam_id: number; subject: string; score: number }>) {
  return http.put("/scores/batch", { items })
}

export function getClassStats(examId: number) {
  return http.get(`/scores/class-stats/${examId}`)
}

export function getSubjectTrend(classId: number, subjects?: string) {
  const params: Record<string, any> = { class_id: classId }
  if (subjects) params.subjects = subjects
  return http.get("/scores/subject-trend", { params })
}

// 教师端新 API
export function getTeacherClasses() {
  return http.get("/scores/teacher/classes")
}

export function getTeacherExams(classIds: string) {
  return http.get("/scores/teacher/exams", { params: { class_ids: classIds } })
}

export function getTeacherDashboard(examIds: string, subject: string) {
  return http.get("/scores/teacher-dashboard", { params: { exam_ids: examIds, subject } })
}
