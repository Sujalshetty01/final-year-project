/**
 * API module
 * Handles all API communication with the backend
 */

class MalwareClassificationAPI {
    constructor(baseURL = (window.CONFIG && window.CONFIG.API_BASE_URL) || 'http://localhost:8000') {
        this.baseURL = baseURL;
        this.timeout = (window.CONFIG && window.CONFIG.API_TIMEOUT) || 60000;
    }
    
    /**
     * Analyze network flows for malware
     * POST /analyze
     */
    async analyzeFlows(flows, appName = null, options = {}) {
        const payload = {
            network_flows: flows,
            app_name: appName,
            enable_detailed_analysis: options.detailedAnalysis !== false,
            use_ensemble: options.useEnsemble !== false
        };
        
        return this._post('/analyze', payload);
    }
    
    /**
     * Get analysis result by ID
     * GET /result/{id}
     */
    async getResult(analysisId) {
        return this._get(`/result/${analysisId}`);
    }
    
    /**
     * Health check
     * GET /health
     */
    async health() {
        return this._get('/health');
    }
    
    /**
     * Readiness check
     * GET /ready
     */
    async ready() {
        return this._get('/ready');
    }
    
    /**
     * Get API statistics
     * GET /stats
     */
    async stats() {
        return this._get('/stats');
    }
    
    /**
     * Check if API is available
     */
    async isAvailable() {
        try {
            const response = await this.ready();
            return response.ready === true;
        } catch (error) {
            console.error('API availability check failed:', error);
            return false;
        }
    }
    
    /**
     * Private method: GET request
     */
    async _get(endpoint) {
        return this._request('GET', endpoint, null);
    }
    
    /**
     * Private method: POST request
     */
    async _post(endpoint, data) {
        return this._request('POST', endpoint, data);
    }
    
    /**
     * Private method: Execute HTTP request
     */
    async _request(method, endpoint, body) {
        const url = `${this.baseURL}${endpoint}`;
        
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };
        
        if (body) {
            options.body = JSON.stringify(body);
        }
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            
            options.signal = controller.signal;
            
            const response = await fetch(url, options);
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            return data;
            
        } catch (error) {
            console.error(`API request failed: ${method} ${url}`, error);
            throw {
                message: error.message,
                status: error.status || 'unknown',
                type: 'api_error'
            };
        }
    }
}

// Create backend API instance and expose a lightweight global `window.api`
const API_BASE = (window.CONFIG && window.CONFIG.API_BASE_URL) || 'http://localhost:8000';
const backendApi = new MalwareClassificationAPI(API_BASE);

window.api = {
    analyze: async function(file) {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            body: formData
        });

        return response.json();
    },
    // Accept flows array to match frontend callers
    analyzeFlows: async function(flows, appName = null, options = {}) {
        return backendApi.analyzeFlows(flows, appName, options);
    },
    isAvailable: async function() {
        return backendApi.isAvailable();
    },
    ready: async function() {
        return backendApi.ready();
    },
    health: async function() {
        return backendApi.health();
    },
    getResult: async function(id) {
        return backendApi.getResult(id);
    }
};

// Legacy global alias for scripts that use `api` instead of `window.api`
try {
    if (typeof api === 'undefined') {
        /* eslint-disable no-var */
        var api = window.api;
        /* eslint-enable no-var */
    }
} catch (e) {
    // ignore
}
