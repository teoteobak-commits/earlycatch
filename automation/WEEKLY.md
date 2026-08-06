# TEO 주간 리서치 지시서

해외(유튜브·인스타그램·틱톡)에서 뜨는데 국내엔 아직 없는 키워드를 찾아 수익모델 후보까지 붙인다. 한국어로 작업한다.

사용자는 실행 중에 없다. 질문하지 말고 판단해서 진행하되, 판단한 내용은 보고에 적는다.
실패한 단계가 있어도 멈추지 말고 나머지를 진행한 뒤 실패 사실을 보고에 분명히 적는다. **절대 실패를 성공처럼 보고하지 않는다.**

---

## 0. 준비

저장소를 최신으로 pull 한다. 오늘 날짜(KST)를 `TODAY` 로 잡는다 — 이 루틴은 UTC 일요일 밤에 도는데 한국은 월요일 아침이다.

```bash
TODAY=$(date -u -d '+9 hours' +%Y-%m-%d)
```

- `src/data/keywords.json` → `earlycatch-blog/snapshots/$TODAY-keywords.json` 으로 복사(비교 기준)
- `src/data/references.json` 을 읽는다. 외부 참조 자료와 그 한계가 적혀 있다.
- `earlycatch-blog/published/` 의 파일 개수를 세서 `n` 으로 둔다(로테이션에 씀)

한글 폰트를 설치한다. 안 하면 이미지 글꼴이 중국어 폰트로 렌더된다.

```bash
apt-get install -y fonts-noto-cjk 2>/dev/null \
  || sudo apt-get install -y fonts-noto-cjk 2>/dev/null \
  || { mkdir -p ~/.fonts && cd ~/.fonts \
       && curl -sL -o NotoSansKR.zip "https://fonts.google.com/download?family=Noto%20Sans%20KR" \
       && unzip -o -q NotoSansKR.zip && fc-cache -f; }
fc-list :lang=ko | head -3
```

둘 다 실패하면 이미지 단계를 건너뛰고 보고에 적는다.

---

### 크레딧 예산 — 이번 실행 상한 40

2026-08-06 첫 실행에서 **85 크레딧**을 썼다. 잔액이 130이라 이 속도면 두 번도 못 돈다. 그래서 상한을 건다.

시작할 때 `vidiq_balance` 로 잔액을 확인하고 기록해둔다. 그리고 **추적 패스를 먼저, 탐색 패스를 나중에** 한다. 추적 도중 40을 넘길 것 같으면 **탐색 패스를 건너뛰고** 보고에 "크레딧 상한으로 탐색 생략"이라고 적는다.

우선순위는 명확하다. **새 걸 못 찾는 건 한 주 손해지만, 추적이 끊기면 지금까지 쌓은 게 무의미해진다.**

---

## 1-A. 추적 패스 — 이걸 먼저 한다

**이게 이 루틴의 핵심이다.** 새 걸 찾는 것보다 기존 걸 계속 다시 재는 게 중요하다. 3주치가 쌓여야 뜨는 건지 식는 건지 갈린다.

keywords.json 의 각 키워드에 `trackQuery` 가 있다. **매주 이 질의를 그대로 쓴다.** 질의를 바꾸면 지난주와 비교가 안 되어 history 가 끊어진다.

| 플랫폼 | 도구 | 이번 주 값으로 쓸 것 |
| --- | --- | --- |
| youtube | `vidiq_youtube_search` 에 trackQuery | 상위 결과의 시간당 조회수 |
| instagram / tiktok | `vidiq_instagram_tiktok_outlier_search` 의 query 에 trackQuery, `datePostedAfter` 는 최근 14일 | 상위 결과의 평소 대비 배율 |

규칙 네 가지.

1. `level` 이 `식었음` 인 키워드는 추적하지 않는다. 비교용으로 그냥 둔다.
2. 찾았으면 `hype.history` 에 숫자를 덧붙이고, `hype.value` 갱신, `weeksTracked` 를 1 올린다.
3. **못 찾았으면 history 에 `null` 을 덧붙인다.** 지난주 숫자를 복사하거나 그럴듯한 값을 지어내지 않는다. 빈칸이 정직한 기록이다.
4. `null` 이 2주 연속이면 `level` 을 `식었음` 으로 바꾸고 추적을 중단한다.

추적 결과는 보고에 반드시 적는다. 몇 개 성공하고 몇 개 놓쳤는지.

## 1-B. 탐색 패스 — 새 후보 찾기

필요하면 ToolSearch로 도구를 먼저 로드한다.

