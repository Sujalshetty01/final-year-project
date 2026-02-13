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
            <strong>${this._getAlertTitle(type)}:</strong> ${message}
            <button onclick="this.parentElement.style.display='none'" style="background:none;border:none;color:inherit;cursor:pointer;float:right;font-size:1.5rem;line-height:0.5;&times;</button>
        `;
        
        alertDiv.appendChild(alert);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            alert.style.display = 'none';
        }, 5000);
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
     * Create footer
     */
    static createFooter() {
        return `
            <div class="footer">
                <p>&copy; 2025 Malware Classification System | Final Year Project | BMS Institute of Technology</p>
            </div>
        `;
    }
    
    /**
     * Format confidence score as percentage
     */
    static formatConfidence(score) {
        const decimals = (window.CONFIG && window.CONFIG.CONFIDENCE_DECIMAL_PLACES) ? window.CONFIG.CONFIDENCE_DECIMAL_PLACES : 2;
        const percentage = (score * 100).toFixed(decimals);
        return `${percentage}%`;
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
        if (ms < 1000) return `${ms.toFixed(0)}ms`;
        return `${(ms / 1000).toFixed(2)}s`;
    }
    
    /**
     * Create classification badge
     */
    static createClassificationBadge(classification, confidence) {
        const badgeClass = classification === 'benign' ? 'benign' : 'malware';
        const badgeText = classification === 'benign' ? '✓ BENIGN' : '⚠ MALWARE';
        
        return `
            <div class="classification-badge ${badgeClass}">
                ${badgeText} (${UI.formatConfidence(confidence)})
            </div>
        `;
    }
    
    /**
     * Create confidence bar
     */
    static createConfidenceBar(confidence, label = '') {
        const barClass = confidence > 0.5 ? 'danger' : 'benign';
        const percentage = (confidence * 100).toFixed(1);
        
        return `
            <div class="confidence-score">
                ${label ? `<div class="score-label">${label}</div>` : ''}
                <div class="score-bar">
                    <div class="score-fill ${barClass}" style="width: ${percentage}%">
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
