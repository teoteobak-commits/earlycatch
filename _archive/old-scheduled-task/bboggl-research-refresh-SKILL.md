---
name: bboggl-research-refresh
description: TEO 리서치 사이트 주간 트렌드 데이터 갱신 (vidiq 수집 → 병합 → 사업아이템 재분석)
---

프로젝트 경로: `C:\Users\LG\Desktop\리서치 폴더`

이 프로젝트는 "TEO 리서치" — 한국어 숏폼/롱폼 유튜브 트렌드를 분석하고, 해외(YouTube + 인스타/틱톡)에서 먼저 터진 뒤 아직 한국에 없는 소재를 찾아 사업 아이템을 제안하는 개인용 리서치 대시보드(React+Vite)다. 핵심 전제: 많은 HYPE 아이템은 해외에서 먼저 터지고 한국으로 벤치마킹되어 들어온다. 이 리포트가 다른 유튜브 트렌드 리포트와 다른 점은 YouTube뿐 아니라 인스타/틱톡까지 함께 보는 것 — 2026-08-04부터 인스타/틱톡 아웃라이어 수집이 추가됨.

**중요 — 이전 실행에서 발견된 문제, 반드시 지켜라:**
1. 매주 같은 결론이 자동으로 반복되면 안 된다. "지난주 1순위를 기본으로 유지"하는 식의 관성적 판단 금지. 매번 증거를 처음부터 다시 평가하고, 근거가 약해졌으면 순위를 내리거나 빼라.
2. 해외 데이터를 매번 완전히 동일한 방식(영어권 전체 VPH 1위)으로만 뽑으면 항상 같은 초대형 채널(MrBeast급)만 나온다. 아래 2번 단계처럼 카테고리를 매주 다르게 돌려서 새로운 신호가 나올 여지를 만들어라.
3. 기존 갭의 증거(VPH 등)가 지난주 대비 하락했으면 confidence를 낮추거나 목록에서 빼라. 상승했다고 무비판적으로 "재확인됨"이라고만 쓰지 말고, 하락한 것도 정직하게 반영해라.

## 0. 갱신 전 스냅샷
`src/data/businessIdea.json`의 `narrative`와 `ideas` 배열, `src/data/globalGaps.json`의 갭 목록(특히 각 항목의 maxVph)을 기억해둔다.

## 1. 국내 데이터 수집 (vidiq MCP)
vidiq_trending_videos 도구를 두 번 호출한다 (필요하면 ToolSearch로 "vidiq_trending_videos" 먼저 로드):
- { videoFormat: 'short', videoTitleLanguage: 'ko', sortBy: 'vph', limit: 30 }
- { videoFormat: 'long', videoTitleLanguage: 'ko', sortBy: 'vph', limit: 20 }

## 2. 해외 데이터 수집 — 매주 다르게, YouTube + 인스타/틱톡
아래 세 가지를 모두 수행한다:
a) 기본 베이스라인: { videoFormat: 'short', videoTitleLanguage: 'en', sortBy: 'vph', limit: 25 } (변화 추적용으로 매번 동일하게 유지)
b) 카테고리 로테이션: vidiq_trend_categories로 카테고리 목록을 받은 뒤, **이번 실행 날짜를 기준으로 지난 2~3주와 다른 카테고리 3개**를 골라 vidiq_outliers를 호출한다: { keyword 또는 trendCategories: [고른 카테고리들], language: 'en', contentType: 'short', publishedWithin: 'thisWeek', sort: 'breakoutScore', limit: 20 }. 이건 절대 규모(초대형 채널)가 아니라 **채널 평균 대비 튀는 정도**로 뽑기 때문에 매번 다른 채널/소재가 나온다 — 이게 staleness 문제를 푸는 핵심 장치다. 어떤 카테고리를 썼는지 로그에 남겨서 다음 실행이 참고하게 하되, 별도 파일에 기록할 필요는 없고 이메일 요약에 "이번 주 살펴본 카테고리: X, Y, Z"로 남기면 된다.
c) **인스타/틱톡 아웃라이어** (2026-08-04부터 추가): `vidiq_instagram_tiktok_outlier_search`를 호출한다. `query`는 매주 다른 각도로 바꿔서 탐색(예: "viral trending short-form format breaking out right now", "unexpected transformation reveal", "everyday life relatable moment" 등 로테이션), `audienceQuery`는 `"Culture/Region: Korea/Korean; Global: true; Demographics: short-form content creators looking for new formats to copy;"` 고정, `embeddingType: 'format'`, `resultsPerPlatform: 20`, `datePostedAfter`는 최근 30일 이내로 설정한다. **저작권 주의**: 결과 중 "footage compilation"/"클립 모음·재편집" 스타일(barrier에 "sourcing/curating viral clips" 등이 명시된 것)은 남의 영상을 재사용하는 포맷이라 갭으로 채택하지 않는다 — 직접 촬영/제작 가능한 포맷(POV 연출, 리액션, 챌린지 등)만 갭 후보로 쓴다.
이 결과들은 videos.json에 병합하지 않고 갭 분석(5번)에만 쓴다.

## 3. 국내 데이터 스키마 변환 → scripts/incoming.json
1번에서 받은 국내 영상만 아래 스키마의 JSON 배열로 변환해서 `scripts/incoming.json`에 저장(덮어쓰기):
```
{
  id: videoId, title: (해시태그 제거), channel: channelTitle,
  category: 테크|엔터테인먼트|건강|재테크|과학|먹방|K-POP|라이프스타일|스포츠|ASMR|게임|뉴스 중 하나,
  views: viewCount, vph: Math.round(vph), uploadedAt: videoPublishedAt,
  keywords: [한국어 키워드 3~4개], estimatedGender: '남성'|'여성', estimatedAgeGroup: '10대'|'20대'|'30대'|'40대+'
}
```
카테고리는 `src/data/businessTypes.js`의 CATEGORY_TO_BUSINESS_TYPE 참고. 새 카테고리 필요하면 사업유형 매핑(INFO/MEME/LIFESTYLE/TOOL)도 추가. estimatedGender/AgeGroup은 추정치이며 `src/data/videos.json` 기존 항목을 분류 스타일 기준으로 삼는다.

