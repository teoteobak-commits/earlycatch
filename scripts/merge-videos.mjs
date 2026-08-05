// 리서치 갱신 시 사용하는 병합 스크립트.
// 사용법: 새로 수집한 영상 배열(우리 스키마 형식)을 scripts/incoming.json에 저장한 뒤
//   node scripts/merge-videos.mjs
// 를 실행하면 src/data/videos.json에 id 기준으로 병합된다.
// 이미 있던 영상은 조회수/시간당조회수 등 최신값으로 갱신되고 firstSeenAt은 유지되며,
// 처음 보는 영상은 새로 추가된다. 실행 후 incoming.json은 지워도 된다.
import { existsSync, readFileSync, writeFileSync, unlinkSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const __dirname = dirname(fileURLToPath(import.meta.url))
const videosPath = join(__dirname, '../src/data/videos.json')
const incomingPath = join(__dirname, 'incoming.json')

if (!existsSync(incomingPath)) {
  console.error('scripts/incoming.json이 없습니다. 새로 수집한 영상 배열을 이 파일에 먼저 저장하세요.')
  process.exit(1)
}

const existing = JSON.parse(readFileSync(videosPath, 'utf-8'))
const incoming = JSON.parse(readFileSync(incomingPath, 'utf-8'))

const now = new Date().toISOString()
const byId = new Map(existing.map((v) => [v.id, v]))

let added = 0
let updated = 0

for (const video of incoming) {
  const prev = byId.get(video.id)
  const firstSeenAt = prev?.firstSeenAt ?? now
  byId.set(video.id, { ...video, firstSeenAt, collectedAt: now })
  prev ? updated++ : added++
}

const merged = [...byId.values()].sort((a, b) => b.vph - a.vph)

writeFileSync(videosPath, JSON.stringify(merged, null, 2) + '\n')
unlinkSync(incomingPath)

console.log(
  `병합 완료: 신규 ${added}건, 갱신 ${updated}건, 전체 ${merged.length}건 → src/data/videos.json`
)
