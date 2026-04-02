/**
 * Results Display Component
 * Displays analysis results with visualizations
 */

class ResultsDisplayComponent {
    constructor(containerId = 'results-section') {
        this.containerId = containerId;
    }
    
    /**
     * Display analysis results
     */
    display(result) {
        // keep most recent result available for inline download fallback
        try { window._lastAnalysisResult = result; } catch (e) {}
        const container = document.getElementById(this.containerId);
        // If backend returns a simple shape {label, score, model}, render a compact view
        if (result && (result.label || result.binary_classification)) {
            const label = result.binary_classification || result.label;
            const confidence = result.binary_confidence != null ? result.binary_confidence : (result.score != null ? result.score : 0);
            const modelName = result.model || (result.gnn_prediction && result.gnn_prediction.model_name) || null;

            let html = `
                <h2>📊 Analysis Results</h2>
                <div style="margin-top: 1rem;">
                    ${UI.createClassificationBadge(label, confidence, modelName)}
                </div>
                <div style="margin-top:1rem;" class="card">
                    <p><strong>Label:</strong> ${label}</p>
                    <p><strong>Confidence:</strong> ${UI.formatConfidence(confidence)}</p>
                    ${modelName ? `<p><strong>Model:</strong> ${modelName}</p>` : ''}
                    <p style="color:var(--text-light); margin-top:0.5rem;">Results may be from the heuristic or the loaded model.</p>
                </div>
            `;

            // Add a Download button for compact results (fallback when no analysis_id available)
            html += `
                <div style="margin-top:1rem;" class="button-group">
                    <button class="btn btn-primary" onclick="downloadInline()">💾 Download Report</button>
                </div>
            `;

            // Performance metrics fallback when available
            if (result.inference_time_ms || result.feature_extraction_time_ms) {
                html += this._createPerformanceMetricsSection(result);
            }

            container.innerHTML = html;
            return;
        }

        // Existing rich result format
        let html = `
            <h2>📊 Analysis Results</h2>
            
            <div style="background-color: #f9f9f9; padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem;">
                <p><strong>Analysis ID:</strong> <code>${result.analysis_id || 'N/A'}</code></p>
                <p><strong>Analyzed At:</strong> ${result.timestamp ? UI.formatTimestamp(result.timestamp) : 'N/A'}</p>
                ${result.app_name ? `<p><strong>Application:</strong> ${result.app_name}</p>` : ''}
                <p><strong>Network Flows:</strong> ${result.num_flows_analyzed || (result.num_flows || 'N/A')}</p>
            </div>
        `;
        
        // Action Buttons
        html += `
            <div class="button-group" style="margin-top: 2rem;">
                <button class="btn btn-secondary" onclick="location.reload()">
                    🔄 New Analysis
                </button>
                <button class="btn btn-primary" onclick="downloadResults('${result.analysis_id}')">
                    💾 Download Report
                </button>
            </div>
        `;
        
        container.innerHTML = html;
    }
    
    /**
     * Create prediction card
     */
    _createPredictionCard(prediction) {
        const flagEmoji = prediction.predicted_label === 'benign' ? '✓' : '⚠';
        const bgColor = prediction.predicted_label === 'benign' ? '#d5f4e6' : '#fadbd8';
        
        return `
            <div style="background-color: ${bgColor}; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0;">
                <h3>${flagEmoji} ${prediction.model_name}</h3>
                <p><strong>Prediction:</strong> <span style="font-weight: bold; font-size: 1.1rem;">
                    ${prediction.predicted_label.toUpperCase()}
                </span></p>
                <p><strong>Confidence:</strong> ${UI.formatConfidence(prediction.confidence)}</p>
                
                <div style="margin-top: 1rem;">
                    <strong>Probabilities:</strong>
                    <table class="features-table">
                        <tr>
                            <td><strong>Benign</strong></td>
                            <td>${UI.formatConfidence(prediction.probabilities.benign)}</td>
                        </tr>
                        <tr>
                            <td><strong>Malware</strong></td>
                            <td>${UI.formatConfidence(prediction.probabilities.malware)}</td>
                        </tr>
                    </table>
                </div>
            </div>
        `;
    }
    
    /**
     * Create risk score section
     */
    _createRiskScoreSection(riskScore) {
        const riskLevel = riskScore > 0.7 ? 'HIGH' : riskScore > 0.4 ? 'MEDIUM' : 'LOW';
        const riskColor = riskScore > 0.7 ? 'var(--danger-color)' : riskScore > 0.4 ? 'var(--warning-color)' : 'var(--success-color)';
        
        return `
            <div style="background-color: #f9f9f9; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0; border-left: 4px solid ${riskColor};">
                <h3>⚠️ Risk Assessment</h3>
                <p><strong>Risk Level:</strong> <span style="color: ${riskColor}; font-weight: bold; font-size: 1.1rem;">${riskLevel}</span></p>
                ${UI.createConfidenceBar(riskScore, 'Overall Risk Score')}
            </div>
        `;
    }
    