## 4. 병합
`node scripts/merge-videos.mjs` 실행 — id 기준으로 `src/data/videos.json`에 병합.

## 5. 해외-국내 갭 분석
2번(a+b+c)에서 받은 해외 영상·릴스·틱톡 전체에서 반복 등장하는 포맷/게임/밈/챌린지를 3~5개 추출한다 (YouTube뿐 아니라 인스타/틱톡에서 나온 포맷도 후보에 포함— 단 2c의 저작권 주의사항을 지킨 것만). 각각 병합 후 `src/data/videos.json` 전체(한국)에 유사 콘텐츠가 있는지 확인해서 없으면 갭으로 기록한다. **기존에 있던 갭은 이번 주 증거(videoCount, maxVph)와 비교해서**: VPH가 유의미하게 떨어졌으면 confidence를 낮추고 opportunity 문구에 하락 사실을 명시, 계속 하락 추세면 목록에서 제외하고 새 갭으로 교체. `src/data/globalGaps.json` 스키마:
```
{ id, topic, sourcePlatform: "youtube"|"instagram/tiktok", overseasEvidence: {videoCount, maxVph 또는 maxOutlierMultiple, exampleTitles}, koreaStatus, confidence: "높음"|"중간"|"낮음", opportunity }
```
(`sourcePlatform`은 이번 갱신부터 추가된 필드 — 기존 갭에도 소급해서 채워넣는다. YouTube는 `maxVph`, 인스타/틱톡은 배율값을 `maxOutlierMultiple`로 기록한다.)
`generatedAt`, `basedOn`, `methodology`도 갱신 — `methodology`에 이번부터 인스타/틱톡도 포함한다는 내용을 반영.

## 6. 사업 아이템 재분석 — 매번 처음부터 재평가
`src/data/businessIdea.json`을 읽고 스키마(`generatedAt`, `basedOn`, `narrative: {intro, development, turn, conclusion}`, `ideas` 배열)는 유지하되, **내용은 매번 증거를 새로 저울질해서 결정**한다:
- `narrative.intro` (기): 이번 주 국내/해외 몇 건, 어떤 카테고리를 새로 살펴봤는지.
- `narrative.development` (승): 국내 1위 니치의 경쟁 상황 + 이번 주 갭 분석 결과 — 강해진 것과 약해진 것을 모두 언급.
- `narrative.turn` (전): 이번 주 1순위가 무엇인지 — 지난주와 같을 수도 다를 수도 있다. 같다면 왜 같은 결론이 재검증됐는지 구체적 근거(예: VPH가 실제로 유지/상승)를 들어라. 다르다면 무엇이 바뀌어서 순위가 바뀌었는지 밝혀라. 국내 데이터만으로 강한 신호가 나와도 기존 서비스(알파컷/Vrew 등)와 직접 경쟁이면 1순위로 올리지 마라.
- `narrative.conclusion` (결): 총평 + 대안 + 다음 주 지켜볼 점.
- `ideas` 배열(3개, rank 1~3): title/oneLiner/targetAudience/rationale/contentNicheType/businessModelType/revenueStreams/risks/vibeCodingRecipe 구조 유지, 내용은 이번 판단에 맞게 갱신. rank 1 title은 "TEO 트렌드 스카우팅 리포트"라는 브랜드명을 유지해라 (Bboggl이라는 이름은 더 이상 쓰지 않는다).

`src/data/tierIdeas.json`은 화면에 안 쓰이니 건드리지 마라.

## 7. 변화 여부 판단
0번 스냅샷과 비교해서 핵심 결론(1순위, 갭 목록, 각 갭의 confidence)이 실질적으로 달라졌으면 "변경됨", 사실상 같으면 "동일함"이라고 판단하되 — 6번 지침대로 "동일함"은 반드시 재검증을 거친 결과여야 한다.

## 8. 이메일 초안 작성 (Gmail MCP의 create_draft — 발송 도구는 없다, 초안까지만)
받는 사람: teoteobak@gmail.com
제목: "[TEO 리서치] 주간 사업 아이템 리포트 — YYYY-MM-DD"
본문은 `narrative`를 자연스러운 문단으로 옮긴다. 바이브코딩 레시피/소스코드는 제외. "이번 주 살펴본 카테고리" 한 줄과, "전" 단락에 변화 여부(7번)를 명시적으로 언급. A4 반 페이지 내외.

## 9. 완료
draft id, 실행 요약(국내/해외 신규 건수, 이번 주 살펴본 카테고리, 인스타/틱톡에서 새로 나온 갭 유무, 갭 confidence 변화, 1순위 변경 여부)을 로그로 남긴다.

## 주의사항
- UI/컴포넌트 파일은 건드리지 않는다 — videos.json, businessIdea.json, globalGaps.json, scripts/incoming.json만 수정. tierIdeas.json은 건드리지 않는다.
- vidiq 호출은 회당 5크레딧(outliers, 인스타/틱톡 포함), 이번 작업은 총 25크레딧 정도.
- 인스타/틱톡 갭 후보 중 "클립 컴필레이션/재편집" 계열(남의 영상 재사용 포맷)은 절대 갭으로 채택하지 않는다 — 저작권 리스크 때문에 상품화 불가.
- git 저장소 아님 — git 명령 실행 금지.
- 이메일은 초안까지만, 발송은 사용자가 직접.