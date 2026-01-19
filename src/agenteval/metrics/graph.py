"""Graph-based structural analysis of agent interaction patterns.

Implements NetworkX-based graph construction, complexity metrics, and pattern detection.
"""

import json
from typing import Any

import networkx as nx


class InteractionGraph:
    """Model agent interactions as graph structures using NetworkX."""

    def __init__(self, directed: bool = True):
        """Initialize interaction graph.

        Args:
            directed: Whether to create directed graph (default True)
        """
        self._graph: nx.Graph | nx.DiGraph = nx.DiGraph() if directed else nx.Graph()

    def add_interaction(self, source: str, target: str, weight: float = 1.0, **attrs: Any) -> None:
        """Add agent interaction edge to graph.

        Args:
            source: Source agent ID
            target: Target agent ID
            weight: Edge weight (default 1.0)
            **attrs: Additional edge attributes
        """
        self._graph.add_edge(source, target, weight=weight, **attrs)

    @classmethod
    def from_interactions(
        cls, interactions: dict[tuple[str, str], dict[str, Any]]
    ) -> "InteractionGraph":
        """Create graph from interaction dictionary.

        Args:
            interactions: Dictionary mapping (source, target) tuples to edge attributes

        Returns:
            InteractionGraph instance
        """
        graph = cls()
        for (source, target), attrs in interactions.items():
            graph.add_interaction(source, target, **attrs)
        return graph

    def node_count(self) -> int:
        """Get number of nodes (agents) in graph.

        Returns:
            Number of nodes
        """
        return self._graph.number_of_nodes()

    def edge_count(self) -> int:
        """Get number of edges (interactions) in graph.

        Returns:
            Number of edges
        """
        return self._graph.number_of_edges()

    def get_networkx_graph(self) -> nx.Graph | nx.DiGraph:
        """Get underlying NetworkX graph.

        Returns:
            NetworkX graph object
        """
        return self._graph

    def is_directed(self) -> bool:
        """Check if graph is directed.

        Returns:
            True if directed, False otherwise
        """
        return isinstance(self._graph, nx.DiGraph)

    def export_json(self) -> str:
        """Export graph to JSON format.

        Returns:
            JSON string representation
        """
        data = nx.node_link_data(self._graph)
        return json.dumps(data, indent=2)

    def export_graphml(self) -> str:
        """Export graph to GraphML format.

        Returns:
            GraphML XML string
        """
        import io

        buffer = io.BytesIO()
        nx.write_graphml(self._graph, buffer)
        return buffer.getvalue().decode("utf-8")


class ComplexityAnalyzer:
    """Calculate complexity metrics from interaction graphs."""

    def calculate_density(self, graph: InteractionGraph) -> dict[str, float]:
        """Calculate graph density metric.

        Args:
            graph: InteractionGraph to analyze

        Returns:
            Dictionary with density metric
        """
        nx_graph = graph.get_networkx_graph()
        density = nx.density(nx_graph)
        return {"density": density}

    def calculate_degree_centrality(self, graph: InteractionGraph) -> dict[str, dict[str, float]]:
        """Calculate degree centrality for all nodes.

        Args:
            graph: InteractionGraph to analyze

        Returns:
            Dictionary with degree centrality per node
        """
        nx_graph = graph.get_networkx_graph()
        centrality = nx.degree_centrality(nx_graph)
        return {"degree_centrality": centrality}

    def calculate_betweenness_centrality(
        self, graph: InteractionGraph
    ) -> dict[str, dict[str, float]]:
        """Calculate betweenness centrality for all nodes.

        Args:
            graph: InteractionGraph to analyze

        Returns:
            Dictionary with betweenness centrality per node
        """
        nx_graph = graph.get_networkx_graph()
        centrality = nx.betweenness_centrality(nx_graph)
        return {"betweenness_centrality": centrality}

    def calculate_clustering_coefficient(self, graph: InteractionGraph) -> dict[str, float]:
        """Calculate clustering coefficient metric.

        Args:
            graph: InteractionGraph to analyze

        Returns:
            Dictionary with clustering coefficient
        """
        nx_graph = graph.get_networkx_graph()
        # For directed graphs, use the undirected version
        if isinstance(nx_graph, nx.DiGraph):
            nx_graph = nx_graph.to_undirected()
        coefficient = nx.average_clustering(nx_graph)
        return {"clustering_coefficient": coefficient}

    def calculate_all_metrics(self, graph: InteractionGraph) -> dict[str, Any]:
        """Calculate all complexity metrics at once.

        Args:
            graph: InteractionGraph to analyze

        Returns:
            Dictionary with all metrics
        """
        result: dict[str, Any] = {}
        result.update(self.calculate_density(graph))
        result.update(self.calculate_degree_centrality(graph))
        result.update(self.calculate_betweenness_centrality(graph))
        result.update(self.calculate_clustering_coefficient(graph))
        return result


class PatternDetector:
    """Identify coordination patterns between agents."""

    def identify_hub_agents(
        self, graph: InteractionGraph, threshold: int = 2
    ) -> dict[str, list[str]]:
        """Identify hub agents (highly connected nodes).

        Args:
            graph: InteractionGraph to analyze
            threshold: Minimum degree to be considered a hub

        Returns:
            Dictionary with list of hub agent IDs
        """
        nx_graph = graph.get_networkx_graph()
        degrees = dict(nx_graph.degree())
        hubs = [node for node, degree in degrees.items() if degree >= threshold]
        return {"hub_agents": hubs}

    def identify_communities(self, graph: InteractionGraph) -> dict[str, Any]:
        """Identify communities (clusters of agents).

        Args:
            graph: InteractionGraph to analyze

        Returns:
            Dictionary with community information
        """
        nx_graph = graph.get_networkx_graph()
        # Convert to undirected for community detection
        if isinstance(nx_graph, nx.DiGraph):
            nx_graph = nx_graph.to_undirected()

        # Use connected components as communities
        communities = list(nx.connected_components(nx_graph))
        return {
            "num_communities": len(communities),
            "communities": [list(c) for c in communities],
        }

    def detect_bottlenecks(self, graph: InteractionGraph) -> dict[str, list[str]]:
        """Detect bottleneck agents (critical for coordination).

        Args:
            graph: InteractionGraph to analyze

        Returns:
            Dictionary with list of bottleneck agent IDs
        """
        nx_graph = graph.get_networkx_graph()
        # Use betweenness centrality to identify bottlenecks
        centrality = nx.betweenness_centrality(nx_graph)

        # Consider nodes with above-average betweenness as bottlenecks
        if centrality:
            avg_centrality = sum(centrality.values()) / len(centrality)
            bottlenecks = [node for node, value in centrality.items() if value > avg_centrality]
        else:
            bottlenecks = []

        return {"bottleneck_agents": bottlenecks}
