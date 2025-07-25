import { useState } from 'react';
import './LivePlaylistManager.css';

export default function LivePlaylistManager({ onAddLiveStream, onClose }) {
  const [channelId, setChannelId] = useState('');
  const [deviceName, setDeviceName] = useState('');
  const [title, setTitle] = useState('');
  const [playlistId, setPlaylistId] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleAddLiveStream = async () => {
    if (!channelId || !deviceName || !title) {
      alert('Please fill in Channel ID, Device Name, and Title');
      return;
    }

    setIsLoading(true);
    
    try {
      const newStream = {
        id: `live-${Date.now()}`,
        title,
        type: 'live-playlist',
        channelId,
        deviceName,
        playlistId: playlistId || null,
        videoId: null, // Will be populated on first refresh
        lastUpdated: null
      };

      onAddLiveStream(newStream);
      
      // Reset form
      setChannelId('');
      setDeviceName('');
      setTitle('');
      setPlaylistId('');
      
      if (onClose) onClose();
    } catch (error) {
      console.error('Error adding live stream:', error);
      alert('Failed to add live stream: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="live-playlist-manager">
      <div className="manager-header">
        <h3>🔴 Add Live Playlist Stream</h3>
        {onClose && (
          <button className="btn btn-secondary btn-small" onClick={onClose}>
            <i className="fas fa-times"></i>
          </button>
        )}
      </div>
      
      <div className="manager-content">
        <div className="form-group">
          <label>
            <i className="fas fa-tv"></i> Channel ID *
          </label>
          <input 
            type="text" 
            value={channelId}
            onChange={(e) => setChannelId(e.target.value)}
            placeholder="UC1234567890abcdef..." 
            disabled={isLoading}
          />
          <small>Find this in the channel's URL or "About" page</small>
        </div>

        <div className="form-group">
          <label>
            <i className="fas fa-microchip"></i> Device Name *
          </label>
          <input 
            type="text" 
            value={deviceName}
            onChange={(e) => setDeviceName(e.target.value)}
            placeholder="OT-2, Plate Reader, etc." 
            disabled={isLoading}
          />
          <small>Will search for playlists containing this name</small>
        </div>

        <div className="form-group">
          <label>
            <i className="fas fa-tag"></i> Display Title *
          </label>
          <input 
            type="text" 
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Lab A - OT-2 Live Stream" 
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label>
            <i className="fas fa-list"></i> Playlist ID (Optional)
          </label>
          <input 
            type="text" 
            value={playlistId}
            onChange={(e) => setPlaylistId(e.target.value)}
            placeholder="PL1234567890abcdef..." 
            disabled={isLoading}
          />
          <small>Leave empty to auto-find by device name</small>
        </div>

        <div className="manager-actions">
          <button 
            className="btn btn-primary" 
            onClick={handleAddLiveStream}
            disabled={isLoading || !channelId || !deviceName || !title}
          >
            {isLoading ? (
              <>
                <i className="fas fa-spinner loading-spinner"></i>
                Adding...
              </>
            ) : (
              <>
                <i className="fas fa-plus"></i>
                Add Live Stream
              </>
            )}
          </button>
        </div>
      </div>

      <div className="manager-help">
        <h4>💡 How to find Channel ID:</h4>
        <ol>
          <li>Go to the YouTube channel</li>
          <li>Click "About" tab</li>
          <li>Look for "Channel ID" or check the URL</li>
          <li>Should start with "UC" followed by 22 characters</li>
        </ol>
      </div>
    </div>
  );
}
