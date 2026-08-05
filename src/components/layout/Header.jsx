import { IdeaIcon, SunIcon, MoonIcon } from '../icons/Icons'

export default function Header({ resultCount, onOpenIdea, theme, onToggleTheme, periodLabel }) {
  return (
    <header className="header">
      <div className="header-top">
        <h1 className="header-title">TEO 리서치</h1>
        <button
          className="theme-toggle"
          onClick={onToggleTheme}
          aria-label={theme === 'dark' ? '라이트 모드로 전환' : '다크 모드로 전환'}
        >
          {theme === 'dark' ? <SunIcon /> : <MoonIcon />}
        </button>
      </div>
      <p className="header-sub">
        해외에서 뜨는데 국내엔 아직 없는 키워드를 찾아 수익모델까지 연결합니다
      </p>

      <div className="header-toolbar">
        <span className="header-meta">
          {periodLabel} · 키워드 {resultCount}개
        </span>
        <button className="btn idea-cta" onClick={onOpenIdea}>
          <IdeaIcon className="idea-cta-icon" />
          이번 주 리포트
        </button>
      </div>
    </header>
  )
}
