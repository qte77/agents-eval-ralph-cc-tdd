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
            source = interaction.get("source")
            target = interaction.get("target")
            # Extract all attributes except source and target
            attrs = {k: v for k, v in interaction.items() if k not in ("source", "target")}
            self.graph.add_edge(source, target, **attrs)
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

    def identify_coordination_patterns(self, graph: Any | None = None) -> dict[str, list[Any]]:
        """Identify coordination patterns in interactions.

        Args:
            graph: Optional graph (uses self.graph if not provided)

        Returns:
            Dictionary with coordination pattern information
        """
        g = graph or self.graph
        if g is None:
            return {"bidirectional_pairs": [], "central_coordinators": []}

        # Find bidirectional pairs
        bidirectional_pairs = []
        for u, v in g.edges():
            if g.has_edge(v, u):
                pair = tuple(sorted([u, v]))
                if pair not in bidirectional_pairs:
                    bidirectional_pairs.append(pair)

        # Find central coordinators (nodes with high degree)
        centrality = nx.degree_centrality(g)
        if centrality:
            max_centrality = max(centrality.values())
            central_coordinators = [
                node for node, score in centrality.items() if score > 0 and score == max_centrality
            ]
        else:
            central_coordinators = []

        return {
            "bidirectional_pairs": bidirectional_pairs,
            "central_coordinators": central_coordinators,
        }

    def calculate_all_metrics(self, graph: Any | None = None) -> dict[str, Any]:
        """Calculate all graph metrics.

        Args:
            graph: Optional graph (uses self.graph if not provided)

        Returns:
            Dictionary of all metrics
        """
        g = graph or self.graph
        centrality = self.calculate_centrality(g)
        avg_centrality = sum(centrality.values()) / len(centrality) if centrality else 0.0

        return {
            "density": self.calculate_density(g),
            "avg_centrality": avg_centrality,
            "clustering_coefficient": self.calculate_clustering_coefficient(g),
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
        import json

        data = nx.node_link_data(graph)
        if output_path:
            with open(output_path, "w") as f:
                json.dump(data, f)
        return data
    elif format == "graphml":
        if output_path:
            nx.write_graphml(graph, output_path)
        return None
    else:
        raise ValueError(f"Unsupported format: {format}")
