"""
AC Hardware Streams - Gradio Version for Hugging Face Spaces
A web application for watching multiple YouTube hardware streams simultaneously.
"""

import gradio as gr
import json
import os
import re
from typing import List, Dict, Optional, Tuple

# File to store stream list
STREAMS_FILE = 'streams.json'

def load_streams() -> List[Dict]:
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

def save_streams(streams: List[Dict]) -> None:
    """Save streams to JSON file"""
    with open(STREAMS_FILE, 'w') as f:
        json.dump(streams, f, indent=2)

def extract_video_id(url: str) -> Optional[str]:
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

def get_youtube_embed_url(video_id: str) -> str:
    """Get YouTube embed URL for video ID"""
    return f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=1&loop=1&playlist={video_id}"

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
            embed_url = get_youtube_embed_url(stream['id'])
            html += f"""
            <div class="video-slot">
                <div class="video-title">{stream['title']}</div>
                <iframe src="{embed_url}" allowfullscreen></iframe>
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
    """Add a new stream"""
    if not url or not title:
        return "Error: URL and title are required", gr.Dropdown()
    
    url = url.strip()
    title = title.strip()
    
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
        'url': url
    }
    
    streams.append(new_stream)
    save_streams(streams)
    
    # Update dropdown choices
    choices = [(f"{s['title']} ({s['url']})", s['title']) for s in streams]
    
    return f"✅ Added stream: {title}", gr.Dropdown(choices=choices, value=[])

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
    
    # Get selected streams
    selected_streams = []
    for title in selected_stream_titles:
        for stream in streams:
            if stream['title'] == title:
                selected_streams.append(stream)
                break
    
    return create_video_grid_html(selected_streams, grid_size)

def get_stream_choices() -> List[Tuple[str, str]]:
    """Get current stream choices for dropdown"""
    streams = load_streams()
    return [(f"{s['title']} ({s['url']})", s['title']) for s in streams]

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
            gr.Markdown("### ➕ Add New Stream")
            
            with gr.Row():
                url_input = gr.Textbox(
                    label="YouTube URL",
                    placeholder="https://www.youtube.com/watch?v=...",
                    elem_classes=["orange-accent"]
                )
                title_input = gr.Textbox(
                    label="Stream Title",
                    placeholder="Enter a descriptive title",
                    elem_classes=["orange-accent"]
                )
            
            add_btn = gr.Button("➕ Add Stream", variant="primary")
            add_status = gr.Textbox(label="Status", interactive=False)
            
            gr.Markdown("### 🗑️ Remove Stream")
            
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
        update_btn.click(
            fn=update_video_grid,
            inputs=[stream_selector, grid_size],
            outputs=[video_grid]
        )
        
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