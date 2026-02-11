"""
Network flow to graph conversion module
Converts raw network flow data into directed graphs with statistical features
"""

import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class FlowGraphBuilder:
    """
    Converts network flow data into directed graphs suitable for GNN input
    """
    
    def __init__(self, max_nodes: int = 1000, timeout: int = 30):
        self.max_nodes = max_nodes
        self.timeout = timeout
    
    def build_graph(self, flows: List[Dict[str, Any]]) -> Tuple[nx.DiGraph, Dict[str, Any]]:
        """
        Build a directed graph from network flows
        
        Args:
            flows: List of network flow dictionaries
            
        Returns:
            Tuple of (NetworkX graph, features dict)
        """
        try:
            G = nx.DiGraph()
            
            # Extract edges and aggregate statistics
            edge_stats = defaultdict(lambda: {
                'total_bytes': 0,
                'count': 0,
                'protocols': set(),
                'ports': set(),
                'durations': []
            })
            
            for flow in flows:
                src = flow.get('src_ip', 'unknown')
                dst = flow.get('dst_ip', 'unknown')
                
                # Add nodes
                G.add_node(src, node_type='ip')
                G.add_node(dst, node_type='ip')
                
                # Aggregate edge statistics
                edge_key = (src, dst)
                edge_stats[edge_key]['total_bytes'] += flow.get('bytes_sent', 0) + flow.get('bytes_received', 0)
                edge_stats[edge_key]['count'] += 1
                edge_stats[edge_key]['protocols'].add(flow.get('protocol', 'unknown'))
                edge_stats[edge_key]['ports'].add(flow.get('dst_port', 0))
                if 'duration' in flow:
                    edge_stats[edge_key]['durations'].append(flow['duration'])
            
            # Add edges with features
            for (src, dst), stats in edge_stats.items():
                edge_features = {
                    'bytes': stats['total_bytes'],
                    'flow_count': stats['count'],
                    'protocols': list(stats['protocols']),
                    'avg_duration': np.mean(stats['durations']) if stats['durations'] else 0.0,
                    'port': stats['ports'].pop() if stats['ports'] else 0
                }
                G.add_edge(src, dst, **edge_features)
            
            # Limit graph size if needed
            if len(G.nodes()) > self.max_nodes:
                logger.warning(f"Graph has {len(G.nodes())} nodes, limiting to {self.max_nodes}")
                # Keep nodes with highest degree
                degrees = dict(G.degree())
                top_nodes = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:self.max_nodes]
                G = G.subgraph([node for node, _ in top_nodes]).copy()
            
            # Extract graph features
            features = self._extract_graph_features(G, flows)
            
            return G, features
            
        except Exception as e:
            logger.error(f"Error building graph: {str(e)}")
            raise
    
    def _extract_graph_features(self, G: nx.DiGraph, flows: List[Dict]) -> Dict[str, Any]:
        """Extract statistical features from the graph"""
        try:
            features = {
                'num_nodes': len(G.nodes()),
                'num_edges': len(G.edges()),
                'avg_degree': np.mean(dict(G.degree()).values()) if G.nodes() else 0,
                'density': nx.density(G),
                'num_flows': len(flows),
                'graph_diameter': None,
                'average_clustering': None,
                'avg_bytes_per_edge': None,
                'protocol_distribution': {}
            }
            
            # Calculate diameter for connected components
            if nx.is_connected(G.to_undirected()):
                try:
                    features['graph_diameter'] = nx.diameter(G.to_undirected())
                except:
                    pass
            
            # Clustering coefficient
            try:
                features['average_clustering'] = nx.average_clustering(G.to_undirected())
            except:
                features['average_clustering'] = 0
            
            # Average bytes per edge
            if G.edges():
                bytes_list = [G[u][v].get('bytes', 0) for u, v in G.edges()]
                features['avg_bytes_per_edge'] = np.mean(bytes_list)
            
            # Protocol distribution
            protocol_counts = defaultdict(int)
            for flow in flows:
                protocol = flow.get('protocol', 'unknown')
                protocol_counts[protocol] += 1
            features['protocol_distribution'] = dict(protocol_counts)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting graph features: {str(e)}")
            return {
                'num_nodes': len(G.nodes()),
                'num_edges': len(G.edges()),
                'avg_degree': 0,
                'density': 0,
                'num_flows': len(flows)
            }
    
    def graph_to_tensor(self, G: nx.DiGraph) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Convert NetworkX graph to tensor representation for GNN
        
        Returns:
            Tuple of (node_features, edge_index, edge_features)
        """
        try:
            # Node mapping
            nodes = list(G.nodes())
            node_to_idx = {node: idx for idx, node in enumerate(nodes)}
            
            # Node features (degree, betweenness, etc.)
            degrees = dict(G.degree())
            node_features = np.array([
                [degrees.get(node, 0)]
                for node in nodes
            ], dtype=np.float32)
            
            # Edge index
            edges = [(node_to_idx[u], node_to_idx[v]) for u, v in G.edges()]
            edge_index = np.array(edges, dtype=np.int64).T if edges else np.zeros((2, 0), dtype=np.int64)
            
            # Edge features
            edge_features_list = []
            for u, v in G.edges():
                edge_data = G[u][v]
                features = [
                    edge_data.get('bytes', 0),
                    edge_data.get('flow_count', 0),
                    edge_data.get('avg_duration', 0),
                    len(edge_data.get('protocols', [])),
                ]
                edge_features_list.append(features)
            
            edge_features = np.array(
                edge_features_list, 
                dtype=np.float32
            ) if edge_features_list else np.zeros((len(edges), 4), dtype=np.float32)
            
            return node_features, edge_index, edge_features
            
        except Exception as e:
            logger.error(f"Error converting graph to tensors: {str(e)}")
            raise


class GraphFeatureExtractor:
    """Extract handcrafted features from graphs for baseline models"""
    
    @staticmethod
    def extract_features(G: nx.DiGraph, graph_features: Dict) -> Dict[str, float]:
        """
        Extract features suitable for traditional ML models
        
        Args:
            G: NetworkX directed graph
            graph_features: Features from FlowGraphBuilder
            
        Returns:
            Dictionary of features for ML models
        """
        features = {}
        
        # Structural features
        features['num_nodes'] = graph_features['num_nodes']
        features['num_edges'] = graph_features['num_edges']
        features['avg_degree'] = graph_features['avg_degree']
        features['density'] = graph_features['density']
        features['num_flows'] = graph_features['num_flows']
        
        # Safe diameter calculation
        features['diameter'] = graph_features.get('graph_diameter', 0) or 0
        
        # Clustering
        features['clustering_coef'] = graph_features.get('average_clustering', 0) or 0
        
        # Traffic features
        if G.edges():
            bytes_list = [G[u][v].get('bytes', 0) for u, v in G.edges()]
            flows_list = [G[u][v].get('flow_count', 0) for u, v in G.edges()]
            
            features['avg_bytes_per_edge'] = np.mean(bytes_list)
            features['std_bytes_per_edge'] = np.std(bytes_list)
            features['max_bytes_per_edge'] = np.max(bytes_list)
            
            features['avg_flow_count'] = np.mean(flows_list)
            features['std_flow_count'] = np.std(flows_list)
        else:
            features['avg_bytes_per_edge'] = 0
            features['std_bytes_per_edge'] = 0
            features['max_bytes_per_edge'] = 0
            features['avg_flow_count'] = 0
            features['std_flow_count'] = 0
        
        # Degree distribution
        if G.nodes():
            degrees = list(dict(G.degree()).values())
            features['max_degree'] = max(degrees)
            features['min_degree'] = min(degrees)
            features['std_degree'] = np.std(degrees)
        else:
            features['max_degree'] = 0
            features['min_degree'] = 0
            features['std_degree'] = 0
        
        # Protocol distribution
        protocol_dist = graph_features.get('protocol_distribution', {})
        for protocol in ['TCP', 'UDP', 'ICMP', 'HTTP', 'HTTPS', 'DNS']:
            features[f'protocol_{protocol.lower()}'] = protocol_dist.get(protocol, 0)
        
        return features
