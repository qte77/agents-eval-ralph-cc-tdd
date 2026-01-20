"""Graph-based complexity analysis metrics for agent evaluation.

Implements NetworkX-based graph analysis for agent interaction patterns
and coordination complexity metrics.
"""

import json
from io import BytesIO

import networkx as nx
from pydantic import BaseModel


class AgentInteraction(BaseModel):
    """Represents an interaction between agents."""

    from_agent: str
    to_agent: str
    interaction_type: str
    timestamp: float
    metadata: dict[str, str]


class GraphMetrics(BaseModel):
    """Graph-based complexity metrics for agent coordination."""

    density: float
    avg_degree_centrality: float
    avg_betweenness_centrality: float
    avg_clustering_coefficient: float
    num_nodes: int
    num_edges: int


class GraphAnalyzer:
    """Analyzer for building and analyzing agent interaction graphs."""

    def build_graph(self, interactions: list[AgentInteraction]) -> nx.DiGraph:
        """Build directed graph from agent interactions.

        Args:
            interactions: List of AgentInteraction objects

        Returns:
            NetworkX DiGraph representing agent interactions
        """
        graph = nx.DiGraph()

        for interaction in interactions:
            graph.add_edge(
                interaction.from_agent,
                interaction.to_agent,
                interaction_type=interaction.interaction_type,
                timestamp=interaction.timestamp,
            )

        return graph

    def calculate_density(self, graph: nx.DiGraph) -> float:
        """Calculate graph density.

        Args:
            graph: NetworkX DiGraph

        Returns:
            Density as float between 0.0 and 1.0
        """
        if len(graph.nodes) == 0:
            return 0.0
        return nx.density(graph)

    def calculate_degree_centrality(self, graph: nx.DiGraph) -> dict[str, float]:
        """Calculate degree centrality for all nodes.

        Args:
            graph: NetworkX DiGraph

        Returns:
            Dictionary mapping node to degree centrality
        """
        return dict(nx.degree_centrality(graph))

    def calculate_betweenness_centrality(self, graph: nx.DiGraph) -> dict[str, float]:
        """Calculate betweenness centrality for all nodes.

        Args:
            graph: NetworkX DiGraph

        Returns:
            Dictionary mapping node to betweenness centrality
        """
        return dict(nx.betweenness_centrality(graph))

    def _calculate_avg_centrality(self, centrality: dict[str, float]) -> float:
        """Calculate average centrality value from a centrality dictionary.

        Args:
            centrality: Dictionary mapping node to centrality value

        Returns:
            Average centrality as float
        """
        if not centrality:
            return 0.0
        return sum(centrality.values()) / len(centrality)

    def calculate_avg_degree_centrality(self, graph: nx.DiGraph) -> float:
        """Calculate average degree centrality across all nodes.

        Args:
            graph: NetworkX DiGraph

        Returns:
            Average degree centrality as float
        """
        return self._calculate_avg_centrality(self.calculate_degree_centrality(graph))

    def calculate_avg_betweenness_centrality(self, graph: nx.DiGraph) -> float:
        """Calculate average betweenness centrality across all nodes.

        Args:
            graph: NetworkX DiGraph

        Returns:
            Average betweenness centrality as float
        """
        return self._calculate_avg_centrality(self.calculate_betweenness_centrality(graph))

    def calculate_avg_clustering_coefficient(self, graph: nx.DiGraph) -> float:
        """Calculate average clustering coefficient.

        Args:
            graph: NetworkX DiGraph

        Returns:
            Average clustering coefficient as float
        """
        if len(graph.nodes) == 0:
            return 0.0
        # Convert to undirected for clustering calculation
        undirected = graph.to_undirected()
        return nx.average_clustering(undirected)

    def _filter_by_threshold(self, centrality: dict[str, float], threshold: float) -> list[str]:
        """Filter agents by centrality threshold.

        Args:
            centrality: Dictionary mapping node to centrality value
            threshold: Minimum centrality value

        Returns:
            List of agent IDs meeting threshold
        """
        return [agent for agent, score in centrality.items() if score >= threshold]

    def identify_hubs(self, graph: nx.DiGraph, threshold: float = 0.5) -> list[str]:
        """Identify hub agents with high degree centrality.

        Args:
            graph: NetworkX DiGraph
            threshold: Minimum degree centrality to be considered a hub

        Returns:
            List of agent IDs that are hubs
        """
        return self._filter_by_threshold(self.calculate_degree_centrality(graph), threshold)

    def identify_bridges(self, graph: nx.DiGraph, threshold: float = 0.1) -> list[str]:
        """Identify bridge agents with high betweenness centrality.

        Args:
            graph: NetworkX DiGraph
            threshold: Minimum betweenness centrality to be considered a bridge

        Returns:
            List of agent IDs that are bridges
        """
        return self._filter_by_threshold(self.calculate_betweenness_centrality(graph), threshold)

    def identify_isolated_agents(self, graph: nx.DiGraph) -> list[str]:
        """Identify isolated agents with no meaningful connections.

        Args:
            graph: NetworkX DiGraph

        Returns:
            List of agent IDs that are isolated
        """
        isolated = []
        for node in graph.nodes:
            # Count non-self-loop edges
            in_edges = [e for e in graph.in_edges(node) if e[0] != node]
            out_edges = [e for e in graph.out_edges(node) if e[1] != node]

            if len(in_edges) == 0 and len(out_edges) == 0:
                isolated.append(node)

        return isolated

    def export_to_json(self, graph: nx.DiGraph) -> str:
        """Export graph to JSON format.

        Args:
            graph: NetworkX DiGraph

        Returns:
            JSON string representation of graph
        """
        data = {
            "nodes": [{"id": node} for node in graph.nodes],
            "edges": [
                {
                    "source": u,
                    "target": v,
                    "interaction_type": graph[u][v].get("interaction_type", ""),
                    "timestamp": graph[u][v].get("timestamp", 0.0),
                }
                for u, v in graph.edges
            ],
        }
        return json.dumps(data)

    def export_to_graphml(self, graph: nx.DiGraph) -> str:
        """Export graph to GraphML format.

        Args:
            graph: NetworkX DiGraph

        Returns:
            GraphML string representation of graph
        """
        buffer = BytesIO()
        nx.write_graphml(graph, buffer)
        return buffer.getvalue().decode("utf-8")


class GraphMetricsEvaluator:
    """Evaluator for calculating comprehensive graph-based metrics."""

    def __init__(self) -> None:
        """Initialize the evaluator with a GraphAnalyzer."""
        self.analyzer = GraphAnalyzer()

    def evaluate(self, interactions: list[AgentInteraction]) -> GraphMetrics:
        """Evaluate agent interactions to produce graph-based metrics.

        Args:
            interactions: List of AgentInteraction objects

        Returns:
            GraphMetrics object with calculated complexity metrics
        """
        # Build graph
        graph = self.analyzer.build_graph(interactions)

        # Calculate all metrics
        density = self.analyzer.calculate_density(graph)
        avg_degree_centrality = self.analyzer.calculate_avg_degree_centrality(graph)
        avg_betweenness_centrality = self.analyzer.calculate_avg_betweenness_centrality(graph)
        avg_clustering_coefficient = self.analyzer.calculate_avg_clustering_coefficient(graph)

        return GraphMetrics(
            density=density,
            avg_degree_centrality=avg_degree_centrality,
            avg_betweenness_centrality=avg_betweenness_centrality,
            avg_clustering_coefficient=avg_clustering_coefficient,
            num_nodes=len(graph.nodes),
            num_edges=len(graph.edges),
        )
