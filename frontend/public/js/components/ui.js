/**
 * UI Components Module
 * Core UI utilities and component builders
 */

class UI {
    /**
     * Show loading state
     */
    static showLoading(message = 'Processing...') {
        const loadingDiv = document.getElementById('loading');
        if (loadingDiv) {
            loadingDiv.innerHTML = `
                <div class="spinner"></div>
                <p>${message}</p>
            `;
            loadingDiv.classList.add('active');
        }
    }
    
    /**
     * Hide loading state
     */
    static hideLoading() {
        const loadingDiv = document.getElementById('loading');
        if (loadingDiv) {
            loadingDiv.classList.remove('active');
        }
    }
    
    /**
     * Show alert message
     */
    static showAlert(message, type = 'info') {
        const alertDiv = document.getElementById('alerts');
        if (!alertDiv) return;

        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            <div style="display:flex;align-items:center;justify-content:space-between;gap:1rem;">
                <div><strong>${this._getAlertTitle(type)}:</strong> ${message}</div>
                <button aria-label="close" class="alert-close">&times;</button>
            </div>
        `;

        // close handler
        alert.querySelector('.alert-close').addEventListener('click', () => {
            alert.style.display = 'none';
            alert.remove();
        });

        alertDiv.appendChild(alert);

        // Auto-remove after 6 seconds
        setTimeout(() => {
            if (alert && alert.parentElement) alert.remove();
        }, 6000);
    }
    
    static _getAlertTitle(type) {
        const titles = {
            'success': 'Success',
            'danger': 'Error',
            'info': 'Info',
            'warning': 'Warning'
        };
        return titles[type] || 'Alert';
    }
    
    /**
     * Create header element
     */
    static createHeader() {
        return `
            <div class="header">
                <h1>🔍 Malware Classification System</h1>
                <p>Deep Learning-based Malware Detection using Graph Neural Networks</p>
                <div id="model-status" style="margin-top:0.5rem;font-size:0.95rem;opacity:0.9;"></div>
            </div>
        `;
    }

    /**
     * Create a small header toolbar with a toggle to force heuristic and
     * a button to open the calibration modal.
     */
    static createHeaderToolbar() {
        return `
            <div id="header-toolbar" style="display:flex;gap:0.75rem;align-items:center;margin-top:0.5rem;">
                <label style="display:flex;align-items:center;gap:0.5rem;">
                    <input id="force-heuristic-toggle" type="checkbox" />
                    <span style="font-size:0.9rem;">Force heuristic</span>
                </label>
                <button id="calib-open-btn" class="btn btn-secondary" title="Show calibration details" style="font-size:0.85rem;">Calibration</button>
                <button id="settings-open-btn" class="btn btn-secondary" title="Open settings" style="font-size:0.85rem;">Settings</button>
            </div>
        `;
    }
    
    /**
     * Create main container
     */
    static createContainer() {
        return `
            <div class="container">
                <div id="alerts"></div>
                <div id="loading" class="loading"></div>
                <div id="upload-section" class="card"></div>
                <div id="results-section" class="card results-section"></div>
            </div>
        `;
    }

    /**
     * Create calibration modal container (hidden by default)
     */
    static createCalibrationModal() {
        return `
            <div id="calibration-modal" class="modal" style="display:none;">
                <div class="modal-content">
                    <span id="calib-close" class="modal-close">&times;</span>
                    <h3>Model Calibration Details</h3>
                    <div id="calib-body" style="margin-top:1rem;"></div>
                </div>
            </div>
        `;
    }

    /**
     * Settings modal to configure API endpoints at runtime
     */
    static createSettingsModal() {
        const apiBase = (window.CONFIG && window.CONFIG.API_BASE_URL) ? window.CONFIG.API_BASE_URL : '';
        const apiFallbacks = (window.CONFIG && window.CONFIG.API_FALLBACKS) ? (Array.isArray(window.CONFIG.API_FALLBACKS) ? window.CONFIG.API_FALLBACKS.join(', ') : window.CONFIG.API_FALLBACKS) : '';

        return `
            <div id="settings-modal" class="modal" style="display:none;">
                <div class="modal-content">
                    <span id="settings-close" class="modal-close">&times;</span>
                    <h3>Settings</h3>
                    <div style="margin-top:1rem;">
                        <label>API Base URL</label>
                        <input id="api-base-input" type="text" value="${apiBase}" style="width:100%;padding:0.5rem;margin-top:0.25rem;" />

                        <label style="margin-top:0.75rem;display:block;">Fallback API URLs (comma-separated)</label>
                        <input id="api-fallbacks-input" type="text" value="${apiFallbacks}" style="width:100%;padding:0.5rem;margin-top:0.25rem;" />

                        <div style="margin-top:1rem;text-align:right;">
                            <button id="settings-save-btn" class="btn btn-primary">Save</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Create footer
     */
    static createFooter() {
        return `
            <div class="footer">
                <p>&copy; 2025 Malware Classification System | Final Year Project</p>
            </div>
        `;
    }
    
    /**
     * Format confidence score as percentage
     */
    static formatConfidence(score) {
        const decimals = (window.CONFIG && window.CONFIG.CONFIDENCE_DECIMAL_PLACES) ? window.CONFIG.CONFIDENCE_DECIMAL_PLACES : 2;
        if (typeof score !== 'number' || !Number.isFinite(score)) return 'N/A';
        const percentage = Number((score * 100).toFixed(decimals));
        // avoid showing 100.00% which looks extreme; clamp display to 99.99% when score==1.0
        if (percentage >= 100) return `99.99%`;
        return `${percentage.toFixed(decimals)}%`;
    }

    /**
     * Render model status information into header
     */
    static renderModelStatus(info) {
        const el = document.getElementById('model-status');
        if (!el) return;
        if (!info) {
            el.innerHTML = `<span style="color:var(--warning-color);">Model: unknown</span>`;
            return;
        }
        const loaded = info.model_loaded ? '<strong style="color:var(--success-color);">Loaded</strong>' : '<strong style="color:var(--warning-color);">Not loaded</strong>';
        const path = info.model_path ? info.model_path.split('/').pop() : '—';
        const temp = (info.model_temp !== undefined && info.model_temp !== null) ? info.model_temp : '—';
        const bias = (info.model_bias !== undefined && info.model_bias !== null) ? info.model_bias : '—';
        let calib = '';
        if (info.calibration) {
            calib = ` (<em>calibrated</em>: T=${info.calibration.temperature}, b=${info.calibration.bias})`;
        }
        el.innerHTML = `Model: ${loaded} &middot; <span style="font-weight:600;">${path}</span>${calib} &nbsp; <span style="opacity:0.75; font-size:0.9rem;">(T=${temp}, b=${bias})</span>`;
    }
    
    /**
     * Format timestamp
     */
    static formatTimestamp(isoString) {
        const date = new Date(isoString);
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
    
    /**
     * Format milliseconds
     */
    static formatTime(ms) {
        if (typeof ms !== 'number' || !Number.isFinite(ms)) return 'N/A';
        if (ms < 1000) return `${ms.toFixed(0)}ms`;
        return `${(ms / 1000).toFixed(2)}s`;
    }
    
    /**
     * Create classification badge
     */
    static createClassificationBadge(classification, confidence, modelName = null) {
        const badgeClass = classification === 'benign' ? 'benign' : 'malware';
        const badgeText = classification === 'benign' ? '✓ BENIGN' : '⚠ MALWARE';

        return `
            <div class="classification-badge ${badgeClass}">
                <div style="display:flex;align-items:center;gap:0.75rem;justify-content:center;">
                    <span>${badgeText}</span>
                    <small style="opacity:0.85; font-weight:600;">${UI.formatConfidence(confidence)}</small>
                </div>
                ${modelName ? `<div style="font-size:0.75rem;opacity:0.7;margin-top:0.25rem;">Model: ${modelName}</div>` : ''}
            </div>
        `;
    }
    
    /**
     * Create confidence bar
     */
    static createConfidenceBar(confidence, label = '') {
        const barClass = (typeof confidence === 'number' && confidence > 0.5) ? 'danger' : 'benign';
        const percentage = (typeof confidence === 'number' && Number.isFinite(confidence)) ? (confidence * 100).toFixed(1) : '0.0';
        const width = (typeof confidence === 'number' && Number.isFinite(confidence)) ? `${percentage}%` : '0%';
        
        return `
            <div class="confidence-score">
                ${label ? `<div class="score-label">${label}</div>` : ''}
                <div class="score-bar">
                    <div class="score-fill ${barClass}" style="width: ${width}">
                        ${UI.formatConfidence(confidence)}
                    </div>
                </div>
            </div>
        `;
    }
    
    /**
     * Disable button
     */
    static disableButton(buttonId) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = true;
            button.opacity = '0.5';
        }
    }
    
    /**
     * Enable button
     */
    static enableButton(buttonId) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.disabled = false;
            button.opacity = '1';
        }
    }
    
    /**
     * Clear section
     */
    static clearSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            section.innerHTML = '';
        }
    }
}
