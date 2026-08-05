import { useMemo, useState } from 'react'
import { getBusinessType } from '../data/businessTypes'
import { daysSince, dailyVelocity, PERIOD_OPTIONS } from '../data/videos'

const SORT_OPTIONS = {
  VPH: 'vph',
  VELOCITY: 'velocity',
  VIEWS: 'views',
}

export function useVideoFilter(videos) {
  const [query, setQuery] = useState('')
  const [gender, setGender] = useState('전체')
  const [ageGroup, setAgeGroup] = useState('전체')
  const [periodDays, setPeriodDays] = useState(PERIOD_OPTIONS[0].days)
  const [sortBy, setSortBy] = useState(SORT_OPTIONS.VPH)

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()

    let result = videos.filter((v) => {
      const matchesQuery =
        q === '' ||
        v.title.toLowerCase().includes(q) ||
        v.keywords.some((k) => k.toLowerCase().includes(q))
      const matchesGender = gender === '전체' || v.estimatedGender === gender
      const matchesAge = ageGroup === '전체' || v.estimatedAgeGroup === ageGroup
      const matchesPeriod = daysSince(v.uploadedAt) <= periodDays
      return matchesQuery && matchesGender && matchesAge && matchesPeriod
    })

    result = [...result].sort((a, b) => {
      if (sortBy === SORT_OPTIONS.VIEWS) return b.views - a.views
      if (sortBy === SORT_OPTIONS.VELOCITY) return dailyVelocity(b) - dailyVelocity(a)
      return b.vph - a.vph
    })

    return result
  }, [videos, query, gender, ageGroup, periodDays, sortBy])

  const keywordRanking = useMemo(() => {
    // 키워드별 등장 횟수 + 어떤 카테고리에서 가장 많이 나왔는지(사업 유형 판단용) 집계
    const counts = new Map()
    const categoryTally = new Map()

    filtered.forEach((v) => {
      v.keywords.forEach((k) => {
        counts.set(k, (counts.get(k) || 0) + 1)
        const tally = categoryTally.get(k) ?? new Map()
        tally.set(v.category, (tally.get(v.category) || 0) + 1)
        categoryTally.set(k, tally)
      })
    })

    return [...counts.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 10)
      .map(([keyword, count]) => {
        const tally = categoryTally.get(keyword)
        const topCategory = [...tally.entries()].sort((a, b) => b[1] - a[1])[0][0]
        return { keyword, count, businessType: getBusinessType(topCategory) }
      })
  }, [filtered])

  return {
    query,
    setQuery,
    gender,
    setGender,
    ageGroup,
    setAgeGroup,
    periodDays,
    setPeriodDays,
    sortBy,
    setSortBy,
    SORT_OPTIONS,
    filtered,
    keywordRanking,
  }
}
