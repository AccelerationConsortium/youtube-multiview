import { useState } from 'react';
import './ApiKeyManager.css';

export default function ApiKeyManager({ 
  currentApiKey, 
  onApiKeyUpdate, 
  isVisible, 
  onClose 
}) {
  const [apiKey, setApiKey] = useState(currentApiKey || '');
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState(null);

  const validateApiKey = async (key) => {
    if (!key.trim()) {
      return { valid: false, error: 'API key cannot be empty' };
    }

    try {
      // Test the API key with a simple quota-friendly request
      const testUrl = 'https://www.googleapis.com/youtube/v3/search';
      const testParams = new URLSearchParams({
        part: 'snippet',
        q: 'test',
        maxResults: '1',
        type: 'video',
        key: key.trim()
      });

      const response = await fetch(`${testUrl}?${testParams}`);
      
      if (response.ok) {
        return { valid: true };
      } else {
        const error = await response.json();
        return { 
          valid: false, 
          error: error.error?.message || `HTTP ${response.status}` 
        };
      }
    } catch (error) {
      return { 
        valid: false, 
        error: 'Network error - check your connection' 
      };
    }
  };

  const handleSave = async () => {
    const trimmedKey = apiKey.trim();
    
    if (!trimmedKey) {
      setValidationResult({ valid: false, error: 'Please enter an API key' });
      return;
    }

    setIsValidating(true);
    setValidationResult(null);

    const result = await validateApiKey(trimmedKey);
    setValidationResult(result);

    if (result.valid) {
      onApiKeyUpdate(trimmedKey);
      // Don't close automatically - let user see success message
      setTimeout(() => {
        onClose();
        setValidationResult(null);
      }, 1500);
    }

    setIsValidating(false);
  };

  const handleClear = () => {
    setApiKey('');
    setValidationResult(null);
    onApiKeyUpdate('');
    onClose();
  };

  if (!isVisible) return null;

  return (
    <div className="api-key-modal">
      <div className="modal-backdrop" onClick={onClose} />
      <div className="modal-content">
        <div className="modal-header">
          <h3>
            <i className="fas fa-key"></i>
            YouTube API Key Configuration
          </h3>
          <button className="btn btn-secondary btn-small" onClick={onClose}>
            <i className="fas fa-times"></i>
          </button>
        </div>

        <div className="modal-body">
          <div className="api-key-info">
            <p>
              Enter your YouTube Data API v3 key to enable live playlist features.
              The key is stored locally in your browser and not shared.
            </p>
            
            <div className="info-box">
              <h4>
                <i className="fas fa-info-circle"></i>
                How to get an API key:
              </h4>
              <ol>
                <li>Go to <a href="https://console.developers.google.com/" target="_blank" rel="noopener noreferrer">Google Cloud Console</a></li>
                <li>Create a new project or select existing one</li>
                <li>Enable "YouTube Data API v3"</li>
                <li>Go to "Credentials" → "Create Credentials" → "API Key"</li>
                <li>Copy the generated key</li>
              </ol>
            </div>
          </div>

          <div className="api-key-form">
            <div className="form-group">
              <label>
                <i className="fas fa-key"></i>
                API Key
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => {
                  setApiKey(e.target.value);
                  setValidationResult(null);
                }}
                placeholder="AIza... (39 characters)"
                disabled={isValidating}
              />
              <small>
                Your API key will be stored securely in your browser's local storage
              </small>
            </div>

            {validationResult && (
              <div className={`validation-result ${validationResult.valid ? 'success' : 'error'}`}>
                <i className={`fas ${validationResult.valid ? 'fa-check-circle' : 'fa-exclamation-triangle'}`}></i>
                <span>
                  {validationResult.valid 
                    ? 'API key is valid and working!' 
                    : `Error: ${validationResult.error}`
                  }
                </span>
              </div>
            )}

            <div className="api-key-actions">
              <button
                className="btn btn-primary"
                onClick={handleSave}
                disabled={isValidating || !apiKey.trim()}
              >
                {isValidating ? (
                  <>
                    <i className="fas fa-spinner loading-spinner"></i>
                    Validating...
                  </>
                ) : (
                  <>
                    <i className="fas fa-save"></i>
                    Save & Validate
                  </>
                )}
              </button>

              {currentApiKey && (
                <button
                  className="btn btn-danger"
                  onClick={handleClear}
                  disabled={isValidating}
                >
                  <i className="fas fa-trash"></i>
                  Clear Key
                </button>
              )}

              <button
                className="btn btn-secondary"
                onClick={onClose}
                disabled={isValidating}
              >
                Cancel
              </button>
            </div>
          </div>

          <div className="api-key-features">
            <h4>
              <i className="fas fa-rocket"></i>
              Features enabled with API key:
            </h4>
            <ul>
              <li><i className="fas fa-broadcast-tower"></i> Live playlist streams</li>
              <li><i className="fas fa-sync-alt"></i> Auto-refresh to latest videos</li>
              <li><i className="fas fa-search"></i> Find playlists by device name</li>
              <li><i className="fas fa-clock"></i> Real-time lab monitoring</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
