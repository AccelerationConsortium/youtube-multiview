"""
AC Hardware Streams - Gradio Version for Hugging Face Spaces
A web application for watching multiple YouTube hardware streams simultaneously.
"""

import gradio as gr
import json
import os
import re
from typing import List, Dict, Optional, Tuple
from yt_utils import (
    check_api_key, extract_playlist_id, extract_video_id, 
    get_latest_video_from_playlist, get_playlist_info,
    export_streams_to_csv, import_streams_from_csv,
    set_api_key, get_api_key
)

# File to store stream list
STREAMS_FILE = 'streams.json'

def load_streams() -> List[Dict]:
    """Load streams from JSON file"""
    if os.path.exists(STREAMS_FILE):
        with open(STREAMS_FILE, 'r') as f:
            return json.load(f)
    else:
        # Sample streams (public playlists - not auto-selected)
        sample_streams = [
            {
                'id': 'NpjSPWitQ-Y',
                'title': 'Sample Live Stream',
                'url': 'https://www.youtube.com/live/NpjSPWitQ-Y',
                'type': 'video'
            },
            {
                'id': 'playlist_PL8uZlc2CEpelrYXunUzUOMJC17wEhiP6Q',
                'title': 'Sample Playlist',
                'url': 'https://www.youtube.com/playlist?list=PL8uZlc2CEpelrYXunUzUOMJC17wEhiP6Q',
                'type': 'playlist',
                'playlist_id': 'PL8uZlc2CEpelrYXunUzUOMJC17wEhiP6Q'
            }
        ]
        save_streams(sample_streams)
        return sample_streams

def save_streams(streams: List[Dict]) -> None:
    """Save streams to JSON file"""
    with open(STREAMS_FILE, 'w') as f:
        json.dump(streams, f, indent=2)

