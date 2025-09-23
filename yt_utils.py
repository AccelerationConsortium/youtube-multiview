"""
YouTube API utilities for playlist and video management with pagination support
"""

import os
import re
import requests
from typing import List, Dict, Optional, Tuple
import json
from datetime import datetime

# YouTube API configuration
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY', '')
YOUTUBE_API_BASE = 'https://www.googleapis.com/youtube/v3'

# Global variable for runtime API key override
_runtime_api_key = None

def set_api_key(api_key: str) -> None:
    """Set API key at runtime"""
    global _runtime_api_key
    _runtime_api_key = api_key.strip() if api_key else None

def get_api_key() -> str:
    """Get the current API key (runtime override or environment)"""
    return _runtime_api_key or YOUTUBE_API_KEY

def check_api_key() -> Tuple[bool, str]:
    """Check if YouTube API key is available and valid"""
    api_key = get_api_key()
    if not api_key:
        return False, "No API key available"
    
    # Test the API key with a simple request
    url = f"{YOUTUBE_API_BASE}/search"
    params = {
        'part': 'snippet',
        'q': 'test',
        'maxResults': 1,
        'key': api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return True, "API key is valid"
        elif response.status_code == 403:
            return False, "API key is invalid or quota exceeded"
        else:
            return False, f"API error: {response.status_code}"
    except Exception as e:
        return False, f"Connection error: {str(e)}"

def get_all_playlist_videos(playlist_id: str) -> List[Dict]:
    """
    Get ALL videos from a YouTube playlist, handling pagination for large playlists.
    
    Args:
        playlist_id: YouTube playlist ID
        
    Returns:
        List of video dictionaries with id, title, publishedAt, and other details
    """
    api_key = get_api_key()
    if not api_key:
        return []
    
    all_videos = []
    next_page_token = None
    max_requests = 20  # Prevent infinite loops (20 * 50 = 1000 videos max)
    request_count = 0
    
    while request_count < max_requests:
        # Build API URL with pagination
        url = f"{YOUTUBE_API_BASE}/playlistItems"
        params = {
            'part': 'snippet',
            'playlistId': playlist_id,
            'maxResults': 50,  # Maximum allowed by API
            'key': api_key
        }
        
        if next_page_token:
            params['pageToken'] = next_page_token
            
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'items' not in data:
                break
                
            # Extract video information
            for item in data['items']:
                snippet = item.get('snippet', {})
                video_info = {
                    'id': snippet.get('resourceId', {}).get('videoId'),
                    'title': snippet.get('title', 'Unknown Title'),
                    'publishedAt': snippet.get('publishedAt', ''),
                    'thumbnails': snippet.get('thumbnails', {}),
                    'position': snippet.get('position', 0)
                }
                if video_info['id']:  # Only add if we have a valid video ID
                    all_videos.append(video_info)
            
            # Check if there are more pages
            next_page_token = data.get('nextPageToken')
            if not next_page_token:
                break
                
            request_count += 1
            
        except Exception as e:
            print(f"Error fetching playlist videos (page {request_count + 1}): {e}")
            break
    
    print(f"Retrieved {len(all_videos)} videos from playlist {playlist_id}")
    return all_videos

def check_videos_live_status(video_ids: List[str]) -> Dict[str, Dict]:
    """
    Check live status for multiple videos efficiently.
    
    Args:
        video_ids: List of YouTube video IDs (max 50 per API call)
        
    Returns:
        Dictionary mapping video_id to video details including live status
    """
    api_key = get_api_key()
    if not api_key or not video_ids:
        return {}
    
    # YouTube API allows up to 50 IDs per request
    video_batches = [video_ids[i:i+50] for i in range(0, len(video_ids), 50)]
    all_video_data = {}
    
    for batch in video_batches:
        videos_url = f"{YOUTUBE_API_BASE}/videos"
        videos_params = {
            'part': 'snippet,liveStreamingDetails',
            'id': ','.join(batch),
            'key': api_key
        }
        
        try:
            response = requests.get(videos_url, params=videos_params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            for item in data.get('items', []):
                video_id = item['id']
                snippet = item['snippet']
                live_details = item.get('liveStreamingDetails', {})
                
                # Determine if video is currently live
                is_live = (
                    live_details.get('actualStartTime') and 
                    not live_details.get('actualEndTime')
                ) or snippet.get('liveBroadcastContent') == 'live'
                
                all_video_data[video_id] = {
                    'id': video_id,
                    'title': snippet['title'],
                    'publishedAt': snippet['publishedAt'],
                    'thumbnails': snippet.get('thumbnails', {}),
                    'is_live': is_live,
                    'live_details': live_details,
                    'liveBroadcastContent': snippet.get('liveBroadcastContent', 'none')
                }
                
        except Exception as e:
            print(f"Error checking live status for video batch: {e}")
            continue
    
    return all_video_data

def get_latest_video_from_playlist(playlist_id: str) -> Optional[Dict]:
    """
    Get the latest live video from a YouTube playlist, with fallback to most recent video.
    Now supports large playlists with pagination.
    
    Args:
        playlist_id: YouTube playlist ID
        
    Returns:
        Dictionary with video details including URL, or None if no videos found
    """
    if not playlist_id:
        return None
    
    # Step 1: Get ALL videos from the playlist (with pagination)
    all_videos = get_all_playlist_videos(playlist_id)
    if not all_videos:
        return None
    
    print(f"Found {len(all_videos)} total videos in playlist")
    
    # Step 2: Sort by publishedAt to get most recent videos first
    try:
        sorted_videos = sorted(
            all_videos, 
            key=lambda x: datetime.fromisoformat(x['publishedAt'].replace('Z', '+00:00')), 
            reverse=True
        )
    except Exception as e:
        print(f"Error sorting videos by date: {e}")
        # Fallback to original order
        sorted_videos = all_videos
    
    # Step 3: Check live status for the most recent videos (up to 50 at a time)
    recent_video_ids = [v['id'] for v in sorted_videos[:100]]  # Check up to 100 most recent
    video_details = check_videos_live_status(recent_video_ids)
    
    # Step 4: Find the most recent live video
    for video in sorted_videos[:100]:  # Only check the 100 most recent
        video_id = video['id']
        if video_id in video_details:
            video_info = video_details[video_id]
            if video_info['is_live']:
                print(f"Found live video: {video_info['title']}")
                return {
                    'id': video_id,
                    'title': video_info['title'],
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'thumbnail': video_info['thumbnails'].get('medium', {}).get('url', ''),
                    'published_at': video_info['publishedAt'],
                    'is_live': True,
                    'playlist_id': playlist_id
                }
    
    # Step 5: If no live video found, return the most recent video
    if sorted_videos:
        latest_video = sorted_videos[0]
        video_id = latest_video['id']
        video_info = video_details.get(video_id, latest_video)
        
        print(f"No live video found, returning most recent: {video_info.get('title', latest_video['title'])}")
        return {
            'id': video_id,
            'title': video_info.get('title', latest_video['title']),
            'url': f"https://www.youtube.com/watch?v={video_id}",
            'thumbnail': latest_video['thumbnails'].get('medium', {}).get('url', ''),
            'published_at': latest_video['publishedAt'],
            'is_live': False,
            'playlist_id': playlist_id
        }
    
    return None

def extract_playlist_id(url: str) -> Optional[str]:
    """Extract playlist ID from YouTube playlist URL"""
    if not url:
        return None
    
    # Pattern: list=PLAYLIST_ID
    match = re.search(r'[?&]list=([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    return None

def extract_video_id(url: str) -> Optional[str]:
    """Extract video ID from YouTube video URL"""
    if not url:
        return None
    
    # Pattern 1: v=VIDEO_ID
    match = re.search(r'[?&]v=([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    
    # Pattern 2: youtu.be/VIDEO_ID
    match = re.search(r'youtu\.be/([a-zA-Z0-9_-]+)', url)
    if match:
        return match.group(1)
    
    return None

def check_video_embeddable(video_id: str) -> Tuple[bool, str]:
    """Check if a video is embeddable using YouTube oEmbed API"""
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        response = requests.get(oembed_url)
        
        if response.status_code == 200:
            data = response.json()
            return True, f"✅ Video '{data.get('title', 'Unknown')}' is embeddable"
        elif response.status_code == 401:
            return False, "❌ Video is private or restricted"
        elif response.status_code == 404:
            return False, "❌ Video not found or unavailable"
        else:
            return False, f"❌ Video embedding check failed (status: {response.status_code})"
    except Exception as e:
        return False, f"❌ Error checking video: {str(e)}"

def get_video_info(video_id: str) -> Optional[Dict]:
    """Get video information by ID"""
    api_key = get_api_key()
    if not api_key:
        return None
    
    url = f"{YOUTUBE_API_BASE}/videos"
    params = {
        'part': 'snippet,liveStreamingDetails',
        'id': video_id,
        'key': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get('items'):
            item = data['items'][0]
            snippet = item['snippet']
            live_details = item.get('liveStreamingDetails', {})
            
            return {
                'id': video_id,
                'title': snippet['title'],
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'thumbnail': snippet['thumbnails'].get('medium', {}).get('url', ''),
                'published_at': snippet['publishedAt'],
                'is_live': bool(live_details),
                'live_status': live_details.get('actualStartTime') is not None
            }
        return None
    except Exception as e:
        print(f"Error fetching video info: {e}")
        return None

def parse_device_name_from_title(title: str) -> Optional[str]:
    """Extract device name from stream title pattern"""
    # Pattern: "OT2-LCM-TrainingLab stream @AC cam-fb7p, 2025-07-24 UTC 01:00"
    # or: "mycobot-AprilTag-SDLT stream @AC cam-w9fo, 2025-07-24 UTC 01:00"
    
    patterns = [
        r'^([^-]+-[^-]+-[^-]+)\s+stream\s+@AC',  # device-setup-lab pattern
        r'^([^\s]+)\s+stream\s+@AC',  # simple device pattern
    ]
    
    for pattern in patterns:
        match = re.search(pattern, title)
        if match:
            return match.group(1)
    
    return None

def export_streams_to_csv(streams: List[Dict]) -> str:
    """Export streams to CSV format"""
    if not streams:
        return "url,title,type,playlist_id\n"
    
    csv_lines = ["url,title,type,playlist_id"]
    
    for stream in streams:
        stream_type = "playlist" if stream.get('playlist_id') else "video"
        playlist_id = stream.get('playlist_id', '')
        
        # Escape commas and quotes in title
        title = stream['title'].replace('"', '""')
        if ',' in title:
            title = f'"{title}"'
        
        csv_lines.append(f"{stream['url']},{title},{stream_type},{playlist_id}")
    
    return "\n".join(csv_lines)

def import_streams_from_csv(csv_content: str) -> List[Dict]:
    """Import streams from CSV content"""
    streams = []
    lines = csv_content.strip().split('\n')
    
    if not lines or lines[0].lower().startswith('url'):
        lines = lines[1:]  # Skip header
    
    for line in lines:
        if not line.strip():
            continue
            
        parts = line.split(',')
        if len(parts) >= 2:
            url = parts[0].strip()
            title = parts[1].strip().strip('"')
            
            if url and title:
                # Determine if it's a playlist or video
                playlist_id = extract_playlist_id(url)
                video_id = extract_video_id(url)
                
                if playlist_id or video_id:
                    streams.append({
                        'url': url,
                        'title': title,
                        'playlist_id': playlist_id,
                        'id': video_id or f"playlist_{playlist_id}"
                    })
    
    return streams
