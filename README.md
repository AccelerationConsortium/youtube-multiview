# AC Hardware Streams

A web application for the Acceleration Consortium that allows you to stream multiple YouTube hardware streams simultaneously in a grid layout.

## Features

- **Multi-stream viewing**: Watch up to 9 YouTube streams at once
- **Flexible grid layouts**: Choose between 1x1, 2x2, or 3x3 grid layouts  
- **16:9 aspect ratio**: Proper YouTube video proportions
- **Stream management**: Add, remove, and organize hardware streams
- **Zoom functionality**: Click to zoom in on any stream for full-screen viewing
- **Responsive design**: Works on desktop and mobile devices
- **Modern dark UI**: Black design with orange accents and AC branding

## Installation

1. Make sure you have Python 3.7+ installed
2. Clone or download this repository
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Start the application:
   ```bash
   python app.py
   ```

2. Open your browser and navigate to `http://localhost:5000`

3. **Managing Streams**:
   - Click "Manage Streams" to open the stream management panel
   - Add new streams by entering a YouTube URL and title
   - Remove streams using the trash icon
   - Close the panel when done

4. **Watching Streams**:
   - Choose your preferred grid size (1x1, 2x2, or 3x3)
   - Click on empty slots to select streams to watch
   - Use the zoom button to view a stream in full-screen
   - Remove streams from slots using the X button

## Supported YouTube URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/live/VIDEO_ID`

## Deployment Options

This application supports multiple deployment platforms:

### 🤗 Hugging Face Spaces
- **Gradio Interface**: `gradio_app.py` 
- **URL**: [https://huggingface.co/spaces/AccelerationConsortium/youtube-multiview](https://huggingface.co/spaces/AccelerationConsortium/youtube-multiview)
- **Features**: Modern tabbed interface, embeddable, automatic deployment via GitHub Actions

### ▲ Vercel (Default)
- **Flask Interface**: `app.py`
- **Features**: Advanced UI with modals, zoom functionality, responsive design

## Technical Details

- **Backend**: Gradio (HF Spaces) / Flask (Vercel)
- **Frontend**: Gradio Components / Vanilla JavaScript, HTML5, CSS3
- **Data Storage**: JSON file (streams.json)
- **YouTube Integration**: YouTube embed API

## File Structure

```
youtube-multiview/
├── app.py                 # Flask backend (Vercel)
├── gradio_app.py          # Gradio backend (HF Spaces)  
├── requirements.txt       # Python dependencies (Flask)
├── requirements-gradio.txt # Python dependencies (Gradio)
├── streams.json          # Stream data storage (auto-generated)
├── Dockerfile            # Docker configuration for HF Spaces
├── README_HF.md          # HF Spaces README
├── .github/
│   └── workflows/
│       ├── deploy.yml    # Vercel deployment
│       └── deploy-hf.yml # HF Spaces deployment
├── static/
│   ├── css/
│   │   └── style.css     # Styling (Flask)
│   └── js/
│       └── app.js        # Frontend JavaScript (Flask)
└── templates/
    └── index.html        # Main HTML template (Flask)
```

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 80+

## Notes

- Some YouTube videos may not be embeddable due to restrictions set by the content creator
- Live streams work best for real-time viewing
- The application auto-mutes videos by default to prevent audio overlap

## Troubleshooting

**Issue**: Video not loading
- **Solution**: Check if the YouTube video allows embedding, try a different video

**Issue**: Audio overlap
- **Solution**: Videos are auto-muted by default, you can unmute individual videos as needed

**Issue**: Performance issues with many streams
- **Solution**: Reduce the number of simultaneous streams or close other browser tabs
