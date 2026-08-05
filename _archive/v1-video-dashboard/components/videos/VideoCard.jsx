import { useState } from 'react'
import { PlayIcon, TrendingUpIcon, UsersIcon } from '../icons/Icons'
import { formatViews, daysSince } from '../../data/videos'

export default function VideoCard({ video }) {
  const [thumbFailed, setThumbFailed] = useState(false)

  return (
    <article className="video-card">
      <div className="video-thumb">
        {!thumbFailed ? (
          <img
            className="video-thumb-img"
            src={`https://i.ytimg.com/vi/${video.id}/hqdefault.jpg`}
            alt=""
            loading="lazy"
            referrerPolicy="no-referrer"
            onError={() => setThumbFailed(true)}
          />
        ) : (
          <div className="video-thumb-fallback">
            <span>{video.category}</span>
          </div>
        )}
        <div className="video-thumb-overlay">
          <PlayIcon className="video-thumb-play" />
        </div>
        <span className="video-category">{video.category}</span>
      </div>

      <div className="video-body">
        <h3 className="video-title">{video.title}</h3>
        <p className="video-channel">
          {video.channel} · {daysSince(video.uploadedAt)}일 전
        </p>

        <div className="video-stats">
          <span className="video-stat">
            <TrendingUpIcon className="video-stat-icon" />
            시간당 {formatViews(video.vph)}
          </span>
          <span className="video-stat video-stat--sub">누적 {formatViews(video.views)}</span>
        </div>

        <div className="video-audience">
          <UsersIcon className="video-audience-icon" />
          <span>
            {video.estimatedGender} · {video.estimatedAgeGroup}
          </span>
        </div>

        <div className="video-keywords">
          {video.keywords.slice(0, 2).map((k) => (
            <span key={k} className="keyword-chip">
              #{k}
            </span>
          ))}
        </div>
      </div>
    </article>
  )
}
