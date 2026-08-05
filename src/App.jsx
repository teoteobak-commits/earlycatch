import { useMemo, useState } from 'react'
import keywordData from './data/keywords.json'
import businessIdea from './data/businessIdea.json'
import { useTheme } from './hooks/useTheme'
import Header from './components/layout/Header'
import KeywordCard from './components/keywords/KeywordCard'
import BusinessIdeaModal from './components/idea/BusinessIdeaModal'
import './App.css'

const PLATFORMS = [
  { id: '전체', label: '전체' },
  { id: 'youtube', label: '유튜브' },
  { id: 'instagram', label: '인스타' },
  { id: 'tiktok', label: '틱톡' },
]

const LEVELS = ['전체', '제일 확실', '좀 애매', '아직 모름', '식었음']

export default function App() {
  const [ideaOpen, setIdeaOpen] = useState(false)
  const [platform, setPlatform] = useState('전체')
  const [level, setLevel] = useState('전체')
  const { theme, toggleTheme } = useTheme()

  const filtered = useMemo(() => {
    return keywordData.keywords.filter((k) => {
      const okPlatform = platform === '전체' || k.platforms.includes(platform)
      const okLevel = level === '전체' || k.hype.level === level
      return okPlatform && okLevel
    })
  }, [platform, level])

  return (
    <div className="page">
      <div className="page-inner">
        <Header
          resultCount={filtered.length}
          onOpenIdea={() => setIdeaOpen(true)}
          theme={theme}
          onToggleTheme={toggleTheme}
          periodLabel={keywordData.basedOn.periodLabel}
        />

        <div className="kw-filters">
          <div className="kw-filter-group">
            {PLATFORMS.map((p) => (
              <button
                key={p.id}
                className={`kw-chip ${platform === p.id ? 'is-active' : ''}`}
                onClick={() => setPlatform(p.id)}
              >
                {p.label}
              </button>
            ))}
          </div>
          <div className="kw-filter-group">
            {LEVELS.map((l) => (
              <button
                key={l}
                className={`kw-chip ${level === l ? 'is-active' : ''}`}
                onClick={() => setLevel(l)}
              >
                {l}
              </button>
            ))}
          </div>
        </div>

        <p className="kw-disclaimer">{keywordData.disclaimer}</p>

        <main className="kw-list">
          {filtered.length === 0 ? (
            <p className="kw-empty">조건에 맞는 키워드가 없습니다.</p>
          ) : (
            filtered.map((item) => <KeywordCard key={item.id} item={item} />)
          )}
        </main>

        <footer className="kw-foot">
          <p>{keywordData.notes.excluded}</p>
          <p>{keywordData.notes.community}</p>
          <p className="kw-foot-meta">
            {keywordData.basedOn.periodLabel} · 국내 표본 {keywordData.basedOn.koreaSampleSize}건 ·{' '}
            {keywordData.basedOn.platforms.length}개 플랫폼
          </p>
        </footer>
      </div>

      <BusinessIdeaModal open={ideaOpen} onClose={() => setIdeaOpen(false)} idea={businessIdea} />
    </div>
  )
}
