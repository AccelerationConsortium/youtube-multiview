import { createYouTubeEmbedUrl } from '../utils/youtube';
import './ZoomModal.css';

export default function ZoomModal({ stream, isVisible, onClose }) {
  if (!isVisible || !stream) return null;

  const videoId = stream.videoId || stream.id;

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      onClose();
    }
  };

  return (
    <div 
      className="zoom-modal" 
      onClick={handleBackdropClick}
      onKeyDown={handleKeyDown}
      tabIndex={-1}
    >
      <div className="modal-backdrop" />
      <div className="zoom-modal-content">
        <div className="zoom-header">
          <div className="zoom-title">
            <h2>{stream.title}</h2>
            {stream.type === 'live-playlist' && (
              <div className="stream-badges">
                <span className="badge live">
                  <i className="fas fa-broadcast-tower"></i>
                  LIVE
                </span>
                {stream.lastUpdated && (
                  <span className="last-update">
                    Updated: {new Date(stream.lastUpdated).toLocaleTimeString()}
                  </span>
                )}
              </div>
            )}
          </div>
          <div className="zoom-actions">
            <button
              className="btn btn-secondary"
              onClick={() => {
                if (document.fullscreenElement) {
                  document.exitFullscreen();
                } else {
                  document.documentElement.requestFullscreen();
                }
              }}
              title="Toggle fullscreen"
            >
              <i className="fas fa-expand"></i>
            </button>
            <button
              className="btn btn-secondary"
              onClick={onClose}
              title="Close zoom"
            >
              <i className="fas fa-times"></i>
            </button>
          </div>
        </div>
        
        <div className="zoom-video-container">
          {videoId ? (
            <iframe
              src={createYouTubeEmbedUrl(videoId, true, false)} // Don't mute in zoom
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              title={stream.title}
            />
          ) : (
            <div className="video-loading">
              <i className="fas fa-spinner loading-spinner"></i>
              <p>Loading video...</p>
            </div>
          )}
        </div>

        {stream.type === 'live-playlist' && (
          <div className="zoom-info">
            <div className="stream-meta">
              <div className="meta-item">
                <i className="fas fa-microchip"></i>
                <span>Device: {stream.deviceName}</span>
              </div>
              <div className="meta-item">
                <i className="fas fa-tv"></i>
                <span>Channel: {stream.channelId}</span>
              </div>
              {stream.playlistId && (
                <div className="meta-item">
                  <i className="fas fa-list"></i>
                  <span>Playlist: {stream.playlistId}</span>
                </div>
              )}
            </div>
          </div>
        )}

        {stream.type === 'static' && (
          <div className="zoom-info">
            <div className="stream-meta">
              <div className="meta-item">
                <i className="fas fa-link"></i>
                <span>URL: {stream.url}</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
