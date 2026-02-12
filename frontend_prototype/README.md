Frontend Prototype: UX, Explainability, Report Download

This folder contains a minimal static prototype demonstrating the recommended
browser UX improvements. It is safe to host as static assets or integrate into
the existing frontend without modifying backend behavior.

Open `index.html` in the browser and point the JS `API_BASE` to your backend
(`http://localhost:8000` or the deployed API). The prototype will call
`/api/v1/analyze` (or a configured endpoint) and render:
- Confidence bars for benign vs malware
- Graph-level metrics (nodes, edges, density)
- Model comparison panel (GNN vs baseline)
- Textual explainability summary
- Download Report button (exports JSON and a simple PDF client-side)
