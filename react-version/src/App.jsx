import { useState, useEffect } from 'react';
import VideoGrid from './components/VideoGrid';
import StreamPanel from './components/StreamPanel';
import ZoomModal from './components/ZoomModal';
import Notification from './components/Notification';
import ApiKeyManager from './components/ApiKeyManager';
import { useStreams } from './hooks/useStreams';
import { useLiveUpdates } from './hooks/useLiveUpdates';
import { hasApiKey, getStoredApiKey, setApiKey } from './utils/youtube';
import './App.css';

function App() {
  // State management
  const {
    streams,
    loading,
    gistId,
    setGistId,
    addStream,
    deleteStream,
    updateStream,
    saveToGist,
    loadFromGist
  } = useStreams();

  const [gridSize, setGridSize] = useState(1);
  const [selectedStreams, setSelectedStreams] = useState([]);
  const [showStreamPanel, setShowStreamPanel] = useState(false);
  const [zoomedStream, setZoomedStream] = useState(null);
  const [notification, setNotification] = useState(null);
  const [showApiKeyManager, setShowApiKeyManager] = useState(false);
  const [currentApiKey, setCurrentApiKey] = useState(getStoredApiKey());

  // Live updates
  const { isRefreshing, lastUpdate, refreshErrors, manualRefresh } = useLiveUpdates(
    streams,
    updateStream,
    60000 // 1 minute refresh interval
  );

  // Check API key availability
  const apiKeyAvailable = hasApiKey();

  // Show notification
  const showNotification = (message, type = 'info') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  };

  // Handle grid size change
  const handleGridSizeChange = (size) => {
    setGridSize(size);
    // Trim selected streams if new grid is smaller
    if (selectedStreams.length > size) {
      setSelectedStreams(selectedStreams.slice(0, size));
    }
  };

  // Handle stream selection for grid
  const handleStreamSelect = (stream, slotIndex) => {
    const newSelectedStreams = [...selectedStreams];
    
    // If slotIndex is provided, replace that specific slot
    if (typeof slotIndex === 'number') {
      newSelectedStreams[slotIndex] = stream;
    } else {
      // Add to next available slot
      const nextSlot = newSelectedStreams.length;
      if (nextSlot < gridSize) {
        newSelectedStreams[nextSlot] = stream;
      }
    }
    
    setSelectedStreams(newSelectedStreams);
  };

  // Handle stream removal from grid
  const handleStreamRemove = (index) => {
    const newSelectedStreams = selectedStreams.filter((_, i) => i !== index);
    setSelectedStreams(newSelectedStreams);
  };

  // Handle adding new stream
  const handleAddStream = (stream) => {
    addStream(stream);
    showNotification(`Added stream: ${stream.title}`, 'success');
  };

  // Handle deleting stream
  const handleDeleteStream = (streamId) => {
    // Remove from selected streams if present
    setSelectedStreams(selectedStreams.filter(s => s.id !== streamId));
    deleteStream(streamId);
    showNotification('Stream deleted', 'info');
  };

  // Handle stream zoom
  const handleStreamZoom = (stream) => {
    setZoomedStream(stream);
  };

  // Handle Gist operations
  const handleSaveToGist = async () => {
    try {
      await saveToGist();
      showNotification('Configuration saved to Gist successfully!', 'success');
    } catch (error) {
      showNotification(`Failed to save to Gist: ${error.message}`, 'error');
    }
  };

  const handleLoadFromGist = async () => {
    try {
      await loadFromGist();
      setSelectedStreams([]); // Clear current selection
      showNotification('Configuration loaded from Gist successfully!', 'success');
    } catch (error) {
      showNotification(`Failed to load from Gist: ${error.message}`, 'error');
    }
  };

  // Handle API key update
  const handleApiKeyUpdate = (newApiKey) => {
    setApiKey(newApiKey);
    setCurrentApiKey(newApiKey);
    if (newApiKey) {
      showNotification('API key saved successfully! Live features are now enabled.', 'success');
    } else {
      showNotification('API key cleared. Live features are disabled.', 'info');
    }
  };

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        if (zoomedStream) {
          setZoomedStream(null);
        } else if (showStreamPanel) {
          setShowStreamPanel(false);
        } else if (showApiKeyManager) {
          setShowApiKeyManager(false);
        }
      } else if (e.key === 'm' || e.key === 'M') {
        if (!zoomedStream && !showApiKeyManager) {
          setShowStreamPanel(!showStreamPanel);
        }
      } else if (e.key >= '1' && e.key <= '3') {
        if (!zoomedStream && !showStreamPanel && !showApiKeyManager) {
          const sizes = { '1': 1, '2': 4, '3': 9 };
          handleGridSizeChange(sizes[e.key]);
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [zoomedStream, showStreamPanel, showApiKeyManager]);

  // Show errors for refresh failures
  useEffect(() => {
    const errorMessages = Object.values(refreshErrors);
    if (errorMessages.length > 0) {
      showNotification(`Live update errors: ${errorMessages.join(', ')}`, 'warning');
    }
  }, [refreshErrors]);

  if (loading) {
    return (
      <div className="app">
        <div className="app-header">
          <div className="app-title">
            <i className="fas fa-tv logo"></i>
            <h1>AC Hardware Streams</h1>
          </div>
          <div className="loading-spinner">
            <i className="fas fa-spinner loading-spinner"></i>
          </div>
        </div>
        <div className="main-content">
          <div className="skeleton" style={{ height: '100%' }}></div>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="app-title">
          <i className="fas fa-tv logo"></i>
          <h1>AC Hardware Streams</h1>
        </div>
        
        <div className="status-info">
          <div className={`api-status ${apiKeyAvailable ? 'connected' : 'warning'}`}>
            <i className={`fas ${apiKeyAvailable ? 'fa-check-circle' : 'fa-exclamation-triangle'}`}></i>
            <span>{apiKeyAvailable ? 'API Connected' : 'API Key Missing'}</span>
          </div>
          
          {streams.filter(s => s.type === 'live-playlist').length > 0 && (
            <div className={`refresh-status ${isRefreshing ? 'refreshing' : ''}`}>
              <i className={`fas ${isRefreshing ? 'fa-spinner loading-spinner' : 'fa-clock'}`}></i>
              <span>
                {isRefreshing ? 'Refreshing...' : `Last: ${lastUpdate.toLocaleTimeString()}`}
              </span>
            </div>
          )}
        </div>

        <div className="header-actions">
          {!apiKeyAvailable && (
            <button
              className="btn btn-secondary"
              onClick={() => setShowApiKeyManager(true)}
              title="Configure YouTube API key"
            >
              <i className="fas fa-key"></i>
              API Key
            </button>
          )}
          
          <button
            className="btn btn-primary"
            onClick={() => setShowStreamPanel(!showStreamPanel)}
            title="Manage streams (M)"
          >
            <i className="fas fa-cogs"></i>
            Manage
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        <div className={`content-area ${showStreamPanel ? 'panel-open' : ''}`}>
          <VideoGrid
            gridSize={gridSize}
            onGridSizeChange={handleGridSizeChange}
            selectedStreams={selectedStreams}
            onStreamSelect={handleStreamSelect}
            onStreamRemove={handleStreamRemove}
            onStreamZoom={handleStreamZoom}
            streams={streams}
          />
        </div>

        {/* Stream Management Panel */}
        <StreamPanel
          streams={streams}
          onAddStream={handleAddStream}
          onDeleteStream={handleDeleteStream}
          isVisible={showStreamPanel}
          onClose={() => setShowStreamPanel(false)}
          gistId={gistId}
          setGistId={setGistId}
          onSaveToGist={handleSaveToGist}
          onLoadFromGist={handleLoadFromGist}
          lastUpdate={lastUpdate}
          isRefreshing={isRefreshing}
          onManualRefresh={manualRefresh}
          onShowApiKeyManager={() => setShowApiKeyManager(true)}
        />
      </main>

      {/* Zoom Modal */}
      <ZoomModal
        stream={zoomedStream}
        isVisible={!!zoomedStream}
        onClose={() => setZoomedStream(null)}
      />

      {/* API Key Manager */}
      <ApiKeyManager
        currentApiKey={currentApiKey}
        onApiKeyUpdate={handleApiKeyUpdate}
        isVisible={showApiKeyManager}
        onClose={() => setShowApiKeyManager(false)}
      />

      {/* Notifications */}
      <Notification
        message={notification?.message}
        type={notification?.type}
        isVisible={!!notification}
        onClose={() => setNotification(null)}
      />

      {/* API Key Warning */}
      {!apiKeyAvailable && (
        <div className="error-message" style={{ 
          position: 'fixed', 
          bottom: '20px', 
          left: '20px', 
          right: '20px',
          zIndex: 1000,
          maxWidth: '600px',
          margin: '0 auto'
        }}>
          <i className="fas fa-exclamation-triangle"></i>
          <span>
            YouTube API key not configured. Live playlist features will not work. 
            <button 
              className="btn btn-secondary btn-small" 
              onClick={() => setShowApiKeyManager(true)}
              style={{ marginLeft: '1rem' }}
            >
              Configure Now
            </button>
          </span>
        </div>
      )}
    </div>
  );
}

export default App;
