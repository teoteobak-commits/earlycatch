import { CheckIcon, LayersIcon } from '../icons/Icons'

export default function RecipeSection({ recipe }) {
  return (
    <section className="idea-section idea-recipe">
      <h3 className="idea-section-title">
        <LayersIcon className="idea-section-icon" />바이브코딩 A-Z 레시피
      </h3>

      <p className="idea-recipe-label">베이스</p>
      <p className="idea-recipe-text">{recipe.base}</p>

      <p className="idea-recipe-label">디자인 시스템</p>
      <ul className="idea-recipe-kv">
        <li>
          <b>색</b>
          {recipe.designSystem.colors}
        </li>
        <li>
          <b>버튼</b>
          {recipe.designSystem.buttonShape}
        </li>
        <li>
          <b>폰트</b>
          {recipe.designSystem.font}
        </li>
        <li>
          <b>아이콘</b>
          {recipe.designSystem.icon}
        </li>
      </ul>

      <p className="idea-recipe-label">핵심 기능</p>
      <ul className="idea-list">
        {recipe.coreFeatures.map((f) => (
          <li key={f}>
            <CheckIcon className="idea-list-icon" />
            <span>{f}</span>
          </li>
        ))}
      </ul>

      <p className="idea-recipe-label">MVP 범위</p>
      <p className="idea-recipe-text">{recipe.mvpScope}</p>

      <p className="idea-recipe-label">진행 단계</p>
      <ol className="idea-steps">
        {recipe.steps.map((s) => (
          <li key={s}>{s}</li>
        ))}
      </ol>
    </section>
  )
}
