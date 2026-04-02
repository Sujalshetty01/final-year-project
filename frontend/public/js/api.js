/**
 * API module
 * Handles all API communication with the backend
 */

class MalwareClassificationAPI {
        /**
         * Predict malware class using GNN model
         * POST /api/v1/predict
         */
        async predict(features, edges, nodeCount) {
            const payload = {
                features,
                edges,
                node_count: nodeCount
            };
            return this._post('/api/v1/predict', payload);
        }
    constructor(baseURL = (window.CONFIG && window.CONFIG.API_BASE_URL) || 'http://localhost:8000', fallbackBaseURLs = (window.CONFIG && window.CONFIG.API_FALLBACKS) || ['http://127.0.0.1:8000', 'http://localhost:8002']) {
        this.baseURL = baseURL;
        this.fallbackBaseURLs = Array.isArray(fallbackBaseURLs) ? fallbackBaseURLs : [fallbackBaseURLs];
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
            use_ensemble: options.useEnsemble !== false,
            force_heuristic: options.forceHeuristic === true
        };
        
        // backend route uses /api/v1 prefix
        return this._post('/api/v1/analyze', payload);
    }
    
    /**
     * Get analysis result by ID
     * GET /result/{id}
     */
    async getResult(analysisId) {
        // backend route is prefixed with /api/v1
        return this._get(`/api/v1/result/${analysisId}`);
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
     * Get model info and calibration
     */
    async modelInfo() {
        return this._get('/api/v1/model_info');
    }
    
    /**
     * Check if API is available
     */
    async isAvailable() {
        try {
            const response = await this.ready();
            return response.ready === true;
        } catch (error) {
            // If backend is still starting, treat as not ready but do not show warning
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
        const bases = [this.baseURL].concat(this.fallbackBaseURLs || []);
        let lastErr = null;

        for (const base of bases) {
            const url = `${base}${endpoint}`;

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
                lastErr = error;
                console.warn(`API request to ${base} failed, trying next fallback if any.`, error);
                continue;
            }
        }

        throw {
            message: (lastErr && lastErr.message) || 'All API endpoints failed',
            status: 'unreachable',
            type: 'api_error'
        };
    }
}

// Create backend API instance and expose a lightweight global `window.api`
let API_BASE = (window.CONFIG && window.CONFIG.API_BASE_URL) || 'http://localhost:8000';
let API_FALLBACKS = (window.CONFIG && window.CONFIG.API_FALLBACKS) || ['http://localhost:8002'];
const backendApi = new MalwareClassificationAPI(API_BASE, API_FALLBACKS);

window.api = {
        predict: async function(features, edges, nodeCount) {
            // Input validation
            if (!Array.isArray(features) || features.length === 0) {
                throw { message: 'Features array is required', type: 'input_error' };
            }
            if (!Array.isArray(edges)) {
                throw { message: 'Edges array is required', type: 'input_error' };
            }
            if (typeof nodeCount !== 'number' || nodeCount <= 0) {
                throw { message: 'Node count must be a positive number', type: 'input_error' };
            }
            return backendApi.predict(features, edges, nodeCount);
        },
    // analyze: async function(file) {
    //     // Legacy upload logic removed. Use the new uploadFile from src/services/api.js
    // },
    // Accept flows array to match frontend callers
    analyzeFlows: async function(flows, appName = null, options = {}) {
        // if user toggled force heuristic in header, pick it up from localStorage unless overridden
        if (typeof options.forceHeuristic === 'undefined') {
            const stored = window.localStorage.getItem('force_heuristic');
            options.forceHeuristic = stored === 'true';
        }
        return backendApi.analyzeFlows(flows, appName, options);
    },
    isAvailable: async function() {
        return backendApi.isAvailable();
    },
    modelInfo: async function() { return backendApi.modelInfo(); },
    ready: async function() {
        return backendApi.ready();
    },
    health: async function() {
        return backendApi.health();
    },
    getResult: async function(id) {
        return backendApi.getResult(id);
    }
    ,
    // Allow runtime update of API base and fallbacks
    setApiBase: function(url) {
        if (!url) return;
        API_BASE = url;
        backendApi.baseURL = url;
        // reflect for other code that may inspect window.CONFIG
        if (window.CONFIG) window.CONFIG.API_BASE_URL = url;
    },
    setApiFallbacks: function(arr) {
        const fallbacks = Array.isArray(arr) ? arr : (typeof arr === 'string' ? arr.split(',').map(s=>s.trim()).filter(Boolean) : []);
        API_FALLBACKS = fallbacks;
        backendApi.fallbackBaseURLs = fallbacks;
        if (window.CONFIG) window.CONFIG.API_FALLBACKS = fallbacks;
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
