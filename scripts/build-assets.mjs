// Vercel 빌드용 — 블로그 이미지만 배포 대상으로 복사한다.
//
// 대시보드(src/)는 의도적으로 배포하지 않는다. keywords.json 이 번들에 박히면
// 저장소를 비공개로 둔 의미가 없어지기 때문. 공개되는 건 어차피 블로그 글에
// 실릴 이미지뿐이다.

import { cp, mkdir, readdir, writeFile, rm } from 'node:fs/promises'
import { existsSync } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const SRC = path.join(ROOT, 'earlycatch-blog', 'images')
const OUT = path.join(ROOT, 'public-assets')

await rm(OUT, { recursive: true, force: true })
await mkdir(path.join(OUT, 'img'), { recursive: true })

let files = []
if (existsSync(SRC)) {
  files = (await readdir(SRC)).filter((f) => /\.(png|jpe?g|webp|gif|svg)$/i.test(f))
  for (const f of files) {
    await cp(path.join(SRC, f), path.join(OUT, 'img', f))
  }
}

// 루트에 안내 페이지 하나. 검색엔진에는 노출하지 않는다.
await writeFile(
  path.join(OUT, 'index.html'),
  `<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex,nofollow">
<title>Early Catch assets</title>
<style>body{font-family:system-ui,sans-serif;max-width:40rem;margin:4rem auto;padding:0 1rem;color:#191919}
code{background:#f7f6f3;padding:.15rem .4rem;border-radius:4px}</style>
<h1>Early Catch — 이미지 호스팅</h1>
<p>블로그 글에 삽입되는 이미지만 서빙합니다. 대시보드는 배포하지 않습니다.</p>
<p>경로: <code>/img/&lt;파일명&gt;</code></p>
<p>현재 ${files.length}개</p>`,
  'utf-8'
)

await writeFile(
  path.join(OUT, 'robots.txt'),
  'User-agent: *\nDisallow: /\n',
  'utf-8'
)

console.log(`이미지 ${files.length}개를 public-assets/img/ 로 복사했습니다.`)
