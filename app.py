from flask import Flask, render_template, request, jsonify
import json
import os
import re
from datetime import datetime
from yt_utils import get_latest_streams_for_channels, YouTubeStreamFetcher

app = Flask(__name__)

# File to store stream list
STREAMS_FILE = 'streams.json'

# Configuration for monitored channels (can be set via environment variables)
MONITORED_CHANNELS = os.environ.get('MONITORED_CHANNELS', '').split(',')
MONITORED_CHANNELS = [ch.strip() for ch in MONITORED_CHANNELS if ch.strip()]

def load_streams():
    """Load streams from JSON file"""
    if os.path.exists(STREAMS_FILE):
        with open(STREAMS_FILE, 'r') as f:
            data = json.load(f)
            # Handle both old format (list) and new format (dict with metadata)
            if isinstance(data, list):
                return {
                    'streams': data,
                    'last_updated': None,
                    'auto_refresh_enabled': bool(MONITORED_CHANNELS)
                }
            return data
    else:
        # Default streams
        default_streams = [
            {
                'id': 'dQw4w9WgXcQ',
                'title': 'Sample Stream 1',
                'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                'id': 'jNQXAC9IVRw',
                'title': 'Sample Stream 2', 
                'url': 'https://www.youtube.com/watch?v=jNQXAC9IVRw'
            },
            {
                'id': '9bZkp7q19f0',
                'title': 'Sample Stream 3',
                'url': 'https://www.youtube.com/watch?v=9bZkp7q19f0'
            }
        ]
        data = {
            'streams': default_streams,
            'last_updated': None,
            'auto_refresh_enabled': bool(MONITORED_CHANNELS)
        }
        save_streams_data(data)
        return data

def save_streams(streams):
    """Save streams to JSON file (legacy function for backward compatibility)"""
    data = load_streams()
    data['streams'] = streams
    save_streams_data(data)

def save_streams_data(data):
    """Save complete streams data including metadata"""
    with open(STREAMS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def extract_video_id(url):
    """Extract YouTube video ID from URL"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r'(?:youtube\.com\/live\/)([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

@app.route('/')
def index():
    """Main page"""
    data = load_streams()
    return render_template('index.html', streams=data['streams'], 
                         last_updated=data.get('last_updated'),
                         auto_refresh_enabled=data.get('auto_refresh_enabled', False))

@app.route('/api/streams', methods=['GET'])
def get_streams():
    """Get all streams"""
    data = load_streams()
    return jsonify(data)

@app.route('/api/streams', methods=['POST'])
def add_stream():
    """Add a new stream"""
    data = request.json
    url = data.get('url', '').strip()
    title = data.get('title', '').strip()
    
    if not url or not title:
        return jsonify({'error': 'URL and title are required'}), 400
    
    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({'error': 'Invalid YouTube URL'}), 400
    
    streams_data = load_streams()
    streams = streams_data['streams']
    
    # Check if stream already exists
    for stream in streams:
        if stream['id'] == video_id:
            return jsonify({'error': 'Stream already exists'}), 400
    
    new_stream = {
        'id': video_id,
        'title': title,
        'url': url
    }
    
    streams.append(new_stream)
    save_streams(streams)
    
    return jsonify(new_stream), 201

@app.route('/api/streams/<stream_id>', methods=['DELETE'])
def delete_stream(stream_id):
    """Delete a stream"""
    streams_data = load_streams()
    streams = streams_data['streams']
    streams = [s for s in streams if s['id'] != stream_id]
    save_streams(streams)
    return jsonify({'success': True})

@app.route('/api/streams/<stream_id>', methods=['PUT'])
def update_stream(stream_id):
    """Update a stream"""
    data = request.json
    streams_data = load_streams()
    streams = streams_data['streams']
    
    for stream in streams:
        if stream['id'] == stream_id:
            stream['title'] = data.get('title', stream['title'])
            break
    
    save_streams(streams)
    return jsonify({'success': True})

@app.route('/api/refresh-streams', methods=['POST'])
def refresh_streams():
    """Refresh streams from monitored YouTube channels"""
    try:
        if not MONITORED_CHANNELS:
            return jsonify({'error': 'No monitored channels configured. Set MONITORED_CHANNELS environment variable.'}), 400
        
        # Check if YouTube API key is available
        api_key = os.environ.get('YOUTUBE_API_KEY')
        if not api_key:
            return jsonify({'error': 'YouTube API key not configured. Set YOUTUBE_API_KEY environment variable.'}), 400
        
        # Fetch latest streams from monitored channels
        latest_streams = get_latest_streams_for_channels(MONITORED_CHANNELS, api_key)
        
        if not latest_streams:
            return jsonify({'error': 'No live streams found in monitored channels'}), 404
        
        # Update streams data
        streams_data = load_streams()
        
        # Option 1: Replace all streams (comment out if you want to append instead)
        streams_data['streams'] = latest_streams
        
        # Option 2: Append new streams (uncomment if you want to keep existing streams)
        # existing_ids = {s['id'] for s in streams_data['streams']}
        # new_streams = [s for s in latest_streams if s['id'] not in existing_ids]
        # streams_data['streams'].extend(new_streams)
        
        streams_data['last_updated'] = datetime.now().isoformat()
        save_streams_data(streams_data)
        
        return jsonify({
            'success': True,
            'message': f'Refreshed with {len(latest_streams)} streams',
            'streams': latest_streams,
            'last_updated': streams_data['last_updated']
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to refresh streams: {str(e)}'}), 500

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get application status including YouTube API configuration"""
    status = {
        'youtube_api_configured': bool(os.environ.get('YOUTUBE_API_KEY')),
        'monitored_channels': MONITORED_CHANNELS,
        'monitored_channels_count': len(MONITORED_CHANNELS),
        'auto_refresh_available': bool(MONITORED_CHANNELS and os.environ.get('YOUTUBE_API_KEY'))
    }
    
    streams_data = load_streams()
    status.update({
        'streams_count': len(streams_data['streams']),
        'last_updated': streams_data.get('last_updated'),
        'auto_refresh_enabled': streams_data.get('auto_refresh_enabled', False)
    })
    
    return jsonify(status)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
