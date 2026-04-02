/**
 * Uploader Component
 * Handles file upload and flow data input
 */

class UploaderComponent {
    constructor(containerId = 'upload-section') {
        this.containerId = containerId;
        this.selectedFile = null;
        this.isDragging = false;
    }
    
    /**
     * Render upload interface
     */
    render() {
        const container = document.getElementById(this.containerId);
        container.innerHTML = `
            <h2>📤 Upload Network Flow Data</h2>
            
            <div class="upload-section">
                <!-- Drag and Drop Zone -->
                <div class="upload-box" id="uploadBox">
                    <div class="upload-icon">📁</div>
                    <p><strong>Drag and drop your file here</strong></p>
                    <p>or <strong id="browseLink">click to browse</strong> for a file</p>
                    <p style="font-size: 0.85rem; color: #95a5a6;">
                        Supported formats: JSON, CSV (max ${window.CONFIG && window.CONFIG.MAX_UPLOAD_SIZE_MB ? window.CONFIG.MAX_UPLOAD_SIZE_MB : 50}MB)
                    </p>
                </div>
                
                <!-- Or Manual Input -->
                <div>
                    <p style="text-align: center; color: var(--text-light); margin: 1rem 0;">— OR —</p>
                </div>
                
                <!-- Manual Flow Data Input -->
                <div class="form-group">
                    <label for="flowDataInput">Paste Network Flow Data (JSON Format):</label>
                    <textarea 
                        id="flowDataInput" 
                        placeholder='[{"src_ip": "192.168.1.1", "dst_ip": "8.8.8.8", "protocol": "UDP", "src_port": 12345, "dst_port": 53, "bytes_sent": 512, "bytes_received": 1024, "duration": 0.5}]'
                        style="font-family: monospace; font-size: 0.9rem;"></textarea>
                </div>
                
                <!-- Application Name -->
                <div class="form-group">
                    <label for="appName">Application Name (optional):</label>
                    <input 
                        type="text" 
                        id="appName" 
                        placeholder="e.g., com.example.app"
                    />
                </div>
                
                <!-- Options -->
                <div class="form-group">
                    <label>Analysis Options:</label>
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input 
                                type="checkbox" 
                                id="detailedAnalysis" 
                                checked
                            />
                            <label for="detailedAnalysis">Detailed Analysis</label>
                        </div>
                        <div class="checkbox-item">
                            <input 
                                type="checkbox" 
                                id="useEnsemble" 
                                checked
                            />
                            <label for="useEnsemble">Compare with Baseline Models</label>
                        </div>
                    </div>
                </div>
                
                <!-- Submit Button -->
                <div class="button-group">
                    <button class="btn btn-primary" id="analyzeButton">
                        🚀 Analyze
                    </button>
                    <button class="btn btn-secondary" id="clearButton">
                        🔄 Clear
                    </button>
                </div>
                
                <div id="fileInfo" style="margin-top: 1rem; padding: 1rem; background-color: #f0f8ff; border-radius: 4px; display: none;">
                    <p><strong>File Selected:</strong> <span id="fileName"></span></p>
                    <p><strong>Flows Detected:</strong> <span id="flowCount"></span></p>
                </div>
            </div>
        `;
        
        this.attachEventListeners();
    }
    
    /**
     * Attach event listeners
     */
    attachEventListeners() {
        const uploadBox = document.getElementById('uploadBox');
        const browseLink = document.getElementById('browseLink');
        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.id = 'fileInput';
        fileInput.style.display = 'none';
        fileInput.accept = '.json,.csv,.txt';
        document.body.appendChild(fileInput);
        
        // Browse button click
            // Attach listeners only if elements exist
            if (browseLink) browseLink.addEventListener('click', () => fileInput.click());
        
        // File input change
            if (fileInput) fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Drag and drop
            if (uploadBox) {
                uploadBox.addEventListener('dragover', (e) => this.handleDragOver(e));
                uploadBox.addEventListener('dragleave', (e) => this.handleDragLeave(e));
                uploadBox.addEventListener('drop', (e) => this.handleDrop(e));
            }
        
        // Analyze button
            const analyzeBtn = document.getElementById('analyzeButton');
            if (analyzeBtn) analyzeBtn.addEventListener('click', () => this.analyze());
        
        // Clear button
            const clearBtn = document.getElementById('clearButton');
            if (clearBtn) clearBtn.addEventListener('click', () => this.clear());
    }
    
    /**
     * Handle file selection
     */
    handleFileSelect(event) {
        const files = event.target.files;
        if (files.length > 0) {
            this.loadFile(files[0]);
        }
    }
    
    /**
     * Handle drag over
     */
    handleDragOver(event) {
        event.preventDefault();
        event.stopPropagation();
        document.getElementById('uploadBox').classList.add('dragover');
    }
    
    /**
     * Handle drag leave
     */
    handleDragLeave(event) {
        event.preventDefault();
        event.stopPropagation();
        document.getElementById('uploadBox').classList.remove('dragover');
    }
    
