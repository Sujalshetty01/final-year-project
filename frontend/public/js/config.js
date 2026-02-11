/**
 * Configuration module
 * Handles API endpoints and environment-based settings
 */

const CONFIG = {
    // API Configuration
    API_BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
    API_TIMEOUT: 60000,
    
    // Feature Flags
    ENABLE_DETAILED_ANALYSIS: true,
    USE_ENSEMBLE: true,
    ENABLE_CACHING: true,
    
    // UI Configuration
    RESULTS_POLL_INTERVAL: 1000, // ms
    MAX_UPLOAD_SIZE_MB: 50,
    ALLOWED_FILE_TYPES: ['json', 'csv', 'txt'],
    
    // Display Configuration
    CONFIDENCE_DECIMAL_PLACES: 2,
    SHOW_BASELINE_MODELS: true,
    
    // Error messages
    MESSAGES: {
        UPLOAD_SUCCESS: 'File uploaded successfully',
        ANALYSIS_STARTED: 'Analysis started',
        ANALYSIS_COMPLETE: 'Analysis complete',
        ERROR_UPLOAD: 'Failed to upload file',
        ERROR_ANALYSIS: 'Analysis failed',
        ERROR_NETWORK: 'Network error',
        ERROR_INVALID_FILE: 'Invalid file format'
    }
};

// Override with environment variables if available
if (typeof window !== 'undefined' && window.location) {
    // Try to detect backend from current hostname
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        CONFIG.API_BASE_URL = 'http://localhost:8000/api/v1';
    }
}

// Export for both CommonJS and ES modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}