**a)** `vidiq_trending_videos { videoFormat:'short', videoTitleLanguage:'en', sortBy:'vph', limit:25 }`

**b)** `vidiq_trend_categories` 로 목록을 받아 **지난 2~3주와 겹치지 않는 카테고리 3개**를 골라
`vidiq_outliers { trendCategories:[고른 것], language:'en', contentType:'short', publishedWithin:'thisWeek', sort:'breakoutScore', limit:20 }`
고른 카테고리는 보고에 적는다(다음 주가 참고함).

**c)** `vidiq_instagram_tiktok_outlier_search` 로 새 후보를 찾는다. **여기서만** query 를 매주 다른 각도로 바꾼다.
`audienceQuery` 는 고정: `"Culture/Region: Korea/Korean; Global: true; Demographics: short-form content creators looking for new formats to copy;"`
`embeddingType` 은 `format`, `resultsPerPlatform` 은 20.

**새 후보에 인스타그램과 틱톡을 최소 1개씩 넣는다.** 지금 목록이 유튜브로 기울어져 있다. 쓸만한 게 없으면 억지로 넣지 말고 보고에 이유를 적는다.

**d)** 국내 비교용 `vidiq_trending_videos { videoFormat:'short', videoTitleLanguage:'ko', sortBy:'vph', limit:30 }` — 파일로 저장하지 않고 대조용으로만 쓴다.

### 반드시 걸러낼 것 둘

- **한 채널에서만 터진 것** — 버린다. 그건 채널이 잘한 거지 포맷이 도는 게 아니다.
- **클립 컴필레이션 계열** — 버린다. `footage compilation`, "Ranking Craziest X", "Instant Karma" 처럼 남의 영상을 모아 재편집하는 포맷은 조회수가 아무리 높아도 저작권 침해 소지가 있어 추천할 수 없다.

남은 것 중 **서로 다른 채널 2곳 이상에서 반복**되는 포맷·밈·챌린지를 고른다.

새로 채택한 키워드에는 **반드시 `trackQuery` 를 만들어 넣는다.** 다음 주에 다시 재려면 이게 있어야 한다. **영문**으로, 포맷을 설명하는 명사구로 쓴다. 한글로 쓰면 영어권 검색이 안 된다.

전체 키워드는 4~7개를 유지한다.

---

## 2. 국내 유입 확인

> **Google Trends 는 이 환경에서 안 된다.** 2026-08-06 실행에서 `trends.google.com` 이 아웃바운드 정책으로 **403 차단**됐다. 로컬에서는 되지만 클라우드에서는 막힌다. 시도하지 말고 크레딧과 시간을 아껴라. (기록: `src/data/references.json`)

키워드마다 한국어로 WebSearch 를 한 번씩 돌려 두 가지를 본다.

1. **그 포맷이 국내에 들어왔나** — 들어왔으면 갭이 닫힌 것이므로 목록에서 빼거나 `부분 존재` 로 낮춘다.
2. **재료가 이미 깔려 있나** — 포맷은 없어도 소재가 국내에 알려져 있으면 진입장벽이 낮다.

`korea.webCheck` 에 한 문장으로 적고, 근거가 Google Trends 면 그걸 명시한다. `korea.checkedAt` 을 오늘 날짜로 채운다.

애매하면 `미확인` 으로 둔다. **지어내지 않는다.**

---

## 3. keywords.json 갱신

스키마를 그대로 유지하며 내용만 바꾼다.

- **`hype.level` 을 근거에 따라 다시 매긴다.** 네 단계: `제일 확실` / `좀 애매` / `아직 모름` / `식었음`. 수치가 꺾였으면 낮춘다. **지난주 등급을 관성으로 유지하지 않는다.**
- **3주 이상 추적되었고 수치가 버틴 키워드만 `제일 확실` 을 받는다.** 1주치만 있으면 아무리 숫자가 커도 최대 `좀 애매`.
- `audience` 는 추론값이므로 `estimated: true` 유지. 다만 **성별 추정은 references.json 의 `platformBaseline` 과 대조한다.** 국내 기준 틱톡은 남성이 약간 많고(54.2%), 인스타그램은 여성이 많다(55.2%). 추정이 기준선과 반대로 가면 근거를 다시 보거나 `혼재` 로 둔다. 연령대는 기준선 자료가 없으니 추론하되 보고에 추정임을 밝힌다. **직업군은 다루지 않는다.**
- `revenue` 는 모델·근거·진입장벽 3종 세트 유지. **수익 금액을 약속하는 표현 금지.**
- `basedOn.periodLabel` 과 `generatedAt` 갱신.