    /**
     * Handle drop
     */
    handleDrop(event) {
        event.preventDefault();
        event.stopPropagation();
        document.getElementById('uploadBox').classList.remove('dragover');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.loadFile(files[0]);
        }
    }
    
    /**
     * Load and parse file
     */
    loadFile(file) {
        const maxMb = (window.CONFIG && window.CONFIG.MAX_UPLOAD_SIZE_MB) ? window.CONFIG.MAX_UPLOAD_SIZE_MB : 50;
        if (file.size > maxMb * 1024 * 1024) {
            UI.showAlert(`File size exceeds ${maxMb}MB limit`, 'danger');
            return;
        }
        
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const content = event.target.result;
                let flows = [];
                
                if (file.name.endsWith('.json')) {
                    flows = JSON.parse(content);
                } else if (file.name.endsWith('.csv')) {
                    flows = this.parseCSV(content);
                } else {
                    throw new Error('Unsupported file format');
                }
                
                if (!Array.isArray(flows)) {
                    flows = [flows];
                }
                
                document.getElementById('flowDataInput').value = JSON.stringify(flows, null, 2);
                document.getElementById('fileName').textContent = file.name;
                document.getElementById('flowCount').textContent = flows.length;
                document.getElementById('fileInfo').style.display = 'block';
                
                this.selectedFile = file;
                UI.showAlert(`Loaded ${flows.length} network flows`, 'success');
                
            } catch (error) {
                UI.showAlert(`Error parsing file: ${error.message}`, 'danger');
            }
        };
        reader.readAsText(file);
    }
    
    /**
     * Parse CSV to JSON
     */
    parseCSV(content) {
        const lines = content.trim().split('\n');
        if (lines.length < 2) return [];
        
        const headers = lines[0].split(',').map(h => h.trim());
        const flows = [];
        
        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',').map(v => v.trim());
            const flow = {};
            
            headers.forEach((header, index) => {
                flow[header] = this.parseValue(values[index]);
            });
            
            flows.push(flow);
        }
        
        return flows;
    }
    
    /**
     * Parse CSV value to appropriate type
     */
    parseValue(value) {
        if (value === '' || value === 'null') return null;
        if (value === 'true') return true;
        if (value === 'false') return false;
        if (!isNaN(value) && value !== '') return Number(value);
        return value;
    }
    
    /**
     * Get flow data for analysis
     */
    getFlowData() {
        const dataInput = document.getElementById('flowDataInput').value.trim();
        if (!dataInput) {
            throw new Error('Please provide network flow data');
        }
        
        try {
            let flows = JSON.parse(dataInput);
            if (!Array.isArray(flows)) {
                flows = [flows];
            }
            // Normalize common field names so backend heuristic and model receive consistent keys
            const normalized = flows.map(f => {
                const obj = Object.assign({}, f);
                // bytes
                if (obj.bytes == null) {
                    const a = obj.bytes_sent || obj.bytes_sent_total || obj.bytes_sent_count || 0;
                    const b = obj.bytes_received || obj.bytes_recv || 0;
                    obj.bytes = (Number(a) || 0) + (Number(b) || 0);
                }
                // duration
                if (obj.duration == null) {
                    obj.duration = obj.flow_duration || obj.time_ms || 0;
                }
                // ports
                if (obj.sport == null && obj.src_port != null) obj.sport = obj.src_port;
                if (obj.dport == null && obj.dst_port != null) obj.dport = obj.dst_port;
                return obj;
            });
            return normalized;
        } catch (error) {
            throw new Error(`Invalid JSON format: ${error.message}`);
        }
    }
    
    /**
     * Perform analysis
     */
    async analyze() {
        try {
            UI.showLoading('Analyzing network flows...');
            UI.disableButton('analyzeButton');
            
            const flows = this.getFlowData();
            const appName = document.getElementById('appName').value || null;
            const detailedAnalysis = document.getElementById('detailedAnalysis').checked;
            const useEnsemble = document.getElementById('useEnsemble').checked;
            
            const result = await api.analyzeFlows(flows, appName, {
                detailedAnalysis,
                useEnsemble
            });
            
            UI.hideLoading();
            UI.showAlert('Analysis completed successfully', 'success');
            
            // Display results
            const resultsComponent = new ResultsDisplayComponent();
            resultsComponent.display(result);
            
            // Show results section
            document.getElementById('results-section').classList.add('active');
            
            // Scroll to results
            document.getElementById('results-section').scrollIntoView({ behavior: 'smooth' });
            
        } catch (error) {
            UI.hideLoading();
            UI.enableButton('analyzeButton');
            console.error('Analysis error:', error);
            UI.showAlert(`Analysis failed: ${error.message || 'Unknown error'}`, 'danger');
        }
    }
    
    /**
     * Clear form
     */
    clear() {
        document.getElementById('flowDataInput').value = '';
        document.getElementById('appName').value = '';
        document.getElementById('fileInfo').style.display = 'none';
        this.selectedFile = null;
        document.getElementById('results-section').classList.remove('active');
        UI.clearSection('results-section');
    }
}
