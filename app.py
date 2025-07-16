from flask import Flask, render_template, request, jsonify
import json
import os
import re

app = Flask(__name__)

# File to store stream list
STREAMS_FILE = 'streams.json'

def load_streams():
    """Load streams from JSON file"""
    if os.path.exists(STREAMS_FILE):
        with open(STREAMS_FILE, 'r') as f:
            return json.load(f)
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
        save_streams(default_streams)
        return default_streams

def save_streams(streams):
    """Save streams to JSON file"""
    with open(STREAMS_FILE, 'w') as f:
        json.dump(streams, f, indent=2)

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
    streams = load_streams()
    return render_template('index.html', streams=streams)

@app.route('/api/streams', methods=['GET'])
def get_streams():
    """Get all streams"""
    streams = load_streams()
    return jsonify(streams)

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
    
    streams = load_streams()
    
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
    streams = load_streams()
    streams = [s for s in streams if s['id'] != stream_id]
    save_streams(streams)
    return jsonify({'success': True})

@app.route('/api/streams/<stream_id>', methods=['PUT'])
def update_stream(stream_id):
    """Update a stream"""
    data = request.json
    streams = load_streams()
    
    for stream in streams:
        if stream['id'] == stream_id:
            stream['title'] = data.get('title', stream['title'])
            break
    
    save_streams(streams)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
