import React, { useEffect, useRef } from 'react';
import { DataSet, Network } from 'vis-network/standalone';
import 'vis-network/styles/vis-network.css';
const NetworkGraph = ({ graph }) => {
  const containerRef = useRef();
  useEffect(() => {
    if (!graph || !containerRef.current) return;
    const nodes = new DataSet(
      graph.nodes.map((n) => ({
        id: n.id,
        label: n.label || n.id,
        color: n.suspicious ? '#e53935' : n.risk === 'High' ? '#ffb300' : '#90caf9',
        shape: n.suspicious ? 'diamond' : 'ellipse',
        font: { color: n.suspicious ? '#fff' : '#222', size: 18 },
      })),
    );
    const edges = new DataSet(
      (graph.edges || []).map((e) => ({
        from: e.source,
        to: e.target,
        color: e.suspicious ? '#e53935' : '#90caf9',
        width: e.suspicious ? 3 : 1.5,
        arrows: 'to',
      })),
    );
    const network = new Network(
      containerRef.current,
      { nodes, edges },
      {
        nodes: { borderWidth: 2, size: 24, shadow: true },
        edges: { smooth: true, shadow: true },
        physics: { enabled: true, barnesHut: { gravitationalConstant: -30000, springLength: 120 } },
        interaction: { hover: true, tooltipDelay: 100 },
        layout: { improvedLayout: true },
      },
    );
    return () => network.destroy();
  }, [graph]);
  return (
    <div
      style={{
        width: '100%',
        height: 360,
        margin: '24px 0',
        borderRadius: 8,
        background: '#23272f',
      }}
      ref={containerRef}
    />
  );
};
export default NetworkGraph;
