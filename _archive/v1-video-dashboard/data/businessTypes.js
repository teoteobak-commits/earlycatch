// 키워드가 속한 영상 카테고리를 기준으로 "사업 유형"을 매핑하고,
// 유형별 추천 수익 파이프라인을 제공한다.
export const BUSINESS_TYPES = {
  INFO: {
    label: '정보·노하우형',
    color: '#2383e2',
    models: ['전자책 / 미니강의', '유료 뉴스레터', '자동화 SaaS (계산기·체크리스트)'],
  },
  MEME: {
    label: '챌린지·밈형',
    color: '#e2237f',
    models: ['숏폼 콘텐츠 대행', '브랜드 챌린지 기획', '광고수익형 채널 운영'],
  },
  LIFESTYLE: {
    label: '제품추천·라이프스타일형',
    color: '#2ba86f',
    models: ['제휴 마케팅 (쿠팡파트너스 등)', 'PB 상품 기획', '브랜드 협찬'],
  },
  TOOL: {
    label: '툴·자동화형',
    color: '#a35ce2',
    models: ['SaaS 구독 과금', '템플릿 / 플러그인 판매', '프리미엄 기능 판매'],
  },
}

export const CATEGORY_TO_BUSINESS_TYPE = {
  테크: 'TOOL',
  재테크: 'INFO',
  과학: 'INFO',
  건강: 'LIFESTYLE',
  라이프스타일: 'LIFESTYLE',
  먹방: 'LIFESTYLE',
  엔터테인먼트: 'MEME',
  'K-POP': 'MEME',
  ASMR: 'LIFESTYLE',
  스포츠: 'LIFESTYLE',
  게임: 'MEME',
  뉴스: 'INFO',
}

export function getBusinessType(category) {
  const key = CATEGORY_TO_BUSINESS_TYPE[category]
  return key ? BUSINESS_TYPES[key] : null
}
