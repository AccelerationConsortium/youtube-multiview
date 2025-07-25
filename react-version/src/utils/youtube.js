// YouTube API utilities - converted from Python yt_utils.py

// Get API key from localStorage or environment
function getApiKey() {
  return localStorage.getItem('youtube-api-key') || import.meta.env.VITE_YT_API_KEY;
}

export async function getLatestVideoId(channelId, deviceName = null, playlistId = null) {
  const YT_API_KEY = getApiKey();
  
  if (!YT_API_KEY) {
    throw new Error('YouTube API key not configured. Please set your API key in the app settings.');
  }
  if (!deviceName && !playlistId) {
    throw new Error("Must specify either deviceName or playlistId");
  }

  if (deviceName && playlistId) {
    console.log("Both deviceName and playlistId provided. Using playlistId.");
  }

  // Step 1: Find playlist by device name if needed
  if (!playlistId && deviceName) {
    const playlistsUrl = 'https://www.googleapis.com/youtube/v3/playlists';
    const playlistsParams = new URLSearchParams({
      part: 'snippet',
      channelId: channelId,
      maxResults: '1000',
      key: YT_API_KEY
    });

    try {
      const playlistsRes = await fetch(`${playlistsUrl}?${playlistsParams}`);
      if (!playlistsRes.ok) throw new Error(`HTTP ${playlistsRes.status}`);
      
      const playlistsData = await playlistsRes.json();
      const playlists = playlistsData.items || [];

      for (const playlist of playlists) {
        if (playlist.snippet.title.toLowerCase().includes(deviceName.toLowerCase())) {
          playlistId = playlist.id;
          break;
        }
      }

      if (!playlistId) {
        throw new Error(`No playlist found matching device name '${deviceName}'`);
      }
    } catch (error) {
      console.error('Error fetching playlists:', error);
      throw error;
    }
  }

  // Step 2: Get latest video from playlist
  if (playlistId) {
    const playlistUrl = 'https://www.googleapis.com/youtube/v3/playlistItems';
    const playlistParams = new URLSearchParams({
      part: 'snippet,contentDetails',
      playlistId: playlistId,
      maxResults: '10',
      key: YT_API_KEY
    });

    try {
      const playlistRes = await fetch(`${playlistUrl}?${playlistParams}`);
      if (!playlistRes.ok) {
        const errorText = await playlistRes.text();
        console.error(`YouTube API error ${playlistRes.status}: ${errorText}`);
        throw new Error(`HTTP ${playlistRes.status}: ${errorText}`);
      }
      
      const playlistData = await playlistRes.json();
      
      // Check for API errors (like private playlists)
      if (playlistData.error) {
        console.error('YouTube API returned error:', playlistData.error);
        throw new Error(`YouTube API error: ${playlistData.error.message || 'Unknown error'}`);
      }
      
      const playlistItems = playlistData.items || [];

      if (!playlistItems.length) {
        console.log(`No items found in playlist ${playlistId} - might be empty or private`);
        return null;
      }

      // Filter out private videos (they might show up but be inaccessible)
      const accessibleItems = playlistItems.filter(item => {
        const snippet = item.snippet;
        // Check if video snippet indicates it's accessible
        return snippet && snippet.resourceId && snippet.resourceId.videoId && 
               snippet.title !== 'Private video' && snippet.title !== 'Deleted video';
      });

      if (!accessibleItems.length) {
        console.log(`No accessible videos found in playlist ${playlistId}`);
        return null;
      }

      // Sort by publish date (newest first)
      const sortedItems = accessibleItems.sort((a, b) => 
        new Date(b.snippet.publishedAt) - new Date(a.snippet.publishedAt)
      );

      return sortedItems[0].snippet.resourceId.videoId;
    } catch (error) {
      console.error('Error fetching playlist items:', error);
      throw error;
    }
  }

  // Fallback: Search API for latest video
  const searchUrl = 'https://www.googleapis.com/youtube/v3/search';
  const searchParams = new URLSearchParams({
    part: 'snippet',
    channelId: channelId,
    maxResults: '1',
    order: 'date',
    type: 'video',
    key: YT_API_KEY
  });

  try {
    const searchRes = await fetch(`${searchUrl}?${searchParams}`);
    if (!searchRes.ok) throw new Error(`HTTP ${searchRes.status}`);
    
    const searchData = await searchRes.json();
    const items = searchData.items || [];

    return items.length ? items[0].id.videoId : null;
  } catch (error) {
    console.error('Error searching videos:', error);
    throw error;
  }
}

export function extractVideoId(url) {
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)/,
    /(?:youtube\.com\/live\/)([^&\n?#]+)/
  ];
  
  for (const pattern of patterns) {
    const match = url.match(pattern);
    if (match) {
      return match[1];
    }
  }
  return null;
}

export function createYouTubeEmbedUrl(videoId, autoplay = true, mute = true) {
  const params = new URLSearchParams({
    rel: '0',
    modestbranding: '1'
  });
  
  if (autoplay) params.set('autoplay', '1');
  if (mute) params.set('mute', '1');
  
  return `https://www.youtube.com/embed/${videoId}?${params.toString()}`;
}

export function isValidYouTubeUrl(url) {
  return extractVideoId(url) !== null;
}

// API Key management
export function setApiKey(apiKey) {
  if (apiKey && apiKey.trim()) {
    localStorage.setItem('youtube-api-key', apiKey.trim());
  } else {
    localStorage.removeItem('youtube-api-key');
  }
}

export function getStoredApiKey() {
  return localStorage.getItem('youtube-api-key');
}

export function hasApiKey() {
  return Boolean(getApiKey());
}

// Check if a video/stream has ended or is no longer live
export async function checkVideoStatus(videoId) {
  const YT_API_KEY = getApiKey();
  
  if (!YT_API_KEY || !videoId) {
    return { isLive: false, hasEnded: false, error: 'Missing API key or video ID' };
  }

  try {
    const url = 'https://www.googleapis.com/youtube/v3/videos';
    const params = new URLSearchParams({
      part: 'snippet,liveStreamingDetails',
      id: videoId,
      key: YT_API_KEY
    });

    const response = await fetch(`${url}?${params}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    
    const data = await response.json();
    const video = data.items?.[0];
    
    if (!video) {
      return { isLive: false, hasEnded: true, error: 'Video not found' };
    }

    const snippet = video.snippet;
    const liveDetails = video.liveStreamingDetails;
    
    // Check if it's a live stream
    const isLiveContent = snippet.liveBroadcastContent === 'live';
    const isUpcoming = snippet.liveBroadcastContent === 'upcoming';
    const hasEnded = snippet.liveBroadcastContent === 'none' && liveDetails?.actualEndTime;
    
    // For completed videos, check if they were recently uploaded (within last hour)
    const isRecentlyCompleted = liveDetails?.actualEndTime && 
      (new Date() - new Date(liveDetails.actualEndTime)) < (60 * 60 * 1000); // 1 hour

    return {
      isLive: isLiveContent,
      isUpcoming: isUpcoming,
      hasEnded: hasEnded || isRecentlyCompleted,
      publishedAt: snippet.publishedAt,
      actualStartTime: liveDetails?.actualStartTime,
      actualEndTime: liveDetails?.actualEndTime,
      liveBroadcastContent: snippet.liveBroadcastContent
    };
  } catch (error) {
    console.error('Error checking video status:', error);
    return { isLive: false, hasEnded: false, error: error.message };
  }
}
