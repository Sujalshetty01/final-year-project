/**
 * Configuration module
 * Handles API endpoints and environment-based settings
 */

// Minimal browser-safe configuration object
// This file is intentionally simple so it can be loaded directly in the browser
// without any bundler or Node.js-specific globals.
window.CONFIG = {
    API_BASE_URL: 'http://localhost:8000'
};

// Provide a legacy global alias for scripts that reference `CONFIG` directly
if (typeof window !== 'undefined') {
    try {
        if (typeof CONFIG === 'undefined') {
            /* eslint-disable no-var */
            var CONFIG = window.CONFIG;
            /* eslint-enable no-var */
        }
    } catch (e) {
        // ignore
    }
}
