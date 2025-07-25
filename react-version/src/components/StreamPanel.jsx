import { useState } from 'react';
import { extractVideoId, isValidYouTubeUrl } from '../utils/youtube';
import LivePlaylistManager from './LivePlaylistManager';
import './StreamPanel.css';

export default function StreamPanel({ 
  streams, 
  onAddStream, 
  onDeleteStream, 
  isVisible, 
  onClose,
  gistId,
  setGistId,
  onSaveToGist,
  onLoadFromGist,
  lastUpdate,
  isRefreshing,
  onManualRefresh,
  onShowApiKeyManager
}) {
  const [url, setUrl] = useState('');
  const [title, setTitle] = useState('');
  const [showLiveManager, setShowLiveManager] = useState(false);
  const [activeTab, setActiveTab] = useState('static');

  const handleAddStaticStream = () => {
    if (!url || !title) {
      alert('Please enter both URL and title');
      return;
    }

    if (!isValidYouTubeUrl(url)) {
      alert('Please enter a valid YouTube URL');
      return;
    }

    const videoId = extractVideoId(url);
    const newStream = {
      id: videoId,
      title,
      url,
      type: 'static'
    };

    onAddStream(newStream);
    setUrl('');
    setTitle('');
  };

  const handleAddLiveStream = (liveStream) => {
    onAddStream(liveStream);
    setShowLiveManager(false);
  };

  const formatLastUpdate = (date) => {
    if (!date) return 'Never';
    return new Intl.DateTimeFormat('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).format(date);
  };

  if (!isVisible) return null;

  return (
    <div className="stream-panel">
      <div className="panel-header">
        <h2>
          <i className="fas fa-cogs"></i>
          Manage Streams
        </h2>
        <button className="btn btn-secondary btn-small" onClick={onClose}>
          <i className="fas fa-times"></i>
        </button>
      </div>

      <div className="panel-content">
        {/* Stream Type Tabs */}
        <div className="stream-tabs">
          <button 
            className={`tab-btn ${activeTab === 'static' ? 'active' : ''}`}
            onClick={() => setActiveTab('static')}
          >
            <i className="fas fa-link"></i>
            Static Streams
          </button>
          <button 
            className={`tab-btn ${activeTab === 'live' ? 'active' : ''}`}
            onClick={() => setActiveTab('live')}
          >
            <i className="fas fa-broadcast-tower"></i>
            Live Playlists
          </button>
          <button 
            className={`tab-btn ${activeTab === 'sync' ? 'active' : ''}`}
            onClick={() => setActiveTab('sync')}
          >
            <i className="fas fa-cloud"></i>
            Sync
          </button>
        </div>

        {/* Static Streams Tab */}
        {activeTab === 'static' && (
          <div className="tab-content">
            <div className="add-stream-form">
              <h3>📺 Add Static Stream</h3>
              <div className="form-group">
                <label>YouTube URL</label>
                <input 
                  type="url" 
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="https://www.youtube.com/watch?v=..." 
                />
              </div>
              <div className="form-group">
                <label>Stream Title</label>
                <input 
                  type="text" 
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="My Lab Stream" 
                />
              </div>
              <button 
                className="btn btn-primary" 
                onClick={handleAddStaticStream}
                disabled={!url || !title}
              >
                <i className="fas fa-plus"></i>
                Add Stream
              </button>
            </div>
          </div>
        )}

        {/* Live Playlists Tab */}
        {activeTab === 'live' && (
          <div className="tab-content">
            <div className="live-refresh-status">
              <div className="refresh-info">
                <span className={`status-indicator ${isRefreshing ? 'refreshing' : 'idle'}`}>
                  <i className={`fas ${isRefreshing ? 'fa-spinner loading-spinner' : 'fa-clock'}`}></i>
                </span>
                <span>Last update: {formatLastUpdate(lastUpdate)}</span>
              </div>
              <button 
                className="btn btn-secondary btn-small" 
                onClick={onManualRefresh}
                disabled={isRefreshing}
              >
                <i className={`fas fa-sync-alt ${isRefreshing ? 'loading-spinner' : ''}`}></i>
                Refresh Now
              </button>
            </div>

            <div className="api-key-prompt">
              <div className="api-info">
                <i className="fas fa-info-circle"></i>
                <span>Live playlist features require a YouTube API key.</span>
              </div>
              <button 
                className="btn btn-primary btn-small"
                onClick={onShowApiKeyManager}
              >
                <i className="fas fa-key"></i>
                Configure API Key
              </button>
            </div>
            
            <LivePlaylistManager 
              onAddLiveStream={handleAddLiveStream}
            />
          </div>
        )}

        {/* Sync Tab */}
        {activeTab === 'sync' && (
          <div className="tab-content">
            <div className="gist-sync">
              <h3>☁️ GitHub Gist Sync</h3>
              <p>Save and share your stream configuration using GitHub Gist.</p>
              
              <div className="form-group">
                <label>Gist ID</label>
                <input 
                  type="text" 
                  value={gistId}
                  onChange={(e) => setGistId(e.target.value)}
                  placeholder="1234567890abcdef..." 
                />
                <small>
                  Create a new gist at <a href="https://gist.github.com" target="_blank" rel="noopener noreferrer">gist.github.com</a>
                </small>
              </div>
              
              <div className="gist-actions">
                <button 
                  className="btn btn-primary" 
                  onClick={onSaveToGist}
                  disabled={!gistId}
                >
                  <i className="fas fa-upload"></i>
                  Save to Gist
                </button>
                <button 
                  className="btn btn-secondary" 
                  onClick={onLoadFromGist}
                  disabled={!gistId}
                >
                  <i className="fas fa-download"></i>
                  Load from Gist
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Streams List */}
        <div className="streams-list">
          <h3>
            Current Streams ({streams.length})
            {streams.filter(s => s.type === 'live-playlist').length > 0 && (
              <span className="live-count">
                {streams.filter(s => s.type === 'live-playlist').length} live
              </span>
            )}
          </h3>
          
          {streams.length === 0 ? (
            <div className="empty-state">
              <i className="fas fa-tv"></i>
              <p>No streams added yet</p>
            </div>
          ) : (
            <div className="streams-container">
              {streams.map(stream => (
                <div key={stream.id} className={`stream-item ${stream.type}`}>
                  <div className="stream-info">
                    <div className="stream-header">
                      <span className="stream-title">{stream.title}</span>
                      <div className="stream-badges">
                        {stream.type === 'live-playlist' && (
                          <span className="badge live">
                            <i className="fas fa-broadcast-tower"></i>
                            LIVE
                          </span>
                        )}
                        {stream.type === 'static' && (
                          <span className="badge static">
                            <i className="fas fa-link"></i>
                            STATIC
                          </span>
                        )}
                      </div>
                    </div>
                    
                    <div className="stream-details">
                      {stream.type === 'static' && (
                        <div className="stream-url">{stream.url}</div>
                      )}
                      {stream.type === 'live-playlist' && (
                        <div className="stream-meta">
                          <div>Device: {stream.deviceName}</div>
                          <div>Channel: {stream.channelId}</div>
                          {stream.lastUpdated && (
                            <div className="last-updated">
                              Updated: {new Date(stream.lastUpdated).toLocaleTimeString()}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="stream-actions">
                    <button 
                      className="btn btn-danger btn-small" 
                      onClick={() => onDeleteStream(stream.id)}
                      title="Delete stream"
                    >
                      <i className="fas fa-trash"></i>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
