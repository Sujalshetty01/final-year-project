/**
 * Main Application Module
 * Initializes and manages the frontend application
 */

class MalwareClassificationApp {
    constructor() {
        this.uploader = null;
        this.isReady = false;
    }
    
    /**
     * Initialize application
     */
    async init() {
        try {
            console.log('Initializing Malware Classification App...');
            
            // Render main UI
            this.renderMainUI();
            
            // Check API availability
            await this.checkAPIAvailability();
            
            // Initialize components
            this.uploader = new UploaderComponent();
            this.uploader.render();
            
            this.isReady = true;
            console.log('Application initialized successfully');
            
        } catch (error) {
            console.error('Initialization error:', error);
            this.showInitializationError(error);
        }
    }
    
    /**
     * Render main UI structure
     */
    renderMainUI() {
        const app = document.getElementById('app');
        app.innerHTML = UI.createHeader() + UI.createContainer() + UI.createFooter();
    }
    
    /**
     * Check API availability
     */
    async checkAPIAvailability() {
        try {
            const isAvailable = await api.isAvailable();
            
            if (!isAvailable) {
                UI.showAlert(
                    'API is not ready. Some features may be unavailable.',
                    'warning'
                );
            }
        } catch (error) {
            console.warn('Could not verify API availability:', error);
            UI.showAlert(
                'Could not connect to backend. Please check if the API server is running.',
                'warning'
            );
        }
    }
    
    /**
     * Show initialization error
     */
    showInitializationError(error) {
        const app = document.getElementById('app');
        app.innerHTML = `
            <div class="header">
                <h1>🔍 Malware Classification System</h1>
            </div>
            <div class="container">
                <div class="card" style="background-color: #fadbd8; border-left: 4px solid var(--danger-color);">
                    <h2>❌ Initialization Error</h2>
                    <p>Failed to initialize the application:</p>
                    <pre style="background-color: #fdebd0; padding: 1rem; border-radius: 4px; overflow-x: auto;">
${error.message}
                    </pre>
                    <p style="margin-top: 1rem; color: var(--text-light);">
                        Please check the browser console for more details.
                    </p>
                </div>
            </div>
            <div class="footer">
                <p>&copy; 2025 Malware Classification System</p>
            </div>
        `;
    }
}

// Initialize application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        const app = new MalwareClassificationApp();
        app.init();
    });
} else {
    const app = new MalwareClassificationApp();
    app.init();
}
