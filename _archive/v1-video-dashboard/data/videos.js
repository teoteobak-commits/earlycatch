import rawVideos from './videos.json'

// videos.json: vidiq_trending_videos로 수집한 실제 데이터.
// estimatedGender / estimatedAgeGroup은 콘텐츠 성격 기반 AI 추정치 —
// 유튜브/vidiq 모두 소유하지 않은 채널의 실제 시청자 인구통계는 제공하지 않는다.
export const videos = rawVideos

export const GENDERS = ['전체', '남성', '여성']
export const AGE_GROUPS = ['전체', '10대', '20대', '30대', '40대+']

// 기간이 늘어날수록 "누적 조회수"만으로는 최근 영상이 불리해지므로,
// 정렬 시에는 시간당/일평균 조회수로 정규화해서 비교한다
export const PERIOD_OPTIONS = [
  { label: '1주', days: 7 },
  { label: '2주', days: 14 },
  { label: '1개월', days: 30 },
  { label: '3개월', days: 90 },
]

export function daysSince(uploadedAt) {
  const diff = Date.now() - new Date(uploadedAt).getTime()
  return Math.max(1, Math.floor(diff / (1000 * 60 * 60 * 24)))
}

export function dailyVelocity(video) {
  return Math.round(video.views / daysSince(video.uploadedAt))
}

export function formatViews(n) {
  if (n >= 100000000) return `${(n / 100000000).toFixed(1)}억회`
  if (n >= 10000) return `${(n / 10000).toFixed(1)}만회`
  return `${n}회`
}
