---
title: AC Hardware Streams
emoji: 🎥
colorFrom: orange
colorTo: red
sdk: gradio
sdk_version: 4.44.1
app_file: gradio_app.py
pinned: false
license: mit
short_description: Multi-stream YouTube viewer for hardware monitoring
---

# AC Hardware Streams

A web application for the Acceleration Consortium that allows you to stream multiple YouTube hardware streams simultaneously in a grid layout.

## Features

- **Multi-stream viewing**: Watch up to 9 YouTube streams at once
- **Flexible grid layouts**: Choose between 1x1, 2x2, or 3x3 grid layouts  
- **16:9 aspect ratio**: Proper YouTube video proportions
- **Stream management**: Add, remove, and organize hardware streams
- **Responsive design**: Works on desktop and mobile devices
- **Modern dark UI**: Black design with orange accents and AC branding

## Deployment Options

This application supports multiple deployment platforms:

### 🤗 Hugging Face Spaces (Gradio)
- **File**: `gradio_app.py`
- **Interface**: Modern Gradio-based UI with tabs
- **Features**: Full functionality with persistent stream management

### ▲ Vercel (Flask)
- **File**: `app.py` 
- **Interface**: Custom Flask web application
- **Features**: Advanced UI with modals and zoom functionality

## Usage

1. **Managing Streams**: Use the "Manage Streams" tab to add YouTube URLs and titles
2. **Watching Streams**: Select streams from the dropdown and choose your grid size
3. **Supported URLs**: YouTube watch, live, embed, and short URLs

## Technical Details

- **Backend**: Gradio (HF Spaces) / Flask (Vercel)
- **Data Storage**: JSON file (streams.json)
- **YouTube Integration**: YouTube embed API

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 80+

## Notes

- Videos are auto-muted by default to prevent audio overlap
- Some YouTube videos may not be embeddable due to creator restrictions
- Live streams work best for real-time viewing

---

**Acceleration Consortium** | [GitHub Repository](https://github.com/AccelerationConsortium/youtube-multiview)