---
title: AC Hardware Streams
emoji: 🎥
colorFrom: orange
colorTo: red
sdk: static
---

# AC Hardware Streams

A React-based application for viewing multiple YouTube streams simultaneously with live playlist support for real-time lab monitoring.

## Features

- 📺 **Multi-grid video viewing**: 1×1, 2×2, 3×3 layouts
- 🔴 **Live playlist integration**: Auto-updates to newest videos from playlists
- 🔧 **Stream management**: Add/remove static and live streams
- 🔍 **Video zoom**: Click any video for full-screen viewing
- 💾 **Gist sync**: Save/share configurations via GitHub Gist
- 📱 **Mobile responsive**: Works on all devices
- ⌨️ **Keyboard shortcuts**: M=manage, 1/2/3=grid sizes, ESC=close

## Usage

### Static Streams
1. Click "Manage" button
2. Go to "Static Streams" tab
3. Enter YouTube URL and title
4. Click "Add Stream"

### Live Playlist Streams
1. Click "Manage" button
2. Go to "Live Playlists" tab
3. Enter Channel ID and Device Name (e.g., "OT-2")
4. The app will find playlists containing that device name
5. Stream auto-updates every minute to show latest video

### Grid Management
- Choose grid size: 1×1, 2×2, or 3×3
- Click empty slots to add streams
- Use video controls to zoom or remove streams

## For Lab Monitoring

Perfect for monitoring multiple hardware setups:
- **OT-2 robots**: Auto-updates to latest protocol runs
- **Plate readers**: Live data collection streams  
- **Synthesis equipment**: Real-time experiment monitoring
- **Multiple labs**: Each device gets its own live stream

## Technical Details

- **Frontend**: React + Vite
- **Storage**: LocalStorage + GitHub Gist sync
- **APIs**: YouTube Data API v3 for live playlist features
- **Deployment**: Static files on Hugging Face Spaces

## Configuration

For live playlist features, you'll need a YouTube Data API key. The app works without it but only for static streams.

---

Built by the Acceleration Consortium for real-time lab monitoring 🚀
