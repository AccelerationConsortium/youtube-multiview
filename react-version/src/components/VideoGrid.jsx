import { useState } from 'react';
import { createYouTubeEmbedUrl } from '../utils/youtube';
import './VideoGrid.css';

export default function VideoGrid({ 
  gridSize, 
  onGridSizeChange, 
  selectedStreams, 
  onStreamSelect, 
  onStreamRemove, 
  onStreamZoom,
  streams 
}) {
  const [showStreamSelector, setShowStreamSelector] = useState(false);
  const [selectingForSlot, setSelectingForSlot] = useState(null);

  const handleSlotClick = (slotIndex) => {
    if (slotIndex < selectedStreams.length) {
      // Slot has a stream, zoom it
      const stream = selectedStreams[slotIndex];
      onStreamZoom(stream);
    } else {
      // Empty slot, show stream selector
      setSelectingForSlot(slotIndex);
      setShowStreamSelector(true);
    }
  };

  const handleStreamSelection = (stream) => {
    onStreamSelect(stream, selectingForSlot);
    setShowStreamSelector(false);
    setSelectingForSlot(null);
  };

  const getGridClass = () => {
    switch (gridSize) {
      case 1: return 'grid-1';
      case 4: return 'grid-4';
      case 9: return 'grid-9';
      default: return 'grid-1';
    }
  };

  const getVideoId = (stream) => {
    return stream.videoId || stream.id;
  };

  return (
    <div className="video-grid-container">
      {/* Grid Controls */}
      <div className="grid-controls">
        <div className="grid-size-buttons">
          {[1, 4, 9].map(size => (
            <button
              key={size}
              className={`btn grid-btn ${gridSize === size ? 'active' : ''}`}
              onClick={() => onGridSizeChange(size)}
              data-size={size}
            >
              {size === 1 && <><i className="fas fa-square"></i> 1×1</>}
              {size === 4 && <><i className="fas fa-th-large"></i> 2×2</>}
              {size === 9 && <><i className="fas fa-th"></i> 3×3</>}
            </button>
          ))}
        </div>
        
        <div className="grid-info">
          <span className="selected-count">
            {selectedStreams.length} / {gridSize} streams selected
          </span>
        </div>
      </div>

      {/* Video Grid */}
      <div className={`video-grid ${getGridClass()}`}>
        {Array.from({ length: gridSize }, (_, index) => {
          const stream = selectedStreams[index];
          const videoId = stream ? getVideoId(stream) : null;
          
          return (
            <div
              key={index}
              className={`video-slot ${!stream ? 'empty' : ''}`}
              onClick={() => handleSlotClick(index)}
            >
              {stream && videoId ? (
                <>
                  <div className="video-header">
                    <div className="video-title">{stream.title}</div>
                    <div className="video-actions">
                      <button
                        className="btn btn-secondary btn-small"
                        onClick={(e) => {
                          e.stopPropagation();
                          onStreamZoom(stream);
                        }}
                        title="Zoom video"
                      >
                        <i className="fas fa-expand"></i>
                      </button>
                      <button
                        className="btn btn-danger btn-small"
                        onClick={(e) => {
                          e.stopPropagation();
                          onStreamRemove(index);
                        }}
                        title="Remove from grid"
                      >
                        <i className="fas fa-times"></i>
                      </button>
                    </div>
                  </div>
                  <div className="video-container">
                    <iframe
                      src={createYouTubeEmbedUrl(videoId, true, true)}
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                      title={stream.title}
                    />
                  </div>
                  {stream.type === 'live-playlist' && (
                    <div className="stream-indicator">
                      <i className="fas fa-broadcast-tower"></i>
                      <span>LIVE</span>
                      {stream.lastUpdated && (
                        <span className="last-update">
                          {new Date(stream.lastUpdated).toLocaleTimeString()}
                        </span>
                      )}
                    </div>
                  )}
                </>
              ) : (
                <div className="empty-slot">
                  <i className="fas fa-plus-circle"></i>
                  <div>Click to add stream</div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Stream Selector Modal */}
      {showStreamSelector && (
        <div className="stream-selector-modal">
          <div className="modal-backdrop" onClick={() => setShowStreamSelector(false)} />
          <div className="modal-content">
            <div className="modal-header">
              <h3>Select a Stream</h3>
              <button
                className="btn btn-secondary btn-small"
                onClick={() => setShowStreamSelector(false)}
              >
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-body">
              {streams.length === 0 ? (
                <div className="empty-state">
                  <i className="fas fa-tv"></i>
                  <p>No streams available</p>
                  <p>Add some streams first using the manage panel</p>
                </div>
              ) : (
                <div className="stream-selection-grid">
                  {streams.map(stream => {
                    const isSelected = selectedStreams.some(s => s.id === stream.id);
                    const videoId = getVideoId(stream);
                    
                    return (
                      <div
                        key={stream.id}
                        className={`selectable-stream ${isSelected ? 'selected' : ''}`}
                        onClick={() => !isSelected && handleStreamSelection(stream)}
                      >
                        <div className="stream-preview">
                          {videoId && (
                            <img 
                              src={`https://img.youtube.com/vi/${videoId}/mqdefault.jpg`}
                              alt={stream.title}
                              onError={(e) => {
                                e.target.style.display = 'none';
                              }}
                            />
                          )}
                          <div className="stream-overlay">
                            {stream.type === 'live-playlist' && (
                              <span className="live-badge">
                                <i className="fas fa-broadcast-tower"></i>
                                LIVE
                              </span>
                            )}
                          </div>
                        </div>
                        <div className="stream-details">
                          <h4>{stream.title}</h4>
                          {stream.type === 'static' && (
                            <p className="stream-url">{stream.url}</p>
                          )}
                          {stream.type === 'live-playlist' && (
                            <p className="stream-device">Device: {stream.deviceName}</p>
                          )}
                        </div>
                        {isSelected && (
                          <div className="selected-indicator">
                            <i className="fas fa-check-circle"></i>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
