Viva Notes — Why a GNN is appropriate for malware classification

- Intuition: network flows and program interactions are naturally a graph where nodes represent endpoints/processes and edges represent communications or control flows. Malware often exhibits structural patterns (e.g., unusual centralization, high outbound degree, or specific subgraph motifs) that are lost when flattening into a vector.

- Message Passing: GNNs perform iterative message passing, aggregating neighbor features into node representations. This lets the model learn how local connectivity and neighboring feature distributions influence a node or entire graph label — e.g., a small cluster of high-degree nodes connected to low-degree peers can indicate command-and-control behavior.

- Advantages over CNN/Flatten: CNNs assume grid-like local stationarity; flattening graph features removes permutation invariance and relational context. RandomForest on pooled statistics captures some signals but cannot learn compositional structural features (motifs, paths).

- Practical defense: use GNN with pooled readout for graph-level classification, include dropout and early stopping to prevent overfitting, and compare against strong baselines (RandomForest) with bootstrap AUC testing to demonstrate statistical significance.

- Reproducibility: use deterministic seeds, clear train/val/test splits with stratification, class-weighting or balanced sampling for imbalance, and report confidence intervals for key metrics.