def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL - using yt_utils version"""
    from yt_utils import extract_video_id as yt_extract_video_id
    return yt_extract_video_id(url)

def get_youtube_embed_url(video_id: str) -> str:
    """Get YouTube embed URL for video ID"""
    # Use a more permissive embed URL that works better with live streams and private videos
    return f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1&modestbranding=1&rel=0&showinfo=0"

def create_video_grid_html(selected_streams: List[Dict], grid_size: int) -> str:
    """Create HTML for video grid layout"""
    if not selected_streams:
        return """
        <div style="text-align: center; padding: 50px; color: #666;">
            <h3>No streams selected</h3>
            <p>Select streams from the dropdown above to start watching.</p>
        </div>
        """
    
    # Determine grid dimensions
    if grid_size == 1:
        cols, rows = 1, 1
    elif grid_size <= 4:
        cols, rows = 2, 2
    else:
        cols, rows = 3, 3
    
    # CSS for responsive grid
    css = f"""
    <style>
    .video-grid {{
        display: grid;
        grid-template-columns: repeat({cols}, 1fr);
        grid-template-rows: repeat({rows}, 1fr);
        gap: 10px;
        width: 100%;
        height: 80vh;
        background: #000;
        padding: 10px;
        border-radius: 8px;
    }}
    .video-slot {{
        background: #1a1a1a;
        border-radius: 8px;
        overflow: hidden;
        position: relative;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .video-slot iframe {{
        width: 100%;
        height: 100%;
        border: none;
        border-radius: 8px;
    }}
    .video-title {{
        position: absolute;
        top: 10px;
        left: 10px;
        background: rgba(0,0,0,0.8);
        color: white;
        padding: 5px 10px;
        border-radius: 4px;
        font-size: 12px;
        z-index: 10;
    }}
    .empty-slot {{
        color: #666;
        text-align: center;
    }}
    </style>
    """
    
    # Create grid HTML
    html = css + '<div class="video-grid">'
    
    for i in range(grid_size):
        if i < len(selected_streams):
            stream = selected_streams[i]
            video_id = stream['id']
            
            # Skip error streams
            if video_id == 'error':
                html += f"""
                <div class="video-slot empty-slot">
                    <div style="color: #ff6666;">{stream['title']}</div>
                </div>
                """
                continue
            
            embed_url = get_youtube_embed_url(video_id)
            # Add fallback link for videos that can't embed
            fallback_url = f"https://www.youtube.com/watch?v={video_id}"
            
            html += f"""
            <div class="video-slot">
                <div class="video-title">{stream['title']}</div>
                <iframe 
                    src="{embed_url}" 
                    allowfullscreen
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    onerror="this.style.display='none'; this.nextElementSibling.style.display='block';"
                ></iframe>
                <div style="display: none; text-align: center; padding: 20px; color: #ccc;">
                    <p>Video cannot be embedded</p>
                    <a href="{fallback_url}" target="_blank" style="color: #ff6600; text-decoration: none;">
                        🔗 Open in YouTube
                    </a>
                </div>
            </div>
            """
        else:
            html += """
            <div class="video-slot empty-slot">
                <div>Empty Slot</div>
            </div>
            """
    
    html += '</div>'
    return html

def add_stream(url: str, title: str) -> Tuple[str, gr.Dropdown]:
    """Add a new stream (video or playlist)"""
    if not url or not title:
        return "Error: URL and title are required", gr.Dropdown()
    
    url = url.strip()
    title = title.strip()
    
    # Check if it's a playlist
    playlist_id = extract_playlist_id(url)
    if playlist_id:
        return add_playlist_stream(url, title, playlist_id)
    
    # Otherwise treat as video
    video_id = extract_video_id(url)
    if not video_id:
        return "Error: Invalid YouTube URL", gr.Dropdown()
    
    streams = load_streams()
    
    # Check if stream already exists
    for stream in streams:
        if stream['id'] == video_id:
            return "Error: Stream already exists", gr.Dropdown()
    
    new_stream = {
        'id': video_id,
        'title': title,
        'url': url,
        'type': 'video'
    }
    
    streams.append(new_stream)
    save_streams(streams)
    
    # Update dropdown choices
    choices = get_stream_choices()
    
    return f"✅ Added video stream: {title}", gr.Dropdown(choices=choices, value=[])

def add_playlist_stream(url: str, title: str, playlist_id: str) -> Tuple[str, gr.Dropdown]:
    """Add a playlist stream"""
    streams = load_streams()
    
    # Check if playlist already exists
    for stream in streams:
        if stream.get('playlist_id') == playlist_id:
            return "Error: Playlist already exists", gr.Dropdown()
    
    # Get playlist info if API key is available
    api_available, _ = check_api_key()
    if api_available and not title.strip():
        playlist_info = get_playlist_info(playlist_id)
        if playlist_info:
            title = playlist_info['title']
    
    new_stream = {
        'id': f'playlist_{playlist_id}',
        'title': title,
        'url': url,
        'type': 'playlist',
        'playlist_id': playlist_id
    }
    
    streams.append(new_stream)
    save_streams(streams)
    
    # Update dropdown choices
    choices = get_stream_choices()
    
    return f"✅ Added playlist: {title}", gr.Dropdown(choices=choices, value=[])

def bulk_add_streams(urls_text: str) -> Tuple[str, gr.Dropdown]:
    """Add multiple streams from text input (supports CSV format)"""
    if not urls_text.strip():
        return "Error: Please enter URLs", gr.Dropdown()
    
    lines = [line.strip() for line in urls_text.strip().split('\n') if line.strip()]
    added_count = 0
    errors = []
    
    for i, line in enumerate(lines):
        # Handle CSV format: url,title
        if ',' in line and not line.startswith('http'):
            parts = [p.strip().strip('"') for p in line.split(',', 1)]
            if len(parts) >= 2:
                url, title = parts[0], parts[1]
            else:
                url, title = parts[0], f"Stream {i+1}"
        # Handle pipe format: URL|Title
        elif '|' in line:
            url, title = line.split('|', 1)
            url, title = url.strip(), title.strip()
        else:
            # Just URL
            url = line.strip()
            title = f"Stream {i+1}"
        
        if not url:
            continue
        
        # Try to add stream
        try:
            result_text, _ = add_stream(url, title)
            if result_text.startswith("✅"):
                added_count += 1
            else:
                errors.append(f"Line {i+1}: {result_text}")
        except Exception as e:
            errors.append(f"Line {i+1}: {str(e)}")
    
    # Prepare result message
    result_parts = [f"✅ Added {added_count} streams"]
    if errors:
        result_parts.append(f"❌ {len(errors)} errors:")
        result_parts.extend(errors[:5])  # Show first 5 errors
        if len(errors) > 5:
            result_parts.append(f"... and {len(errors) - 5} more errors")
    
    # Update dropdown choices
    choices = get_stream_choices()
    
    return "\n".join(result_parts), gr.Dropdown(choices=choices, value=[])

def export_streams() -> str:
    """Export streams to CSV format"""
    streams = load_streams()
    return export_streams_to_csv(streams)

def import_streams_csv(csv_content: str) -> Tuple[str, gr.Dropdown]:
    """Import streams from CSV content"""
    if not csv_content.strip():
        return "Error: Please provide CSV content", gr.Dropdown()
    
    try:
        imported_streams = import_streams_from_csv(csv_content)
        if not imported_streams:
            return "Error: No valid streams found in CSV", gr.Dropdown()
        
        current_streams = load_streams()
        added_count = 0
        
        for stream in imported_streams:
            # Check for duplicates
            exists = False
            for existing in current_streams:
                if existing.get('id') == stream.get('id') or existing.get('url') == stream.get('url'):
                    exists = True
                    break
            
            if not exists:
                current_streams.append(stream)
                added_count += 1
        
        save_streams(current_streams)
        choices = get_stream_choices()
        
        return f"✅ Imported {added_count} new streams (skipped duplicates)", gr.Dropdown(choices=choices, value=[])
        
    except Exception as e:
        return f"Error: Failed to parse CSV - {str(e)}", gr.Dropdown()

def refresh_playlists() -> Tuple[str, gr.Dropdown]:
    """Refresh latest videos from all playlists"""
    api_available, api_message = check_api_key()
    if not api_available:
        return api_message, gr.Dropdown()
    
    streams = load_streams()
    updated_count = 0
    errors = []
    
    for stream in streams:
        if stream.get('type') == 'playlist' and stream.get('playlist_id'):
            try:
                latest_video = get_latest_video_from_playlist(stream['playlist_id'])
                if latest_video:
                    # Update the stream with latest video info
                    stream['latest_video'] = latest_video
                    stream['last_updated'] = latest_video['published_at']
                    updated_count += 1
                else:
                    errors.append(f"No videos found in playlist: {stream['title']}")
            except Exception as e:
                errors.append(f"Error updating {stream['title']}: {str(e)}")
    
    save_streams(streams)
    choices = get_stream_choices()
    
    result_parts = [f"✅ Updated {updated_count} playlists"]
    if errors:
        result_parts.append(f"❌ {len(errors)} errors:")
        result_parts.extend(errors[:3])
    
    return "\n".join(result_parts), gr.Dropdown(choices=choices, value=[])

def update_api_key(api_key: str) -> str:
    """Update the YouTube API key"""
    if not api_key.strip():
        return "Error: Please enter an API key"
    
    set_api_key(api_key)
    api_available, api_message = check_api_key()
    
    if api_available:
        return f"✅ API key updated successfully! {api_message}"
    else:
        return f"❌ API key validation failed: {api_message}"

def get_api_status() -> str:
    """Get current API key status"""
    api_available, api_message = check_api_key()
    return api_message

def remove_stream(selected_title: str) -> Tuple[str, gr.Dropdown]:
    """Remove a stream"""
    if not selected_title:
        return "Error: Please select a stream to remove", gr.Dropdown()
    
    streams = load_streams()
    original_count = len(streams)
    
    # Find and remove stream by title
    streams = [s for s in streams if s['title'] != selected_title]
    
    if len(streams) == original_count:
        return "Error: Stream not found", gr.Dropdown()
    
    save_streams(streams)
    
    # Update dropdown choices
    choices = [(f"{s['title']} ({s['url']})", s['title']) for s in streams]
    
    return f"✅ Removed stream: {selected_title}", gr.Dropdown(choices=choices, value=[])

def update_video_grid(selected_stream_titles: List[str], grid_size: int) -> str:
    """Update the video grid based on selected streams"""
    streams = load_streams()
    
    # Get selected streams and resolve playlists to latest videos
    selected_streams = []
    for title in selected_stream_titles:
        for stream in streams:
            if stream['title'] == title:
                if stream.get('type') == 'playlist':
                    # Get latest video from playlist
                    latest_video = stream.get('latest_video')
                    if latest_video:
                        # Use latest video data
                        resolved_stream = {
                            'id': latest_video['id'],
                            'title': f"📁 {stream['title']} (Latest: {latest_video['title'][:30]}...)",
                            'url': latest_video['url']
                        }
                    else:
                        # Try to fetch latest video if not cached
                        api_available, _ = check_api_key()
                        if api_available:
                            latest_video = get_latest_video_from_playlist(stream['playlist_id'])
                            if latest_video:
                                # Update cache
                                stream['latest_video'] = latest_video
                                save_streams(streams)
                                resolved_stream = {
                                    'id': latest_video['id'],
                                    'title': f"📁 {stream['title']} (Latest: {latest_video['title'][:30]}...)",
                                    'url': latest_video['url']
                                }
                            else:
                                resolved_stream = {
                                    'id': 'error',
                                    'title': f"📁 {stream['title']} (No videos found)",
                                    'url': stream['url']
                                }
                        else:
                            resolved_stream = {
                                'id': 'error',
                                'title': f"📁 {stream['title']} (API key required)",
                                'url': stream['url']
                            }
                    selected_streams.append(resolved_stream)
                else:
                    # Regular video stream
                    selected_streams.append({
                        'id': stream['id'],
                        'title': f"📺 {stream['title']}",
                        'url': stream['url']
                    })
                break
    
    return create_video_grid_html(selected_streams, grid_size)

def get_stream_choices() -> List[Tuple[str, str]]:
    """Get current stream choices for dropdown"""
    streams = load_streams()
    choices = []
    for s in streams:
        if s.get('type') == 'playlist':
            icon = "📁"
            latest_info = ""
            if s.get('latest_video'):
                latest_info = f" (Latest: {s['latest_video']['title'][:20]}...)"
            display_text = f"{icon} {s['title']}{latest_info}"
        else:
            icon = "📺"
            display_text = f"{icon} {s['title']}"
        choices.append((display_text, s['title']))
    return choices

# Initialize the interface
def create_interface():
    """Create the Gradio interface"""
    
    with gr.Blocks(
        title="AC Hardware Streams",
        theme="dark",
        css="""
        .gradio-container {
            max-width: 1200px !important;
        }
        .orange-accent {
            border-color: #ff6600 !important;
        }
        """
    ) as demo:
        
        gr.HTML("""
        <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%); border-radius: 10px; margin-bottom: 20px;">
            <h1 style="color: #ff6600; margin: 0; font-size: 2.5em;">
                🎥 AC Hardware Streams
            </h1>
            <p style="color: #ccc; margin: 10px 0 0 0;">Watch multiple YouTube hardware streams simultaneously</p>
        </div>
        """)
        
        with gr.Tab("🎬 Watch Streams"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📺 Select Streams")
                    stream_selector = gr.Dropdown(
                        choices=get_stream_choices(),
                        label="Available Streams",
                        multiselect=True,
                        value=[],
                        elem_classes=["orange-accent"]
                    )
                    
                    grid_size = gr.Radio(
                        choices=[1, 4, 9],
                        value=4,
                        label="Grid Size",
                        info="1=1x1, 4=2x2, 9=3x3"
                    )
                    
                    update_btn = gr.Button("🔄 Update Grid", variant="primary")
                
                with gr.Column(scale=3):
                    video_grid = gr.HTML(
                        value=create_video_grid_html([], 4),
                        label="Video Grid"
                    )
        
        with gr.Tab("⚙️ Manage Streams"):
            # API status and configuration
            gr.Markdown("## 🔑 YouTube API Configuration")
            gr.Markdown("""
            **YouTube API Key is required for playlist features.**
            
            Get your API key from [Google Cloud Console](https://console.cloud.google.com/) → APIs & Services → Credentials → Create API Key → Enable YouTube Data API v3
            """)
            
            api_status_display = gr.Textbox(
                label="API Status",
                value=get_api_status(),
                interactive=False
            )
            
            with gr.Row():
                api_key_input = gr.Textbox(
                    label="YouTube API Key",
                    placeholder="Enter your YouTube Data API v3 key...",
                    type="password",
                    elem_classes=["orange-accent"]
                )
                api_key_btn = gr.Button("🔑 Set API Key", variant="secondary")
            
            api_key_status = gr.Textbox(label="Update Status", interactive=False)
            
            gr.Markdown("---")  # Visual separator
            
            with gr.Tab("➕ Add Single Stream"):
                gr.Markdown("### Add Video or Playlist")
                
                with gr.Row():
                    url_input = gr.Textbox(
                        label="YouTube URL",
                        placeholder="https://www.youtube.com/watch?v=... or https://www.youtube.com/playlist?list=...",
                        elem_classes=["orange-accent"]
                    )
                    title_input = gr.Textbox(
                        label="Stream Title",
                        placeholder="Enter a descriptive title (auto-filled for playlists)",
                        elem_classes=["orange-accent"]
                    )
                
                add_btn = gr.Button("➕ Add Stream", variant="primary")
                add_status = gr.Textbox(label="Status", interactive=False)
            
            with gr.Tab("📋 Bulk Add / CSV Import"):
                gr.Markdown("""
                ### Add Multiple Streams
                **Supported formats:**
                - **Simple URLs:** One URL per line
                - **CSV Format:** `url,title` per line
                - **Pipe Format:** `URL|Title` per line
                """)
                
                bulk_input = gr.Textbox(
                    label="URLs or CSV Data",
                    placeholder="""https://www.youtube.com/watch?v=...
https://www.youtube.com/playlist?list=...,Lab Equipment
https://www.youtube.com/watch?v=...|Custom Title""",
                    lines=10,
                    elem_classes=["orange-accent"]
                )
                
                with gr.Row():
                    bulk_add_btn = gr.Button("📋 Add All Streams", variant="primary")
                    csv_import_btn = gr.Button("📥 Import as CSV", variant="secondary")
                
                bulk_status = gr.Textbox(label="Status", interactive=False, lines=5)
            
            with gr.Tab("📤 Export"):
                gr.Markdown("### Export Current Streams to CSV")
                export_btn = gr.Button("📤 Export to CSV", variant="secondary")
                export_output = gr.Textbox(
                    label="CSV Data",
                    placeholder="Click export to generate CSV...",
                    lines=8,
                    interactive=False
                )
            
            with gr.Tab("🔄 Playlist Management"):
                gr.Markdown("### Refresh Latest Videos")
                gr.Markdown("Update all playlists to show their latest videos (requires API key)")
                
                refresh_btn = gr.Button("� Refresh All Playlists", variant="primary")
                refresh_status = gr.Textbox(label="Refresh Status", interactive=False, lines=3)
            
            with gr.Tab("�🗑️ Remove Streams"):
                gr.Markdown("### Remove Stream")
                
                with gr.Row():
                    remove_selector = gr.Dropdown(
                        choices=get_stream_choices(),
                        label="Select Stream to Remove",
                        elem_classes=["orange-accent"]
                    )
                    remove_btn = gr.Button("🗑️ Remove Stream", variant="stop")
                
                remove_status = gr.Textbox(label="Status", interactive=False)
            
        with gr.Tab("ℹ️ About"):
            gr.Markdown("""
            ## About AC Hardware Streams
            
            This application allows you to watch multiple YouTube hardware streams simultaneously in a grid layout, perfect for monitoring different lab equipment or processes.
            
            ### Features:
            - **Multi-stream viewing**: Watch up to 9 streams at once
            - **Flexible layouts**: Choose 1x1, 2x2, or 3x3 grid
            - **Stream management**: Add and remove YouTube streams
            - **Auto-mute**: Videos are muted by default to prevent audio overlap
            
            ### Supported YouTube Formats:
            - `https://www.youtube.com/watch?v=VIDEO_ID`
            - `https://youtu.be/VIDEO_ID` 
            - `https://www.youtube.com/live/VIDEO_ID`
            - `https://www.youtube.com/embed/VIDEO_ID`
            
            ### Tips:
            - Live streams work best for real-time monitoring
            - Some videos may not embed due to creator restrictions
            - Click stream titles in management to see full URLs
            - Use fullscreen mode for better viewing experience
            
            ---
            
            **Acceleration Consortium** | [GitHub](https://github.com/AccelerationConsortium/youtube-multiview)
            """)
        
        # Event handlers
        
        # API key management
        api_key_btn.click(
            fn=update_api_key,
            inputs=[api_key_input],
            outputs=[api_key_status]
        ).then(
            fn=lambda: "",  # Clear API key input for security
            outputs=[api_key_input]
        ).then(
            fn=get_api_status,  # Update status display
            outputs=[api_status_display]
        )
        
        update_btn.click(
            fn=update_video_grid,
            inputs=[stream_selector, grid_size],
            outputs=[video_grid]
        )
        
        # Single add
        add_btn.click(
            fn=add_stream,
            inputs=[url_input, title_input],
            outputs=[add_status, stream_selector]
        ).then(
            fn=lambda: ("", ""),  # Clear inputs
            outputs=[url_input, title_input]
        ).then(
            fn=get_stream_choices,  # Update remove selector
            outputs=[remove_selector]
        )
        
        # Bulk add
        bulk_add_btn.click(
            fn=bulk_add_streams,
            inputs=[bulk_input],
            outputs=[bulk_status, stream_selector]
        ).then(
            fn=lambda: "",  # Clear input
            outputs=[bulk_input]
        ).then(
            fn=get_stream_choices,  # Update remove selector
            outputs=[remove_selector]
        )
        
        # CSV import (same function, different button)
        csv_import_btn.click(
            fn=import_streams_csv,
            inputs=[bulk_input],
            outputs=[bulk_status, stream_selector]
        ).then(
            fn=lambda: "",  # Clear input
            outputs=[bulk_input]
        ).then(
            fn=get_stream_choices,  # Update remove selector
            outputs=[remove_selector]
        )
        
        # Export
        export_btn.click(
            fn=export_streams,
            outputs=[export_output]
        )
        
        # Refresh playlists
        refresh_btn.click(
            fn=refresh_playlists,
            outputs=[refresh_status, stream_selector]
        ).then(
            fn=get_stream_choices,  # Update remove selector
            outputs=[remove_selector]
        )
        
        # Remove
        remove_btn.click(
            fn=remove_stream,
            inputs=[remove_selector],
            outputs=[remove_status, stream_selector]
        ).then(
            fn=get_stream_choices,  # Update remove selector
            outputs=[remove_selector]
        )
        
        # Auto-update grid when selection changes
        stream_selector.change(
            fn=update_video_grid,
            inputs=[stream_selector, grid_size],
            outputs=[video_grid]
        )
        
        grid_size.change(
            fn=update_video_grid,
            inputs=[stream_selector, grid_size],
            outputs=[video_grid]
        )
    
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
