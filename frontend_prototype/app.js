// Prototype client-side UX for results, explainability and report download
const API_BASE = window.API_BASE || 'http://127.0.0.1:8000';

function setConfidence(benign, malware) {
  const container = document.getElementById('confidence-bars');
  container.innerHTML = '';
  const b = document.createElement('div'); b.className = 'bar benign';
  const bf = document.createElement('div'); bf.className = 'fill'; bf.style.width = (benign*100)+'%'; b.appendChild(bf);
  const m = document.createElement('div'); m.className = 'bar malware';
  const mf = document.createElement('div'); mf.className = 'fill'; mf.style.width = (malware*100)+'%'; m.appendChild(mf);
  container.appendChild(b); container.appendChild(m);
}

function setRisk(score) {
  const el = document.getElementById('risk');
  const v = document.getElementById('risk-val');
  v.textContent = (score*100).toFixed(1)+'%';
  el.className = score >= 0.75 ? 'risk-high' : score >= 0.4 ? 'risk-medium' : 'risk-low';
}

function setMetrics(metrics) {
  const ul = document.getElementById('graph-metrics'); ul.innerHTML = '';
  ['num_nodes','num_edges','density','avg_degree'].forEach(k=>{
    if(metrics[k]!==undefined){ const li=document.createElement('li'); li.textContent = `${k}: ${metrics[k]}`; ul.appendChild(li)}
  });
}

function setComparison(preds){
  const tbody = document.querySelector('#model-compare tbody'); tbody.innerHTML='';
  preds.forEach(p=>{
    const tr=document.createElement('tr');
    tr.innerHTML = `<td>${p.model}</td><td>${p.predicted_label}</td><td>${(p.confidence*100).toFixed(1)}%</td>`;
    tbody.appendChild(tr);
  });
}

function setExplain(summary, importances){
  document.getElementById('explain-text').textContent = summary || 'No explanation.';
  const ul = document.getElementById('feature-importances'); ul.innerHTML='';
  (importances || []).slice(0,6).forEach(it=>{ const li=document.createElement('li'); li.textContent = `${it.feature}: ${it.score.toFixed(3)}`; ul.appendChild(li) });
}

async function analyze() {
  // Call GNN endpoint
  try {
    // Example: features, edges, node_count
    const features = [[0.1,0.2],[0.3,0.4]]; // Replace with actual input
    const edges = [[0,1],[1,0]];
    const node_count = features.length;
    const res = await fetch(API_BASE + '/api/gnn/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ features, edges, node_count })
    });
    const j = await res.json();
    setConfidence(j.confidence || 0.5, 1-(j.confidence||0.5));
    setRisk(j.confidence || 0.5);
    setMetrics({num_nodes: node_count, num_edges: edges.length});
    setComparison([ {model:'GNN', predicted_label:j.predicted_class, confidence:j.confidence||0.5} ]);
    setExplain('Prediction explanation not available.', []);
    window.__last_analysis = j;
  } catch(e) {
    console.error(e);
    alert('Analysis failed. If backend not running, this prototype still demonstrates UI.');
  }
}

function downloadReport(){
  const data = window.__last_analysis || {note:'no analysis run'};
  const jsonStr = JSON.stringify(data, null, 2);
  const blob = new Blob([jsonStr], {type:'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a'); a.href=url; a.download='analysis_report.json'; a.click();
  URL.revokeObjectURL(url);
}

document.getElementById('analyze').addEventListener('click', analyze);
document.getElementById('download').addEventListener('click', downloadReport);
