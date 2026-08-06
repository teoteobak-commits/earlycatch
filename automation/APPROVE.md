# TEO 발행 신호 확인 지시서

주간 리서치가 보낸 블로그 초안에 사용자가 응답했는지 확인하고, 발행 신호가 왔으면 초안을 저장소에 확정 저장한다.

사용자는 실행 중에 없다. 질문하지 말고 판단해서 진행한다.
**대부분의 실행은 할 일이 없어서 바로 끝난다. 그게 정상이다.**

---

## 1. 할 일이 있는지 먼저 확인 — 없으면 즉시 종료

저장소를 pull 하고 `automation/pending.json` 을 읽는다.

다음 중 하나라도 해당하면 **아무것도 하지 말고 즉시 종료**한다. 텔레그램도 보내지 않는다.

- 파일이 없다
- `status` 가 `pending` 이 아니다 (`approved` / `rejected` / `skipped` 등)
- `attempt_count` 가 20 이상이다 (한 주 내내 답이 없었으므로 포기)

이 경우 최종 보고는 한 줄이면 된다. 예: `대기 중인 초안 없음. 종료.`

---

## 2. 텔레그램에서 답장 확인

```bash
curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getUpdates?offset=-30"
```

> **주의** — 이 봇은 다른 프로젝트(쇼츠박스)와 공유한다. 관계없는 메시지가 잔뜩 섞여 있다.

다음 조건을 **모두** 만족하는 메시지만 찾는다.

1. `message.chat.id` 가 `$TELEGRAM_CHAT_ID` 와 같다
2. `message.date` 가 pending.json 의 `date` 이후다
3. 본문에 다음 중 하나가 들어있다
   - `TEO발행` 또는 `TEO 발행` → **발행 신호**
   - `TEO보류` 또는 `TEO 보류` → **보류 신호**

`message.reply_to_message.message_id` 가 pending.json 의 `telegram_anchor_message_id` 와 같으면 확실하다. 답장이 아니어도 위 3조건을 만족하면 유효한 신호로 본다 — 사용자가 답장 대신 그냥 입력할 수 있다.

> **중요** — `TEO` 접두사가 없는 그냥 "발행", "승인", "ok", "좋아" 같은 메시지는 **절대 신호로 처리하지 않는다.** 다른 프로젝트 대화와 섞여 있어 오인식 위험이 크다. 특히 쇼츠박스는 "승인"을 자기 키워드로 쓰므로 그 단어는 무시한다.

### 신호가 없으면

pending.json 의 `attempt_count` 를 1 올려서 커밋/push 하고 종료한다. **텔레그램은 보내지 않는다** — 두 시간마다 알림이 오면 짜증난다.

### 보류 신호면

`status` 를 `rejected` 로 바꾸고 메시지 본문을 `reject_reason` 에 넣어 커밋/push 한다.
텔레그램에 `[TEO] 보류합니다. 이번 주는 올리지 않겠습니다.` 를 보내고 종료한다.

---

## 3. 발행 신호면 — 초안 회수

pending.json 의 `draft_file_id` 로 텔레그램에서 초안 파일을 다시 받아온다. **초안은 공개 저장소에 없고 텔레그램에만 있다.**

```bash
FILE_PATH=$(curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getFile?file_id=<draft_file_id>" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['result']['file_path'])")
curl -s -o /tmp/approved.md "https://api.telegram.org/file/bot$TELEGRAM_BOT_TOKEN/$FILE_PATH"
```

받은 파일이 비어있거나 200바이트 미만이면 **회수 실패**다. 그 경우 `status` 는 그대로 두고, 텔레그램에 `[TEO] 초안 회수 실패. 원본 파일을 다시 확인해주세요.` 를 보낸 뒤 종료한다. **실패를 성공처럼 처리하지 않는다.**

---

## 4. 확정 저장

회수한 초안을 `earlycatch-blog/published/{date}-{슬러그}.md` 로 저장한다. 슬러그는 제목에서 만들되 영문 소문자와 하이픈만 쓴다.

파일 맨 위에 프론트매터를 붙인다.

```yaml
---
date: (pending.json 의 date)
title: (pending.json 의 title)
category: (pending.json 의 category)
tags: (pending.json 의 tags)
status: approved
approved_at: (지금 시각)
tistory_url:
---
```

`tistory_url` 은 비워둔다. 실제 발행 후 채운다.

pending.json 의 `status` 를 `approved` 로 바꾸고 `approved_at` 을 넣는다.

둘 다 커밋하고 push 한다. 이 환경에는 git 쓰기 자격증명이 기본으로 없으니 **반드시 `$GH_TOKEN` 을 붙인다.**

```bash
git config user.email "noreply@anthropic.com"
git config user.name "TEO approve routine"
git commit -m "초안 발행 확정 ($TODAY)"
git push "https://x-access-token:${GH_TOKEN}@github.com/teoteobak-commits/earlycatch.git" HEAD:master
```

push 가 거부되면 `git pull --rebase` 후 한 번만 재시도한다.
그래도 실패하면 회수한 초안을 텔레그램으로 다시 보내고(`sendDocument`), `status` 는 `pending` 그대로 두고, 실패 사실을 알린다. **성공한 척하지 않는다.**

---

## 5. 완료 알림

```bash
curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
  -F chat_id="$TELEGRAM_CHAT_ID" -F text="<내용>"
```

내용:

```
[TEO] 발행 신호 확인했습니다.

초안을 저장소에 확정 저장했습니다.
earlycatch-blog/published/(파일명)

티스토리는 자동으로 안 올라갑니다. 2024년 2월에 글쓰기 API가 닫혀서
브라우저로 직접 올려야 합니다.
PC 켜시면 클로드에게 "블로그 발행" 이라고 말씀해주세요.
저장소에서 이 글을 찾아 이미지까지 올려드립니다.
```

---

## 주의사항

- **티스토리에 발행하지 않는다.** 확정 저장까지만이다.
- 환경변수 값(토큰)을 로그나 보고에 **절대 출력하지 않는다.**
- 신호가 애매하면 처리하지 않는다. 다음 실행에서 다시 본다.
