"""
YouTube utility functions for fetching live streams using YouTube Data API v3.
Based on the implementation referenced from HuggingFace spaces.
"""
import os
import requests
import json
from datetime import datetime
from typing import List, Dict, Optional

class YouTubeStreamFetcher:
    """Utility class for fetching YouTube live streams using API key."""
    
    def __init__(self, api_key: str = None):
        """Initialize with YouTube Data API key."""
        self.api_key = api_key or os.environ.get('YOUTUBE_API_KEY')
        if not self.api_key:
            raise ValueError("YouTube API key is required. Set YOUTUBE_API_KEY environment variable.")
        
        self.base_url = "https://www.googleapis.com/youtube/v3"
    
    def get_channel_live_streams(self, channel_id: str, max_results: int = 10) -> List[Dict]:
        """
        Get live streams from a specific YouTube channel.
        
        Args:
            channel_id: YouTube channel ID (e.g., "UCxxxxxx")
            max_results: Maximum number of results to return
            
        Returns:
            List of dictionaries containing stream information
        """
        try:
            # First, search for live videos from the channel
            search_url = f"{self.base_url}/search"
            search_params = {
                'part': 'snippet',
                'channelId': channel_id,
                'eventType': 'live',
                'type': 'video',
                'maxResults': max_results,
                'key': self.api_key
            }
            
            response = requests.get(search_url, params=search_params)
            response.raise_for_status()
            data = response.json()
            
            streams = []
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                snippet = item['snippet']
                
                stream_info = {
                    'id': video_id,
                    'title': snippet.get('title', 'Unknown Title'),
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'channel_title': snippet.get('channelTitle', 'Unknown Channel'),
                    'published_at': snippet.get('publishedAt'),
                    'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url'),
                    'description': snippet.get('description', '')[:200]  # Truncate description
                }
                streams.append(stream_info)
            
            return streams
            
        except requests.RequestException as e:
            print(f"Error fetching streams from channel {channel_id}: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error: {e}")
            return []
    
    def get_multiple_channels_streams(self, channel_ids: List[str], max_results_per_channel: int = 5) -> List[Dict]:
        """
        Get live streams from multiple YouTube channels.
        
        Args:
            channel_ids: List of YouTube channel IDs
            max_results_per_channel: Maximum results per channel
            
        Returns:
            List of all streams from all channels
        """
        all_streams = []
        for channel_id in channel_ids:
            streams = self.get_channel_live_streams(channel_id, max_results_per_channel)
            all_streams.extend(streams)
        
        # Sort by published date (newest first)
        all_streams.sort(key=lambda x: x.get('published_at', ''), reverse=True)
        return all_streams
    
    def get_video_details(self, video_id: str) -> Optional[Dict]:
        """
        Get detailed information about a specific video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Video details dictionary or None if not found
        """
        try:
            videos_url = f"{self.base_url}/videos"
            params = {
                'part': 'snippet,liveStreamingDetails,status',
                'id': video_id,
                'key': self.api_key
            }
            
            response = requests.get(videos_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('items'):
                return None
            
            item = data['items'][0]
            snippet = item['snippet']
            live_details = item.get('liveStreamingDetails', {})
            status = item.get('status', {})
            
            return {
                'id': video_id,
                'title': snippet.get('title'),
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'channel_title': snippet.get('channelTitle'),
                'is_live': live_details.get('actualStartTime') is not None and live_details.get('actualEndTime') is None,
                'live_start_time': live_details.get('actualStartTime'),
                'live_end_time': live_details.get('actualEndTime'),
                'privacy_status': status.get('privacyStatus'),
                'thumbnail': snippet.get('thumbnails', {}).get('medium', {}).get('url')
            }
            
        except requests.RequestException as e:
            print(f"Error fetching video details for {video_id}: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

def get_latest_streams_for_channels(channel_ids: List[str], api_key: str = None) -> List[Dict]:
    """
    Convenience function to get latest live streams from specified channels.
    
    Args:
        channel_ids: List of YouTube channel IDs to monitor
        api_key: YouTube Data API key (optional, can use environment variable)
        
    Returns:
        List of live stream information
    """
    try:
        fetcher = YouTubeStreamFetcher(api_key)
        return fetcher.get_multiple_channels_streams(channel_ids)
    except Exception as e:
        print(f"Error in get_latest_streams_for_channels: {e}")
        return []

# Example usage and configuration
DEFAULT_MONITORED_CHANNELS = [
    # Add your default channel IDs here
    # Example: "UCxxxxxxxxxxxxxxxxxxxxxx"
]

if __name__ == "__main__":
    # Test the functionality
    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        print("Please set YOUTUBE_API_KEY environment variable to test")
    else:
        fetcher = YouTubeStreamFetcher(api_key)
        # Test with a known channel (replace with actual channel ID)
        test_channel = "UCxxxxxxxxxxxxxxxxxxxxxx"  # Replace with real channel ID
        streams = fetcher.get_channel_live_streams(test_channel)
        print(f"Found {len(streams)} live streams")
        for stream in streams:
            print(f"- {stream['title']}: {stream['url']}")