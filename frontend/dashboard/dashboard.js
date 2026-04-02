// dashboard.js


// Accessibility: focus error on error div
function focusError() {
    const errDiv = document.getElementById('error');
    if (errDiv && errDiv.innerText) {
        errDiv.setAttribute('tabindex', '-1');
        errDiv.focus();
    }
}

document.getElementById('graph-form').addEventListener('submit', async function(e) {
    e.preventDefault();
    document.getElementById('loading').style.display = 'block';
    document.getElementById('result').innerHTML = '';
    document.getElementById('error').innerHTML = '';
    document.getElementById('prediction-summary').style.display = 'none';
    try {
        const features = JSON.parse(document.getElementById('node-features').value);
        const edges = JSON.parse(document.getElementById('edge-index').value);
        const node_count = features.length;
        const response = await fetch('http://localhost:8000/api/gnn/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ features, edges, node_count })
        });
        const data = await response.json();
        if (response.ok) {
            document.getElementById('prediction-summary').style.display = 'block';
            document.getElementById('predicted-class').textContent = 'Predicted Class: ' + (data.predicted_class || 'N/A');
            const confidence = typeof data.confidence === 'number' ? data.confidence : 0;
            document.getElementById('confidence-fill').style.width = (confidence * 100) + '%';
            document.getElementById('confidence-label').textContent = 'Confidence: ' + (confidence * 100).toFixed(1) + '%';
            document.getElementById('result').innerHTML = '<b>Full Response:</b><pre>' + JSON.stringify(data, null, 2) + '</pre>';
            document.getElementById('predictionChart').style.display = 'none';
        } else {
            document.getElementById('error').innerHTML = data.detail || 'Error occurred.';
            focusError();
        }
    } catch (err) {
        document.getElementById('error').innerHTML = 'Input error: ' + (err.message || 'Invalid input.');
        focusError();
    }
    document.getElementById('loading').style.display = 'none';
});

// Demo Data Button Logic
document.getElementById('demo-btn').addEventListener('click', async function() {
    // Example demo data for GNN input
    const demoFeatures = [[0.1,0.2],[0.3,0.4]];
    const demoEdges = [[0,1],[1,0]];
    document.getElementById('node-features').value = JSON.stringify(demoFeatures, null, 2);
    document.getElementById('edge-index').value = JSON.stringify(demoEdges, null, 2);
});
