import { TagIcon } from '../icons/Icons'

export default function KeywordRanking({ ranking, activeQuery, onSelectKeyword }) {
  return (
    <aside className="keyword-panel">
      <div className="keyword-panel-header">
        <TagIcon className="keyword-panel-icon" />
        <h2 className="keyword-panel-title">인기 키워드 랭킹</h2>
      </div>
      <p className="keyword-panel-sub">클릭하면 해당 키워드로 필터링돼요</p>

      {ranking.length === 0 ? (
        <p className="keyword-empty">표시할 키워드가 없어요.</p>
      ) : (
        <ol className="keyword-list">
          {ranking.map((item, idx) => {
            const isActive = activeQuery.trim().toLowerCase() === item.keyword.toLowerCase()
            return (
              <li key={item.keyword}>
                <button
                  className={isActive ? 'keyword-row keyword-row--active' : 'keyword-row'}
                  onClick={() => onSelectKeyword(isActive ? '' : item.keyword)}
                >
                  <span className="keyword-rank">{idx + 1}</span>
                  {item.businessType && (
                    <span
                      className="keyword-dot"
                      style={{ background: item.businessType.color }}
                      title={item.businessType.label}
                    />
                  )}
                  <span className="keyword-name">#{item.keyword}</span>
                  <span className="keyword-count">{item.count}건</span>
                </button>
              </li>
            )
          })}
        </ol>
      )}
    </aside>
  )
}