    /**
     * Create graph features section
     */
    _createGraphFeaturesSection(features) {
        return `
            <div style="background-color: #f9f9f9; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0;">
                <h3>📈 Network Graph Features</h3>
                <table class="features-table">
                    <tr>
                        <th>Feature</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td>Number of Nodes</td>
                        <td>${features.num_nodes}</td>
                    </tr>
                    <tr>
                        <td>Number of Edges</td>
                        <td>${features.num_edges}</td>
                    </tr>
                    <tr>
                        <td>Average Node Degree</td>
                        <td>${features.avg_degree.toFixed(2)}</td>
                    </tr>
                    <tr>
                        <td>Graph Density</td>
                        <td>${features.density.toFixed(4)}</td>
                    </tr>
                    ${features.average_shortest_path !== null ? `
                    <tr>
                        <td>Average Shortest Path</td>
                        <td>${features.average_shortest_path.toFixed(2)}</td>
                    </tr>
                    ` : ''}
                    ${features.clustering_coefficient !== null ? `
                    <tr>
                        <td>Clustering Coefficient</td>
                        <td>${features.clustering_coefficient.toFixed(4)}</td>
                    </tr>
                    ` : ''}
                </table>
            </div>
        `;
    }
    
    /**
     * Create baseline predictions section
     */
    _createBaselinePredictionsSection(predictions) {
        let html = `
            <div style="background-color: #f9f9f9; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0;">
                <h3>🔍 Baseline Model Comparison</h3>
                <p style="color: var(--text-light); font-size: 0.9rem;">
                    Predictions from traditional machine learning models for cross-validation:
                </p>
                <div class="predictions-grid">
        `;
        
        predictions.forEach(pred => {
            const flagEmoji = pred.predicted_label === 'benign' ? '✓' : '⚠';
            html += `
                <div class="prediction-card">
                    <h4>${flagEmoji} ${pred.model_name}</h4>
                    <div class="prediction-item">
                        <strong>Prediction:</strong>
                        <span style="display: block; font-weight: bold; margin-top: 0.25rem;">
                            ${pred.predicted_label.toUpperCase()}
                        </span>
                    </div>
                    <div class="prediction-item">
                        <strong>Confidence:</strong>
                        <span style="display: block; margin-top: 0.25rem;">
                            ${UI.formatConfidence(pred.confidence)}
                        </span>
                    </div>
                    <div class="prediction-item" style="margin-top: 0.75rem;">
                        <strong>Benign:</strong> ${UI.formatConfidence(pred.probabilities.benign)}<br>
                        <strong>Malware:</strong> ${UI.formatConfidence(pred.probabilities.malware)}
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
        
        return html;
    }
    
    /**
     * Create performance metrics section
     */
    _createPerformanceMetricsSection(result) {
        return `
            <div style="background-color: #f9f9f9; padding: 1.5rem; border-radius: 8px; margin: 1.5rem 0;">
                <h3>⏱️ Performance Metrics</h3>
                <table class="features-table">
                    <tr>
                        <th>Metric</th>
                        <th>Time</th>
                    </tr>
                    <tr>
                        <td>Feature Extraction</td>
                        <td>${UI.formatTime(result.feature_extraction_time_ms)}</td>
                    </tr>
                    <tr>
                        <td>Model Inference</td>
                        <td>${UI.formatTime(result.inference_time_ms)}</td>
                    </tr>
                    <tr>
                        <td><strong>Total Analysis Time</strong></td>
                        <td><strong>${UI.formatTime(result.total_time_ms)}</strong></td>
                    </tr>
                </table>
            </div>
        `;
    }
}

/**
 * Download results as JSON report
 */
function downloadResults(analysisId) {
    api.getResult(analysisId).then(result => {
        const json = JSON.stringify(result, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `malware-classification-report-${analysisId}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    }).catch(error => {
        UI.showAlert(`Failed to download report: ${error.message}`, 'danger');
    });
}

/**
 * Download the most recently displayed result (fallback for compact responses)
 */
function downloadInline() {
    try {
        const result = window._lastAnalysisResult;
        if (!result) throw new Error('No result available to download');
        const json = JSON.stringify(result, null, 2);
        const blob = new Blob([json], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        const name = result.analysis_id ? result.analysis_id : 'inline';
        a.download = `malware-classification-report-${name}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    } catch (error) {
        UI.showAlert(`Failed to download report: ${error.message}`, 'danger');
    }
}
