class StaticYouTubeMultiView {
    constructor() {
        // Predefined streams - you can modify these
        this.streams = [
            {
                id: 'dQw4w9WgXcQ',
                title: 'Hardware Stream 1',
                url: 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
            },
            {
                id: 'jNQXAC9IVRw',
                title: 'Hardware Stream 2', 
                url: 'https://www.youtube.com/watch?v=jNQXAC9IVRw'
            },
            {
                id: '9bZkp7q19f0',
                title: 'Hardware Stream 3',
                url: 'https://www.youtube.com/watch?v=9bZkp7q19f0'
            },
            {
                id: 'L_jWHffIx5E',
                title: 'Hardware Stream 4',
                url: 'https://www.youtube.com/watch?v=L_jWHffIx5E'
            },
            {
                id: 'kJQP7kiw5Fk',
                title: 'Hardware Stream 5',
                url: 'https://www.youtube.com/watch?v=kJQP7kiw5Fk'
            },
            {
                id: 'kXYiU_JCYtU',
                title: 'Hardware Stream 6',
                url: 'https://www.youtube.com/watch?v=kXYiU_JCYtU'
            },
            {
                id: 'RjrEQaG5jPM',
                title: 'Hardware Stream 7',
                url: 'https://www.youtube.com/watch?v=RjrEQaG5jPM'
            },
            {
                id: 'hiI3zAz7b3k',
                title: 'Hardware Stream 8',
                url: 'https://www.youtube.com/watch?v=hiI3zAz7b3k'
            },
            {
                id: 'rub3n2TLt6Q',
                title: 'Hardware Stream 9',
                url: 'https://www.youtube.com/watch?v=rub3n2TLt6Q'
            }
        ];
        
        this.currentGridSize = 1;
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateVideoGrid();
    }

    bindEvents() {
        // Grid controls
        document.querySelectorAll('.grid-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const size = parseInt(e.target.dataset.size);
                this.changeGridSize(size);
            });
        });

        // Modal controls
        document.getElementById('close-zoom-btn').addEventListener('click', () => {
            this.hideZoomModal();
        });

        // Fullscreen
        document.getElementById('fullscreen-btn').addEventListener('click', () => {
            this.toggleFullscreen();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideZoomModal();
            }
        });
    }

    changeGridSize(size) {
        this.currentGridSize = size;
        
        // Update active button
        document.querySelectorAll('.grid-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-size="${size}"]`).classList.add('active');
        
        // Update grid class
        const grid = document.getElementById('video-grid');
        grid.className = `video-grid grid-${size}`;
        
        this.updateVideoGrid();
    }

    updateVideoGrid() {
        const grid = document.getElementById('video-grid');
        grid.innerHTML = '';

        for (let i = 0; i < this.currentGridSize; i++) {
            const slot = document.createElement('div');
            slot.className = 'video-slot';

            if (i < this.streams.length) {
                const stream = this.streams[i];
                slot.innerHTML = `
                    <div class="video-header">
                        <div class="video-title">${this.escapeHtml(stream.title)}</div>
                        <div class="video-actions">
                            <button class="btn btn-secondary btn-small" onclick="staticApp.zoomVideo('${stream.id}', '${this.escapeHtml(stream.title)}')">
                                <i class="fas fa-expand"></i>
                            </button>
                        </div>
                    </div>
                    <div class="video-container">
                        <iframe 
                            src="https://www.youtube.com/embed/${stream.id}?autoplay=1&mute=1&rel=0&modestbranding=1"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowfullscreen>
                        </iframe>
                    </div>
                `;
            } else {
                slot.classList.add('empty');
                slot.innerHTML = `
                    <div>
                        <i class="fas fa-video" style="font-size: 2rem; margin-bottom: 0.5rem;"></i>
                        <div>No more streams available</div>
                    </div>
                `;
            }

            grid.appendChild(slot);
        }
    }

    zoomVideo(streamId, title) {
        const modal = document.getElementById('zoom-modal');
        const titleElement = document.getElementById('zoomed-title');
        const container = document.getElementById('zoomed-video-container');

        titleElement.textContent = title;
        container.innerHTML = `
            <iframe 
                src="https://www.youtube.com/embed/${streamId}?autoplay=1&rel=0&modestbranding=1"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowfullscreen>
            </iframe>
        `;

        this.showZoomModal();
    }

    showZoomModal() {
        document.getElementById('zoom-modal').classList.remove('hidden');
    }

    hideZoomModal() {
        document.getElementById('zoom-modal').classList.add('hidden');
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the static app
const staticApp = new StaticYouTubeMultiView();
