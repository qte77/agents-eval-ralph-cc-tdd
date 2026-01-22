"""Graph-based complexity analysis for agent interaction patterns.

This module models agent interactions as directed graphs and computes
structural metrics like density, centrality, and clustering coefficients.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import networkx as nx


class GraphAnalyzer:
    """Analyzes agent interaction graphs for complexity metrics."""

    def build_graph(self, interactions: list[dict[str, Any]]) -> nx.DiGraph:
        """Build a directed graph from agent interactions.

        Args:
            interactions: List of interaction dicts with 'source' and 'target' keys

        Returns:
            NetworkX directed graph with interaction data
        """
        graph = nx.DiGraph()
        for interaction in interactions:
            source = interaction.get("source")
            target = interaction.get("target")
            if source and target:
                # Add edge with all interaction attributes
                graph.add_edge(source, target, **interaction)
        return graph

    def calculate_density(self, graph: nx.DiGraph) -> float:
        """Calculate graph density (edge connectivity).

        Args:
            graph: NetworkX directed graph

        Returns:
            Density value between 0 and 1
        """
        if graph.number_of_nodes() <= 1:
            return 0.0
        return nx.density(graph)

    def calculate_centrality(self, graph: nx.DiGraph) -> dict[str, float]:
        """Calculate node centrality metrics.

        Args:
            graph: NetworkX directed graph

        Returns:
            Dict mapping node names to centrality values
        """
        if graph.number_of_nodes() == 0:
            return {}
        return nx.betweenness_centrality(graph)

    def calculate_clustering_coefficient(self, graph: nx.DiGraph) -> float:
        """Calculate average clustering coefficient.

        Args:
            graph: NetworkX directed graph

        Returns:
            Clustering coefficient between 0 and 1
        """
        if graph.number_of_nodes() == 0:
            return 0.0
        # Convert to undirected for clustering coefficient calculation
        undirected = graph.to_undirected()
        return nx.average_clustering(undirected)

    def identify_coordination_patterns(self, graph: nx.DiGraph) -> dict[str, list[str]]:
        """Identify coordination patterns in the interaction graph.

        Args:
            graph: NetworkX directed graph

        Returns:
            Dict with 'bidirectional_pairs' and 'central_coordinators' lists
        """
        bidirectional_pairs = []
        central_coordinators = []

        # Find bidirectional pairs
        for node1 in graph.nodes():
            for node2 in graph.nodes():
                if node1 < node2 and graph.has_edge(node1, node2) and graph.has_edge(node2, node1):
                    bidirectional_pairs.append((node1, node2))

        # Find central coordinators (high in-degree and out-degree)
        if graph.number_of_nodes() > 0:
            centrality = self.calculate_centrality(graph)
            threshold = sum(centrality.values()) / len(centrality) if centrality else 0
            central_coordinators = [node for node, score in centrality.items() if score > threshold]

        return {
            "bidirectional_pairs": bidirectional_pairs,
            "central_coordinators": central_coordinators,
        }

    def calculate_all_metrics(self, graph: nx.DiGraph) -> dict[str, float]:
        """Calculate all complexity metrics at once.

        Args:
            graph: NetworkX directed graph

        Returns:
            Dict with 'density', 'avg_centrality', 'clustering_coefficient'
        """
        centrality = self.calculate_centrality(graph)
        avg_centrality = sum(centrality.values()) / len(centrality) if centrality else 0.0

        return {
            "density": self.calculate_density(graph),
            "avg_centrality": avg_centrality,
            "clustering_coefficient": self.calculate_clustering_coefficient(graph),
        }


def export_graph(graph: nx.DiGraph, output_path: Path, format: str = "json") -> None:
    """Export graph data in specified format.

    Args:
        graph: NetworkX directed graph
        output_path: Path to write output file
        format: Export format ('json' or 'graphml')

    Raises:
        ValueError: If format is not supported
    """
    if format == "json":
        # Convert to node-link format for JSON
        data = nx.node_link_data(graph)
        with open(output_path, "w") as f:
            json.dump(data, f)
    elif format == "graphml":
        nx.write_graphml(graph, output_path)
    else:
        raise ValueError(f"Unsupported format: {format}")
