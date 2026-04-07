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

            // Add loading spinner
            const app = document.getElementById('app');
            app.insertAdjacentHTML('beforeend', '<div id="loading" class="loading"><div class="spinner"></div><div>Loading...</div></div>');

            // Inject modals into DOM (calibration + settings)
            app.insertAdjacentHTML('beforeend', UI.createCalibrationModal());
            app.insertAdjacentHTML('beforeend', UI.createSettingsModal());

            // Show loading spinner
            const loadingEl = document.getElementById('loading');
            if (loadingEl && loadingEl.classList) loadingEl.classList.add('active');

            // Check API availability
            await this.checkAPIAvailability();

            // Fetch model info and render status in header
            try {
                const info = await api.modelInfo();
                UI.renderModelStatus(info);
            } catch (e) {
                UI.showAlert('Could not fetch model info: ' + e.message, 'warning');
            }

            // Hide loading spinner
            const loadingEl2 = document.getElementById('loading');
            if (loadingEl2 && loadingEl2.classList) loadingEl2.classList.remove('active');

            // Initialize header toolbar wiring (toggle + modal)
            try {
                const toggle = document.getElementById('force-heuristic-toggle');
                const calibBtn = document.getElementById('calib-open-btn');
                const modal = document.getElementById('calibration-modal');
                const close = document.getElementById('calib-close');
                const calibBody = document.getElementById('calib-body');

                // restore stored toggle value
                const stored = window.localStorage.getItem('force_heuristic');
                                if (toggle && stored === 'true') toggle.checked = true;

                                if (toggle) {
                                    toggle.addEventListener('change', () => {
                                            window.localStorage.setItem('force_heuristic', toggle.checked ? 'true' : 'false');
                                            UI.showAlert(`Force heuristic is now ${toggle.checked ? 'ON' : 'OFF'}`, 'info');
                                    });
                                }

                if (calibBtn && modal && calibBody) {
                  calibBtn.addEventListener('click', async () => {
                      try {
                          const info = await api.modelInfo();
                          calibBody.innerHTML = `<pre style="white-space:pre-wrap">${JSON.stringify(info, null, 2)}</pre>`;
                      } catch (e) {
                          calibBody.innerHTML = `<div style="color:var(--danger-color);">Failed to fetch calibration: ${e.message}</div>`;
                      }
                      modal.style.display = 'block';
                  });
                  close && close.addEventListener('click', () => { modal.style.display = 'none'; });
                  window.addEventListener('click', (ev) => { if (ev.target === modal) modal.style.display = 'none'; });
                }

                // Settings modal wiring
                const settingsBtn = document.getElementById('settings-open-btn');
                const settingsModal = document.getElementById('settings-modal');
                const settingsClose = document.getElementById('settings-close');
                const settingsSave = document.getElementById('settings-save-btn');
                const apiBaseInput = document.getElementById('api-base-input');
                const apiFallbacksInput = document.getElementById('api-fallbacks-input');

                // Populate inputs from localStorage if present
                try {
                    const storedBase = window.localStorage.getItem('api_base_url');
                    const storedFallbacks = window.localStorage.getItem('api_fallbacks');
                    if (storedBase) apiBaseInput.value = storedBase;
                    if (storedFallbacks) apiFallbacksInput.value = storedFallbacks;
                } catch (e) {}

                if (settingsBtn && settingsModal) settingsBtn.addEventListener('click', () => { settingsModal.style.display = 'block'; });
                if (settingsClose && settingsModal) settingsClose.addEventListener('click', () => { settingsModal.style.display = 'none'; });
                window.addEventListener('click', (ev) => { if (ev.target === settingsModal) settingsModal.style.display = 'none'; });

                if (settingsSave && apiBaseInput && apiFallbacksInput) settingsSave.addEventListener('click', () => {
                    const base = apiBaseInput.value.trim();
                    const fall = apiFallbacksInput.value.trim();
                    try {
                        if (base) {
                            window.localStorage.setItem('api_base_url', base);
                            api.setApiBase(base);
                        }
                        if (fall) {
                            window.localStorage.setItem('api_fallbacks', fall);
                            api.setApiFallbacks(fall);
                        }
                        UI.showAlert('Settings saved. API endpoints updated.', 'success');
                        settingsModal.style.display = 'none';
                    } catch (e) {
                        UI.showAlert('Failed to save settings: ' + e.message, 'danger');
                    }
                });
            } catch (e) {
                UI.showAlert('Header toolbar wiring failed: ' + e.message, 'danger');
            }

            // Initialize components
            this.uploader = new UploaderComponent();
            this.uploader.render();

            this.isReady = true;
            console.log('Application initialized successfully');
        } catch (error) {
            const loadingEl = document.getElementById('loading');
            if (loadingEl && loadingEl.classList) loadingEl.classList.remove('active');
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
                UI.showLoading('Waiting for backend to start...');
                // Do not show warning, just show loading state
            }
        } catch (error) {
            // Do not show warning if backend is still starting
            UI.showLoading('Waiting for backend to start...');
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
