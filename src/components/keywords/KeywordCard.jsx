import { useState } from 'react'

const PLATFORM_LABEL = {
  youtube: '유튜브',
  instagram: '인스타',
  tiktok: '틱톡',
}

const LEVEL_CLASS = {
  '제일 확실': 'lv-strong',
  '좀 애매': 'lv-mid',
  '아직 모름': 'lv-unknown',
  '식었음': 'lv-cold',
}

function formatMetric(hype) {
  if (hype.metric === '시간당 조회수') {
    return `${(hype.value / 10000).toFixed(0)}만`
  }
  return `${hype.value.toLocaleString()}배`
}

export default function KeywordCard({ item }) {
  const [open, setOpen] = useState(false)
  const { hype, korea, audience, revenue } = item

  return (
    <article className={`kw-card ${open ? 'is-open' : ''}`}>
      <header className="kw-head">
        <div className="kw-head-main">
          <div className="kw-badges">
            {item.platforms.map((p) => (
              <span key={p} className={`kw-plat kw-plat--${p}`}>
                {PLATFORM_LABEL[p] || p}
              </span>
            ))}
            <span className={`kw-level ${LEVEL_CLASS[hype.level] || ''}`}>{hype.level}</span>
          </div>
          <h3 className="kw-title">{item.keyword}</h3>
          <p className="kw-summary">{item.summary}</p>
        </div>

        <div className="kw-metric">
          <div className="kw-metric-value">{formatMetric(hype)}</div>
          <div className="kw-metric-label">{hype.metric}</div>
          <div className="kw-metric-track">
            {hype.weeksTracked}주 추적 · {hype.trend}
          </div>
        </div>
      </header>

      <div className="kw-korea">
        <span className="kw-korea-tag">국내 {korea.status}</span>
        <span className="kw-korea-detail">{korea.detail}</span>
      </div>

      <button className="kw-toggle" onClick={() => setOpen((v) => !v)}>
        {open ? '접기' : `수익모델 ${revenue.length}개 · 오디언스 보기`}
      </button>

      {open && (
        <div className="kw-body">
          <section className="kw-section">
            <h4 className="kw-section-title">
              오디언스 <span className="kw-est">추정</span>
            </h4>
            <dl className="kw-aud">
              <div><dt>연령</dt><dd>{audience.age}</dd></div>
              <div><dt>성별</dt><dd>{audience.gender}</dd></div>
              <div><dt>보는 맥락</dt><dd>{audience.context}</dd></div>
            </dl>
          </section>

          {korea.webCheck && korea.webCheck !== '미확인' && (
            <section className="kw-section">
              <h4 className="kw-section-title">국내 유입 확인</h4>
              <p className="kw-web">{korea.webCheck}</p>
            </section>
          )}

          <section className="kw-section">
            <h4 className="kw-section-title">수익모델 후보</h4>
            {revenue.length === 0 ? (
              <p className="kw-web">추천하지 않습니다. 비교용으로만 남겨둔 항목입니다.</p>
            ) : (
              <ul className="kw-rev">
                {revenue.map((r) => (
                  <li key={r.model}>
                    <p className="kw-rev-model">{r.model}</p>
                    <p className="kw-rev-why">{r.why}</p>
                    <p className="kw-rev-barrier">진입장벽 — {r.barrier}</p>
                  </li>
                ))}
              </ul>
            )}
          </section>
        </div>
      )}
    </article>
  )
}
