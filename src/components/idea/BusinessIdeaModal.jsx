import { useEffect, useState } from 'react'
import { CloseIcon, AlertIcon, LayersIcon, TrendingUpIcon } from '../icons/Icons'
import RecipeSection from './RecipeSection'
import keywordData from '../../data/keywords.json'

export default function BusinessIdeaModal({ open, onClose, idea }) {
  const [recipeOpen, setRecipeOpen] = useState(false)

  useEffect(() => {
    if (!open) return
    const onKeyDown = (e) => e.key === 'Escape' && onClose()
    document.addEventListener('keydown', onKeyDown)
    return () => document.removeEventListener('keydown', onKeyDown)
  }, [open, onClose])

  if (!open) return null

  const top = idea.ideas[0]
  const alternatives = idea.ideas.slice(1)

  return (
    <div className="idea-modal-backdrop" onClick={onClose}>
      <div className="idea-modal" onClick={(e) => e.stopPropagation()}>
        <button className="idea-modal-close" onClick={onClose} aria-label="닫기">
          <CloseIcon />
        </button>

        <div className="idea-modal-scroll">
          <p className="idea-modal-meta">
            {idea.basedOn.periodLabel} · {idea.basedOn.source}
          </p>
          <h2 className="idea-modal-title">이번 주 사업 아이템 리포트</h2>

          <section className="narrative-block">
            <span className="narrative-label">기</span>
            <p className="narrative-text">{idea.narrative.intro}</p>
          </section>

          <section className="narrative-block">
            <span className="narrative-label">승</span>
            <p className="narrative-text">{idea.narrative.development}</p>
            <ul className="gap-mini-list">
              {keywordData.keywords.map((k) => {
                const isYoutube = k.platforms.includes('youtube')
                const platformLabel = k.platforms.includes('youtube') ? 'YouTube' : '인스타/틱톡'
                const evidenceText =
                  k.hype.metric === '시간당 조회수'
                    ? `최고 시간당 ${(k.hype.value / 10000).toFixed(1)}만회`
                    : `평소 대비 ${k.hype.value.toLocaleString()}배`
                return (
                  <li key={k.id}>
                    <div className="gap-mini-head">
                      <b>{k.keyword}</b>
                      <span className={`gap-platform-badge gap-platform-badge--${isYoutube ? 'youtube' : 'ig'}`}>
                        {platformLabel}
                      </span>
                    </div>
                    <span>
                      {evidenceText} · {k.hype.weeksTracked}주 추적 · 국내 {k.korea.status}
                    </span>
                  </li>
                )
              })}
            </ul>
          </section>

          <section className="narrative-block">
            <span className="narrative-label">전</span>
            <p className="narrative-text">{idea.narrative.turn}</p>

            <div className="top-idea-card">
              <p className="top-idea-title">{top.title}</p>
              <p className="top-idea-oneliner">{top.oneLiner}</p>

              <div className="revenue-grid">
                {top.revenueStreams.map((r) => (
                  <div key={r.name} className="revenue-card">
                    <p className="revenue-name">{r.name}</p>
                    <p className="revenue-model">{r.model}</p>
                    <p className="revenue-desc">{r.description}</p>
                  </div>
                ))}
              </div>

              <ul className="idea-list idea-list--risk">
                {top.risks.map((r) => (
                  <li key={r}>
                    <AlertIcon className="idea-list-icon" />
                    <span>{r}</span>
                  </li>
                ))}
              </ul>

              <button className="tier-recipe-toggle" onClick={() => setRecipeOpen((v) => !v)}>
                <LayersIcon className="tier-recipe-toggle-icon" />
                {recipeOpen ? 'A-Z 레시피 접기' : 'A-Z 레시피 보기'}
              </button>

              {recipeOpen && <RecipeSection recipe={top.vibeCodingRecipe} />}
            </div>
          </section>

          <section className="narrative-block">
            <span className="narrative-label">결</span>
            <p className="narrative-text">{idea.narrative.conclusion}</p>
            <ul className="alt-idea-list">
              {alternatives.map((a) => (
                <li key={a.rank}>
                  <TrendingUpIcon className="idea-list-icon" />
                  <span>
                    <b>{a.rank}순위 · {a.title}</b> — {a.oneLiner}
                  </span>
                </li>
              ))}
            </ul>
          </section>
        </div>
      </div>
    </div>
  )
}
