#!/usr/bin/env python3
"""
Test script for YouTube API functionality
"""

import os
from yt_utils import get_latest_video_from_playlist, check_api_key

def test_api():
    """Test API key and playlist functionality"""
    print("Testing YouTube API functionality...")
    
    # Check API key
    api_available, message = check_api_key()
    print(f"API Status: {message}")
    
    if not api_available:
        print("❌ No API key available for testing")
        return
    
    # Test with the sample playlist
    playlist_id = "PL8uZlc2CEpelrYXunUzUOMJC17wEhiP6Q"
    print(f"\nTesting playlist: {playlist_id}")
    
    try:
        latest_video = get_latest_video_from_playlist(playlist_id)
        if latest_video:
            print("✅ Successfully fetched latest video:")
            print(f"   Title: {latest_video['title']}")
            print(f"   Video ID: {latest_video['id']}")
            print(f"   URL: {latest_video['url']}")
            print(f"   Published: {latest_video['published_at']}")
        else:
            print("❌ No video found in playlist")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api()
