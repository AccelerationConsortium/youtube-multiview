#!/usr/bin/env python3
"""
Test script for YouTube API integration
"""
import os
import json
from yt_utils import YouTubeStreamFetcher

def test_youtube_api_key_handling():
    """Test YouTube API key handling"""
    print("Testing YouTube API key handling...")
    
    # Test without API key
    original_key = os.environ.get('YOUTUBE_API_KEY')
    if 'YOUTUBE_API_KEY' in os.environ:
        del os.environ['YOUTUBE_API_KEY']
    
    try:
        fetcher = YouTubeStreamFetcher()
        print("✗ Should have raised ValueError for missing API key")
        return False
    except ValueError as e:
        if "API key is required" in str(e):
            print("✓ Correctly raises error when API key is missing")
        else:
            print(f"✗ Wrong error message: {e}")
            return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return False
    
    # Restore original key if it existed
    if original_key:
        os.environ['YOUTUBE_API_KEY'] = original_key
        
    return True

def test_api_endpoints():
    """Test new API endpoints exist"""
    print("\nTesting API endpoint availability...")
    
    try:
        import app
        client = app.app.test_client()
        
        # Test status endpoint
        response = client.get('/api/status')
        if response.status_code == 200:
            print("✓ /api/status endpoint is accessible")
            status_data = json.loads(response.data)
            expected_keys = ['youtube_api_configured', 'monitored_channels', 'streams_count']
            for key in expected_keys:
                if key in status_data:
                    print(f"✓ Status includes {key}")
                else:
                    print(f"✗ Status missing {key}")
                    return False
        else:
            print(f"✗ /api/status returned status code {response.status_code}")
            return False
        
        # Test refresh endpoint (should fail without API key but should exist)
        response = client.post('/api/refresh-streams')
        if response.status_code in [400, 500]:  # Expected to fail without proper config
            print("✓ /api/refresh-streams endpoint exists (fails as expected without config)")
        else:
            print(f"? /api/refresh-streams returned unexpected status {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing API endpoints: {e}")
        return False

def test_backwards_compatibility():
    """Test that existing functionality still works"""
    print("\nTesting backwards compatibility...")
    
    try:
        import app
        client = app.app.test_client()
        
        # Test existing streams API
        response = client.get('/api/streams')
        if response.status_code == 200:
            print("✓ /api/streams endpoint still works")
            data = json.loads(response.data)
            if 'streams' in data:
                print("✓ Response includes streams data")
            else:
                print("✗ Response missing streams data")
                return False
        else:
            print(f"✗ /api/streams returned status code {response.status_code}")
            return False
            
        # Test main page
        response = client.get('/')
        if response.status_code == 200:
            print("✓ Main page loads successfully")
        else:
            print(f"✗ Main page returned status code {response.status_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ Error testing backwards compatibility: {e}")
        return False

def main():
    """Run all tests"""
    print("YouTube API Integration Tests")
    print("=" * 40)
    
    tests = [
        test_youtube_api_key_handling,
        test_api_endpoints,
        test_backwards_compatibility
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All YouTube API integration tests passed!")
        return True
    else:
        print("❌ Some tests failed.")
        return False

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)