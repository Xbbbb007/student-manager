import http from './http'

export function getMyScores() {
  return http.get('/scores/my')
}

export function getClassRanking(examId: number) {
  return http.get(`/scores/ranking/${examId}`)
}

export function getScoreTrend() {
  return http.get('/scores/trend')
}
