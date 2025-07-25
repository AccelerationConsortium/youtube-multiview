import { useState, useEffect, useCallback } from 'react';
import { getLatestVideoId, checkVideoStatus } from '../utils/youtube';

// Default refresh interval: 1 minute for status checks (in milliseconds)
const DEFAULT_STATUS_CHECK_INTERVAL = 60000; // 1 minute
// Fallback refresh interval: 10 minutes for full refresh (in milliseconds)
const FALLBACK_REFRESH_INTERVAL = 10 * 60 * 1000; // 10 minutes

export function useLiveUpdates(streams, updateStream, statusCheckInterval = DEFAULT_STATUS_CHECK_INTERVAL) {
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isCheckingStatus, setIsCheckingStatus] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [lastStatusCheck, setLastStatusCheck] = useState(new Date());
  const [refreshErrors, setRefreshErrors] = useState({});
  const [streamStatuses, setStreamStatuses] = useState({});

  // Check status of current videos to see if they've ended
  const checkStreamStatuses = useCallback(async () => {
    const liveStreams = streams.filter(s => s.type === 'live-playlist' && s.videoId);
    
    if (!liveStreams.length) {
      return [];
    }

    setIsCheckingStatus(true);
    const endedStreams = [];
    const newStatuses = { ...streamStatuses };

    for (const stream of liveStreams) {
      try {
        const status = await checkVideoStatus(stream.videoId);
        newStatuses[stream.id] = status;

        // If stream has ended or was recently completed, mark for refresh
        if (status.hasEnded || (!status.isLive && !status.isUpcoming)) {
          endedStreams.push(stream);
          console.log(`Stream ${stream.title} has ended, will refresh`);
        }
      } catch (error) {
        console.error(`Failed to check status for ${stream.title}:`, error);
      }
    }

    setStreamStatuses(newStatuses);
    setIsCheckingStatus(false);
    setLastStatusCheck(new Date());
    
    return endedStreams;
  }, [streams, streamStatuses]);

  const refreshLiveStreams = useCallback(async (streamsToRefresh = null) => {
    const targetStreams = streamsToRefresh || streams.filter(s => s.type === 'live-playlist');
    
    if (!targetStreams.length) {
      return;
    }

    setIsRefreshing(true);
    const errors = {};

    for (const stream of targetStreams) {
      try {
        const latestVideoId = await getLatestVideoId(
          stream.channelId, 
          stream.deviceName, 
          stream.playlistId
        );
        
        if (latestVideoId && latestVideoId !== stream.videoId) {
          console.log(`Updating ${stream.title}: ${stream.videoId} -> ${latestVideoId}`);
          updateStream(stream.id, {
            videoId: latestVideoId,
            lastUpdated: new Date().toISOString()
          });
        }
      } catch (error) {
        console.error(`Failed to refresh ${stream.title}:`, error);
        errors[stream.id] = error.message;
      }
    }

    setRefreshErrors(errors);
    setIsRefreshing(false);
    setLastUpdate(new Date());
  }, [streams, updateStream]);

  // Smart refresh: check status first, then refresh only ended streams
  const smartRefresh = useCallback(async () => {
    const endedStreams = await checkStreamStatuses();
    
    if (endedStreams.length > 0) {
      console.log(`Found ${endedStreams.length} ended streams, refreshing...`);
      await refreshLiveStreams(endedStreams);
    } else {
      console.log('No streams have ended, skipping refresh');
    }
  }, [checkStreamStatuses, refreshLiveStreams]);

  const manualRefresh = async () => {
    await refreshLiveStreams();
  };

  // Status check timer (every minute)
  useEffect(() => {
    const interval = setInterval(() => {
      smartRefresh();
    }, statusCheckInterval);

    return () => clearInterval(interval);
  }, [smartRefresh, statusCheckInterval]);

  // Fallback timer (every 10 minutes) - full refresh regardless of status
  useEffect(() => {
    const interval = setInterval(() => {
      console.log('Fallback refresh: updating all live streams');
      refreshLiveStreams();
    }, FALLBACK_REFRESH_INTERVAL);

    return () => clearInterval(interval);
  }, [refreshLiveStreams]);

  // Initial status check for live streams
  useEffect(() => {
    const hasLiveStreams = streams.some(s => s.type === 'live-playlist');
    if (hasLiveStreams) {
      smartRefresh();
    }
  }, [streams.length]); // Only run when streams array changes

  return {
    isRefreshing,
    isCheckingStatus,
    lastUpdate,
    lastStatusCheck,
    refreshErrors,
    streamStatuses,
    manualRefresh,
    checkStreamStatuses
  };
}