`src/data/businessIdea.json` 의 `narrative`(기/승/전/결)도 갱신한다.

---

## 4. 블로그 초안 (로테이션)

`n % 4` 로 글 종류를 정한다.

| n%4 | 글 종류 | 티스토리 카테고리 |
| --- | --- | --- |
| 0 | 이번 주 갭 리스트 | 이번 주 하입 키워드 |
| 1 | 갭 하나를 깊게 — 한국판으로 어떻게 만들까 | 포맷 활용법 |
| 2 | 이번 주 갭 리스트 | 이번 주 하입 키워드 |
| 3 | **검증편** — 한 달 전 갭이 실제로 국내에 들어왔나 | 이번 주 하입 키워드 |

**글을 쓰기 전에 반드시 `earlycatch-blog/TONE.md` 를 읽는다.** 문체·금지어·구조의 단일 기준이다.

초안은 `/tmp/draft-$TODAY.md` 에 저장한다. **저장소에 커밋하지 않는다** — 공개 저장소라 발행 전 원고를 올리지 않는다.

**쓸 게 없으면 쓰지 않는다.** 신규 키워드가 없고 수치 변동도 미미하면 초안 없이 보고에 "스킵 권장"과 이유를 적는다. 억지로 채운 글이 제일 위험하다.

---

## 5. 이미지 (초안을 쓴 경우에만)

`earlycatch-blog/` 의 템플릿 4개에서 **이번 주 숫자와 문구만** 바꿔 렌더한다. `chart.html` 은 3주 추적 그래프니 `history` 값을 그대로 쓴다.

```bash
CHROME=$(node -e "console.log(require('playwright').chromium.executablePath())" 2>/dev/null) \
  || CHROME=$(which chromium || which chromium-browser || which google-chrome)

"$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars --force-device-scale-factor=1 \
  --screenshot="$PWD/earlycatch-blog/images/01-cover.png" --window-size=1200,630 \
  "file://$PWD/earlycatch-blog/cover.html"
```

출력은 **절대경로**여야 한다. 크기는 이렇다.

| 템플릿 | 크기 | 출력 파일 |
| --- | --- | --- |
| cover.html | 1200×630 | 01-cover.png |
| chart.html | 1200×760 | 02-chart.png |
| gaps.html | 1200×820 | 03-gaps.png |
| thumb.html | 800×800 (정사각) | 00-thumb-sm.png |

thumb 은 목록 썸네일용이라 정사각이다. 커버를 대신 쓰면 좌우가 잘린다.

생성 후 **Read로 열어 한글이 네모로 깨지지 않았는지 눈으로 확인한다.** 깨졌으면 폰트 설치가 안 된 것이니 보고에 적는다.

---

## 6. 검사 2종 (초안을 쓴 경우에만)

```bash
python3 earlycatch-blog/tone_check.py /tmp/draft-$TODAY.md
python3 earlycatch-blog/overlap_check.py /tmp/draft-$TODAY.md --gaps earlycatch-blog/snapshots/$TODAY-keywords.json
```

- **톤 검사** 위반이 나오면 초안을 고치고 다시 돌린다. 단 **규칙 자체가 틀렸을 가능성도 함께 검토한다.**
- **중복 검사**가 "스킵 또는 각도 변경 권장"을 내면, 로테이션의 다른 글 종류로 바꿔 다시 쓰거나 스킵을 권고한다.

---

## 7. 커밋 (이미지와 데이터만)

이 환경에는 git 쓰기 자격증명이 기본으로 없다. **반드시 `$GH_TOKEN` 을 붙여 push 한다.**

```bash
git config user.email "noreply@anthropic.com"
git config user.name "TEO weekly routine"
git add src/data/keywords.json src/data/businessIdea.json earlycatch-blog/images earlycatch-blog/snapshots
git commit -m "주간 갱신 ($TODAY)"

git push "https://x-access-token:${GH_TOKEN}@github.com/teoteobak-commits/earlycatch.git" HEAD:master
```

**초안은 절대 커밋하지 않는다.** push 가 거부되면 `git pull --rebase` 후 위 명령을 한 번만 재시도한다.

`$GH_TOKEN` 이 비어 있거나 push 가 또 실패하면 **거기서 멈추지 말고** 아래를 반드시 한다.

1. 산출물을 **텔레그램으로 직접 보낸다.** 이미지 4장은 `sendPhoto`, `keywords.json` 과 초안은 `sendDocument` 로. 세션이 끝나면 컨테이너가 사라져서 그러지 않으면 그냥 유실된다.
2. 보고에 `[치명적 실패] 저장소 반영 실패` 를 적고 에러 원문을 붙인다.
3. 승인 요청(`TEO발행` 안내)은 하지 않는다. 이미지가 배포되지 않아 발행해도 깨진다.

