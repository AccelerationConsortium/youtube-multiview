import { useState, useEffect } from 'react';

const STORAGE_KEY = 'youtube-multiview-streams';
const GIST_ID_KEY = 'youtube-multiview-gist-id';

// Default streams for new installations
const DEFAULT_STREAMS = [
  {
    id: 'dQw4w9WgXcQ',
    title: 'Sample Stream 1',
    url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
    type: 'static'
  },
  {
    id: 'jNQXAC9IVRw',
    title: 'Sample Stream 2',
    url: 'https://www.youtube.com/watch?v=jNQXAC9IVRw',
    type: 'static'
  },
  {
    id: '9bZkp7q19f0',
    title: 'Sample Stream 3',
    url: 'https://www.youtube.com/watch?v=9bZkp7q19f0',
    type: 'static'
  }
];

export function useStreams() {
  const [streams, setStreams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [gistId, setGistId] = useState(localStorage.getItem(GIST_ID_KEY) || '');

  // Load streams from localStorage on mount
  useEffect(() => {
    loadStreams();
  }, []);

  const loadStreams = () => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsedStreams = JSON.parse(saved);
        setStreams(parsedStreams);
      } else {
        setStreams(DEFAULT_STREAMS);
        saveStreamsToStorage(DEFAULT_STREAMS);
      }
    } catch (error) {
      console.error('Error loading streams:', error);
      setStreams(DEFAULT_STREAMS);
    } finally {
      setLoading(false);
    }
  };

  const saveStreamsToStorage = (newStreams) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newStreams));
    } catch (error) {
      console.error('Error saving streams:', error);
    }
  };

  const updateStreams = (newStreams) => {
    setStreams(newStreams);
    saveStreamsToStorage(newStreams);
  };

  const addStream = (stream) => {
    const newStreams = [...streams, { ...stream, id: stream.id || Date.now().toString() }];
    updateStreams(newStreams);
  };

  const deleteStream = (streamId) => {
    const newStreams = streams.filter(s => s.id !== streamId);
    updateStreams(newStreams);
  };

  const updateStream = (streamId, updates) => {
    const newStreams = streams.map(s => 
      s.id === streamId ? { ...s, ...updates } : s
    );
    updateStreams(newStreams);
  };

  // Gist integration
  const saveToGist = async () => {
    if (!gistId) {
      throw new Error('Please enter a Gist ID first');
    }

    const gistData = {
      streams,
      config: {
        lastUpdate: new Date().toISOString(),
        version: '1.0.0'
      }
    };

    try {
      const response = await fetch(`https://api.github.com/gists/${gistId}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          files: {
            'youtube-multiview-config.json': {
              content: JSON.stringify(gistData, null, 2)
            }
          }
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to save to Gist: ${response.status}`);
      }

      localStorage.setItem(GIST_ID_KEY, gistId);
      return true;
    } catch (error) {
      console.error('Error saving to Gist:', error);
      throw error;
    }
  };

  const loadFromGist = async () => {
    if (!gistId) {
      throw new Error('Please enter a Gist ID first');
    }

    try {
      const response = await fetch(`https://api.github.com/gists/${gistId}`);
      
      if (!response.ok) {
        throw new Error(`Failed to load from Gist: ${response.status}`);
      }

      const gistData = await response.json();
      const configFile = gistData.files['youtube-multiview-config.json'];
      
      if (!configFile) {
        throw new Error('Configuration file not found in Gist');
      }

      const config = JSON.parse(configFile.content);
      updateStreams(config.streams || []);
      localStorage.setItem(GIST_ID_KEY, gistId);
      
      return true;
    } catch (error) {
      console.error('Error loading from Gist:', error);
      throw error;
    }
  };

  return {
    streams,
    loading,
    gistId,
    setGistId,
    addStream,
    deleteStream,
    updateStream,
    updateStreams,
    saveToGist,
    loadFromGist
  };
}
