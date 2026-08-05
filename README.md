# Early Catch / TEO 리서치

해외(유튜브·인스타·틱톡)에서 뜨는데 **국내엔 아직 없는** 키워드를 매주 찾아, 오디언스와 수익모델 후보까지 붙여주는 개인용 도구.

찾은 것은 두 갈래로 나간다.
- **대시보드** — `src/` (React + Vite)
- **블로그** — [Early Catch](https://weusedtodo.tistory.com) 주간 발행

## 구조

```
src/data/keywords.json     단일 데이터 소스. 키워드 / 하입 강도 / 오디언스(추정) / 수익모델
src/                       대시보드 화면
earlycatch-blog/           블로그 자산 (아래 참고)
product-*/                 크몽 판매 상품 (가이드, 스카우팅 리포트)
_archive/                  폐기된 v1 코드와 폐기 사유
```

### earlycatch-blog/

| 파일 | 용도 |
| --- | --- |
| `TONE.md` | **글쓰기 단일 기준.** 새 글을 쓰기 전 반드시 읽는다 |
| `tone_check.py` | 문체 규칙 검사 (볼드·이모지·금지어·문단·리듬) |
| `overlap_check.py` | 지난 글과 겹치는지 검사. 주간 발행의 최대 위험이 중복이다 |
| `cover/gaps/chart/thumb.html` | 이미지 템플릿. 숫자·문구만 바꿔 렌더 |
| `published/` `snapshots/` `drafts/` | 발행 이력 / 주간 스냅샷 / 초안 |
| `imgserve.py` | 이미지 삽입용 임시 CORS 서버 (로컬 전용) |

이미지 렌더:
```bash
msedge --headless --disable-gpu --force-device-scale-factor=1 --hide-scrollbars \
  --screenshot="<절대경로>/images/01-cover.png" --window-size=1200,630 "file://<절대경로>/cover.html"
```
크기 — cover 1200×630 / gaps 1200×820 / chart 1200×760 / **thumb 800×800(정사각)**

## 원칙

**오디언스는 추정치다.** 어떤 플랫폼도 임의 콘텐츠의 연령·성별을 알려주지 않는다. `keywords.json`의 `audience`는 콘텐츠 성격에서 추론한 값이며 `estimated: true`로 표시된다. v1은 이 구분을 안 해서 폐기했다(`_archive/README.md` 참고).

**직업군은 다루지 않는다.** 제공하는 플랫폼이 없다. 대신 "소비 맥락"(출퇴근·퇴근 후·주말)으로 대체했다.

**클립 컴필레이션은 제외한다.** 남의 영상을 모아 재편집하는 포맷은 조회수가 높아도 저작권 침해 소지가 있어 후보에서 뺀다.

**수익 금액을 약속하지 않는다.** 확신도는 네 단계로만 표시한다 — 제일 확실 / 좀 애매 / 아직 모름 / 식었음.

## 비밀 정보

`.secrets/`는 커밋되지 않는다. 텔레그램 봇 토큰은 `set_token.py`로 넣는다(입력이 화면에 표시되지 않음).

```bash
python set_token.py
python notify_telegram.py --setup   # 봇에게 말 한 번 건 뒤 실행
python notify_telegram.py --test
```