**절대 조용히 넘어가지 않는다.** 2026-08-06 실행에서 이 단계가 실패해 한 주치 작업이 통째로 날아갔다.

push 후 1~2분이면 Vercel이 자동 배포해서 `https://earlycatch.vercel.app/img/<파일명>` 으로 공개 접근된다.

---

## 8. 텔레그램 보고

환경변수 `$TELEGRAM_BOT_TOKEN`, `$TELEGRAM_CHAT_ID` 를 쓴다. 둘 중 하나라도 비어있으면 전송을 건너뛰고 보고에 적는다.

> **주의** — 이 봇은 다른 프로젝트(쇼츠박스)와 공유한다. 쇼츠박스 루틴이 매시간 돌면서 "승인"이 들어간 메시지를 찾아 **스레드에 자동 게시**한다. 그래서 TEO의 발행 키워드는 "승인"이라는 글자를 쓰지 않고 **`TEO발행`** 을 쓴다. **이 규칙을 절대 바꾸지 않는다.**

모든 메시지를 `[TEO]` 로 시작해 구분되게 한다.

### 8-1. 보고 메시지

```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
  -F chat_id="$TELEGRAM_CHAT_ID" -F text="<보고내용>"
```

형식 예시 (짧게, 판단 근거 위주로):

```
[TEO] 8월 2주차

[추적] 5개 중 4개 성공
  Haaland      70.4만 → 68.1만 (4주차, 유지)
  POV 릴스     1188배 → 940배 (2주차, 인스타그램)
  반려동물     126배 → 203배 (2주차, 틱톡, 상승)
  마리오가족   재측정 실패 → null 기록

[신규] 1개
  틱톡 립싱크 리액션 (312배)

[교차검증] Google Trends
  국내: Haaland 검색 잡힘(재료 깔림), 포맷은 여전히 없음
  미국: 상위 미포착

[블로그] 2회차 — 갭 하나 깊게
  톤 검사   통과
  중복 검사 12% (충분히 다름)
  이미지    4장 배포됨

[판정] 발행 권장
  이유: 틱톡 키워드가 2주 연속 상승, 국내 여전히 0건

괜찮으면 이 메시지에 TEO발행 이라고 답장해주세요.
안 쓰실 거면 TEO보류 라고 해주세요.
```

응답의 `result.message_id` 를 **반드시 기록한다**(python3 로 JSON 파싱 권장). 승인 루틴이 이걸 기준으로 답장을 찾는다.

### 8-2. 초안을 파일로 전송 (초안을 쓴 경우에만)

```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendDocument" \
  -F chat_id="$TELEGRAM_CHAT_ID" -F document=@/tmp/draft-$TODAY.md \
  -F caption="[TEO] $TODAY 초안"
```

응답에서 `result.document.file_id` 를 기록한다. **이게 핵심이다** — 초안을 공개 저장소에 안 올리는 대신 텔레그램에 보관하고, 발행 신호가 오면 그 file_id 로 다시 받아간다.

---

## 9. 상태 파일 커밋

`automation/pending.json` 을 Write로 작성하고 커밋/push 한다.

```json
{
  "status": "pending",
  "date": "TODAY값",
  "post_type": "이번 주 글 종류",
  "category": "티스토리 카테고리명",
  "title": "글 제목",
  "tags": ["태그들"],
  "images": ["01-cover.png", "02-chart.png", "03-gaps.png", "00-thumb-sm.png"],
  "image_base_url": "https://earlycatch.vercel.app/img/",
  "draft_file_id": "8-2에서 받은 file_id",
  "telegram_anchor_message_id": 0,
  "last_update_id": null,
  "attempt_count": 0
}
```

`telegram_anchor_message_id` 는 8-1에서 받은 실제 message_id(숫자)로 채운다.
초안을 안 썼으면 `status` 를 `"skipped"` 로 하고 `skip_reason` 을 넣는다.

---

## 10. 최종 보고

텔레그램에 보낸 내용을 그대로 남기고, 실패한 단계가 있으면 **에러 원문**을 붙인다. 사용한 vidiq 크레딧도 적는다.

---

## 주의사항

- **티스토리에 발행하지 않는다.** 초안까지만이다.
- `_archive/` 는 건드리지 않는다.
- 환경변수 값(토큰)을 로그나 보고에 **절대 출력하지 않는다.**
- 수익 금액을 약속하는 표현을 쓰지 않는다.
