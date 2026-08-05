import { GENDERS, AGE_GROUPS, PERIOD_OPTIONS } from '../../data/videos'

export default function FilterBar({
  gender,
  onGenderChange,
  ageGroup,
  onAgeGroupChange,
  periodDays,
  onPeriodDaysChange,
  sortBy,
  onSortByChange,
  SORT_OPTIONS,
}) {
  return (
    <div className="filter-bar">
      <div className="period-toggle">
        {PERIOD_OPTIONS.map((p) => (
          <button
            key={p.days}
            className={periodDays === p.days ? 'period-btn period-btn--active' : 'period-btn'}
            onClick={() => onPeriodDaysChange(p.days)}
          >
            {p.label}
          </button>
        ))}
      </div>

      <select
        className="filter-select"
        value={gender}
        onChange={(e) => onGenderChange(e.target.value)}
      >
        {GENDERS.map((g) => (
          <option key={g} value={g}>
            {g === '전체' ? '성별 전체' : g}
          </option>
        ))}
      </select>

      <select
        className="filter-select"
        value={ageGroup}
        onChange={(e) => onAgeGroupChange(e.target.value)}
      >
        {AGE_GROUPS.map((a) => (
          <option key={a} value={a}>
            {a === '전체' ? '연령 전체' : a}
          </option>
        ))}
      </select>

      <div className="sort-toggle">
        <button
          className={sortBy === SORT_OPTIONS.VPH ? 'sort-btn sort-btn--active' : 'sort-btn'}
          onClick={() => onSortByChange(SORT_OPTIONS.VPH)}
        >
          시간당 조회순
        </button>
        <button
          className={sortBy === SORT_OPTIONS.VIEWS ? 'sort-btn sort-btn--active' : 'sort-btn'}
          onClick={() => onSortByChange(SORT_OPTIONS.VIEWS)}
        >
          누적 조회순
        </button>
      </div>
    </div>
  )
}
