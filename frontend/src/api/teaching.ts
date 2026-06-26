import http from "./http"

export function getQuestions(params?: { subject?: string; difficulty?: string; question_type?: string }) {
  return http.get("/teaching/questions", { params })
}

export function createQuestion(data: {
  subject: string
  question_type: string
  question_desc: string
  difficulty: string
  answer?: string
  explanation?: string
}) {
  return http.post("/teaching/questions", data)
}

export function getPapers(params?: { subject?: string }) {
  return http.get("/teaching/papers", { params })
}

export function createPaper(data: {
  title: string
  subject: string
  difficulty: string
  questions: number[]
}) {
  return http.post("/teaching/papers", data)
}

export function autoGeneratePaper(params: {
  title: string
  subject: string
  difficulty: string
  count: number
}) {
  return http.post("/teaching/papers/auto", null, { params })
}

export function getResources(params?: { subject?: string; grade?: string }) {
  return http.get("/teaching/resources", { params })
}

export function uploadResource(data: {
  title: string
  subject: string
  grade: string
  file_name: string
  file_path: string
}) {
  return http.post("/teaching/resources", data)
}
