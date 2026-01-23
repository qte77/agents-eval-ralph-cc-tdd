"""Graph-based complexity analysis for agent interactions."""

from typing import Any

import networkx as nx


class GraphAnalyzer:
    """Analyzes agent interactions as graph structures."""

    def __init__(self) -> None:
        """Initialize the graph analyzer."""
        self.graph: nx.DiGraph | None = None

    def build_graph(self, interactions: list[dict[str, Any]]) -> nx.DiGraph:
        """Build a NetworkX graph from interactions.

        Args:
            interactions: List of interaction dictionaries

        Returns:
            Directed graph representing interactions
        """
        self.graph = nx.DiGraph()
        for interaction in interactions:
            self.graph.add_edge(interaction.get("source"), interaction.get("target"))
        return self.graph

    def calculate_density(self, graph: Any | None = None) -> float:
        """Calculate graph density.

        Args:
            graph: Optional graph (uses self.graph if not provided)

        Returns:
            Graph density value
        """
        g = graph or self.graph
        if g is None:
            return 0.0
        return nx.density(g)

    def calculate_centrality(self, graph: Any | None = None) -> dict[str, float]:
        """Calculate centrality metrics.

        Args:
            graph: Optional graph (uses self.graph if not provided)

        Returns:
            Centrality scores for nodes
        """
        g = graph or self.graph
        if g is None:
            return {}
        return nx.degree_centrality(g)

    def calculate_clustering_coefficient(self, graph: Any | None = None) -> float:
        """Calculate clustering coefficient.

        Args:
            graph: Optional graph (uses self.graph if not provided)

        Returns:
            Average clustering coefficient
        """
        g = graph or self.graph
        if g is None:
            return 0.0
        return nx.average_clustering(g.to_undirected())

    def identify_coordination_patterns(self, graph: Any | None = None) -> list[tuple[str, str]]:
        """Identify coordination patterns in interactions.

        Args:
            graph: Optional graph (uses self.graph if not provided)

        Returns:
            List of coordinated node pairs
        """
        return []

    def calculate_all_metrics(self, graph: Any | None = None) -> dict[str, Any]:
        """Calculate all graph metrics.

        Args:
            graph: Optional graph (uses self.graph if not provided)

        Returns:
            Dictionary of all metrics
        """
        return {
            "density": self.calculate_density(graph),
            "centrality": self.calculate_centrality(graph),
            "clustering": self.calculate_clustering_coefficient(graph),
        }


def export_graph(graph: Any, output_path: Any | None = None, format: str = "json") -> Any:
    """Export a graph in specified format.

    Args:
        graph: NetworkX graph to export
        output_path: Optional output file path
        format: Export format (json, graphml, etc.)

    Returns:
        Exported graph data
    """
    if format == "json":
        return nx.node_link_data(graph)
    return {}
