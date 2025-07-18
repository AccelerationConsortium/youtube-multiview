class YouTubeMultiView {
    constructor() {
        this.streams = [];
        this.selectedStreams = [];
        this.currentGridSize = 1;
        this.maxGridSize = 9;
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadStreams();
        this.setupGrid();
    }

    bindEvents() {
        // Panel controls
        document.getElementById('manage-streams-btn').addEventListener('click', () => {
            this.toggleStreamPanel();
        });

        document.getElementById('close-panel-btn').addEventListener('click', () => {
            this.hideStreamPanel();
        });

        // Stream management
        document.getElementById('add-stream-btn').addEventListener('click', () => {
            this.addStream();
        });

        // Grid controls
        document.querySelectorAll('.grid-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const size = parseInt(e.target.dataset.size);
                this.changeGridSize(size);
            });
        });

        // Modal controls
        document.getElementById('close-selector-btn').addEventListener('click', () => {
            this.hideStreamSelector();
        });

        document.getElementById('close-zoom-btn').addEventListener('click', () => {
            this.hideZoomModal();
        });

        document.getElementById('confirm-selection-btn').addEventListener('click', () => {
            this.confirmStreamSelection();
        });

        document.getElementById('cancel-selection-btn').addEventListener('click', () => {
            this.hideStreamSelector();
        });

        // Fullscreen
        document.getElementById('fullscreen-btn').addEventListener('click', () => {
            this.toggleFullscreen();
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.hideAllModals();
            }
        });
    }

    async loadStreams() {
        try {
            const response = await fetch('/api/streams');
            this.streams = await response.json();
            this.updateStreamsList();
            this.updateStreamSelector();
        } catch (error) {
            console.error('Error loading streams:', error);
            this.showError('Failed to load streams');
        }
    }

    async addStream() {
        const urlInput = document.getElementById('stream-url');
        const titleInput = document.getElementById('stream-title');
        
        const url = urlInput.value.trim();
        const title = titleInput.value.trim();

        if (!url || !title) {
            this.showError('Please enter both URL and title');
            return;
        }

        try {
            const response = await fetch('/api/streams', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url, title }),
            });

            if (response.ok) {
                urlInput.value = '';
                titleInput.value = '';
                this.showSuccess('Stream added successfully');
                await this.loadStreams();
            } else {
                const error = await response.json();
                this.showError(error.error || 'Failed to add stream');
            }
        } catch (error) {
            console.error('Error adding stream:', error);
            this.showError('Failed to add stream');
        }
    }

    async deleteStream(streamId) {
        if (!confirm('Are you sure you want to delete this stream?')) {
            return;
        }

        try {
            const response = await fetch(`/api/streams/${streamId}`, {
                method: 'DELETE',
            });

            if (response.ok) {
                this.showSuccess('Stream deleted successfully');
                await this.loadStreams();
                // Remove from selected streams if present
                this.selectedStreams = this.selectedStreams.filter(s => s.id !== streamId);
                this.updateVideoGrid();
            } else {
                this.showError('Failed to delete stream');
            }
        } catch (error) {
            console.error('Error deleting stream:', error);
            this.showError('Failed to delete stream');
        }
    }

    updateStreamsList() {
        const container = document.getElementById('streams-container');
        container.innerHTML = '';

        this.streams.forEach(stream => {
            const streamElement = document.createElement('div');
            streamElement.className = 'stream-item';
            streamElement.innerHTML = `
                <div class="stream-info">
                    <div class="stream-title">${this.escapeHtml(stream.title)}</div>
                    <div class="stream-url">${this.escapeHtml(stream.url)}</div>
                </div>
                <div class="stream-actions">
                    <button class="btn btn-danger btn-small" onclick="app.deleteStream('${stream.id}')">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            container.appendChild(streamElement);
        });
    }

    updateStreamSelector() {
        const container = document.getElementById('stream-selection-grid');
        container.innerHTML = '';

        this.streams.forEach(stream => {
            const streamElement = document.createElement('div');
            streamElement.className = 'selectable-stream';
            streamElement.dataset.streamId = stream.id;
            streamElement.innerHTML = `
                <h4>${this.escapeHtml(stream.title)}</h4>
                <p>${this.escapeHtml(stream.url)}</p>
            `;

            streamElement.addEventListener('click', () => {
                this.toggleStreamSelection(stream);
            });

            container.appendChild(streamElement);
        });
    }

    toggleStreamSelection(stream) {
        const element = document.querySelector(`[data-stream-id="${stream.id}"]`);
        const isSelected = this.selectedStreams.some(s => s.id === stream.id);

        if (isSelected) {
            this.selectedStreams = this.selectedStreams.filter(s => s.id !== stream.id);
            element.classList.remove('selected');
        } else {
            if (this.selectedStreams.length < this.currentGridSize) {
                this.selectedStreams.push(stream);
                element.classList.add('selected');
            } else {
                this.showError(`You can only select ${this.currentGridSize} streams for this grid size`);
            }
        }
    }

    confirmStreamSelection() {
        this.hideStreamSelector();
        this.updateVideoGrid();
        this.updateSelectedCount();
    }

    changeGridSize(size) {
        this.currentGridSize = size;
        
        // Update active button
        document.querySelectorAll('.grid-btn').forEach(btn => btn.classList.remove('active'));
        document.querySelector(`[data-size="${size}"]`).classList.add('active');
        
        // Update grid class
        const grid = document.getElementById('video-grid');
        grid.className = `video-grid grid-${size}`;
        
        // Clear selections if too many
        if (this.selectedStreams.length > size) {
            this.selectedStreams = this.selectedStreams.slice(0, size);
        }
        
        this.updateVideoGrid();
        this.updateSelectedCount();
    }

    setupGrid() {
        this.updateVideoGrid();
        this.updateSelectedCount();
    }

    updateVideoGrid() {
        const grid = document.getElementById('video-grid');
        grid.innerHTML = '';

        for (let i = 0; i < this.currentGridSize; i++) {
            const slot = document.createElement('div');
            slot.className = 'video-slot';

            if (i < this.selectedStreams.length) {
                const stream = this.selectedStreams[i];
                slot.innerHTML = `
                    <div class="video-header">
                        <div class="video-title">${this.escapeHtml(stream.title)}</div>
                        <div class="video-actions">
                            <button class="btn btn-secondary btn-small" onclick="app.zoomVideo('${stream.id}', '${this.escapeHtml(stream.title)}')">
                                <i class="fas fa-expand"></i>
                            </button>
                            <button class="btn btn-danger btn-small" onclick="app.removeStreamFromGrid(${i})">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    <div class="video-container">
                        <iframe 
                            src="https://www.youtube.com/embed/${stream.id}?autoplay=1&mute=1&rel=0&modestbranding=1"
                            allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
                            allowfullscreen>
                        </iframe>
                    </div>
                `;
            } else {
                slot.classList.add('empty');
                slot.innerHTML = `
                    <div>
                        <i class="fas fa-plus-circle" style="font-size: 2rem; margin-bottom: 0.5rem;"></i>
                        <div>Click to add stream</div>
                    </div>
                `;
                slot.addEventListener('click', () => {
                    this.showStreamSelector();
                });
            }

            grid.appendChild(slot);
        }
    }

    removeStreamFromGrid(index) {
        this.selectedStreams.splice(index, 1);
        this.updateVideoGrid();
        this.updateSelectedCount();
    }

    zoomVideo(streamId, title) {
        const modal = document.getElementById('zoom-modal');
        const titleElement = document.getElementById('zoomed-title');
        const container = document.getElementById('zoomed-video-container');

        titleElement.textContent = title;
        container.innerHTML = `
            <iframe 
                src="https://www.youtube.com/embed/${streamId}?autoplay=1&rel=0&modestbranding=1"
                allow="autoplay; encrypted-media; picture-in-picture; fullscreen"
                allowfullscreen>
            </iframe>
        `;

        this.showZoomModal();
    }

    updateSelectedCount() {
        document.getElementById('selected-count').textContent = this.selectedStreams.length;
    }

    // UI Controls
    toggleStreamPanel() {
        const panel = document.getElementById('stream-panel');
        panel.classList.toggle('hidden');
    }

    hideStreamPanel() {
        document.getElementById('stream-panel').classList.add('hidden');
    }

    showStreamSelector() {
        this.updateStreamSelector();
        document.getElementById('stream-selector').classList.remove('hidden');
    }

    hideStreamSelector() {
        document.getElementById('stream-selector').classList.add('hidden');
    }

    showZoomModal() {
        document.getElementById('zoom-modal').classList.remove('hidden');
    }

    hideZoomModal() {
        document.getElementById('zoom-modal').classList.add('hidden');
    }

    hideAllModals() {
        this.hideStreamSelector();
        this.hideZoomModal();
    }

    toggleFullscreen() {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen();
        } else {
            document.exitFullscreen();
        }
    }

    // Utility functions
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type) {
        // Remove existing notifications
        const existing = document.querySelector('.notification');
        if (existing) {
            existing.remove();
        }

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            padding: 1rem 1.5rem;
            border-radius: 4px;
            color: white;
            font-weight: 500;
            z-index: 1001;
            animation: slideIn 0.3s ease;
            background: ${type === 'error' ? '#dc3545' : '#ff6600'};
            border: 1px solid ${type === 'error' ? '#dc3545' : '#ff6600'};
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Initialize the app
const app = new YouTubeMultiView();
