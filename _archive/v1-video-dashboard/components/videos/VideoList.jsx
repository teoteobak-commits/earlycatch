import VideoCard from './VideoCard'

export default function VideoList({ videos }) {
  if (videos.length === 0) {
    return (
      <div className="empty-state">
        <p>조건에 맞는 영상이 없어요. 필터를 조정해보세요.</p>
      </div>
    )
  }

  return (
    <div className="video-grid">
      {videos.map((v) => (
        <VideoCard key={v.id} video={v} />
      ))}
    </div>
  )
}
