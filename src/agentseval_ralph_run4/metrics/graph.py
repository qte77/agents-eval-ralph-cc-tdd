"""Graph-based complexity analyzer for agent interactions.

Analyzes agent interactions through graph structures to understand coordination
complexity using NetworkX for graph operations and metrics calculation.
"""

import json
from io import BytesIO
from typing import Any

import networkx as nx
from pydantic import BaseModel, Field, field_validator


class AgentInteraction(BaseModel):
    """Model for agent-to-agent interaction."""

    from_agent: str
    to_agent: str
    interaction_type: str
    timestamp: str
    metadata: dict[str, Any] | None = None


class GraphMetrics(BaseModel):
    """Model for graph complexity metrics."""

    density: float = Field(..., ge=0.0, le=1.0)
    avg_clustering_coefficient: float = Field(..., ge=0.0, le=1.0)
    avg_betweenness_centrality: float = Field(..., ge=0.0, le=1.0)
    num_nodes: int
    num_edges: int

    @field_validator(
        "density",
        "avg_clustering_coefficient",
        "avg_betweenness_centrality",
    )
    @classmethod
    def validate_metric(cls, v: float) -> float:
        """Validate metric values are between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("metric must be between 0 and 1")
        return v


class GraphComplexityAnalyzer:
    """Analyzer for graph-based agent interaction complexity."""

    def build_graph(self, interactions: list[AgentInteraction]) -> nx.DiGraph:
        """Build a directed graph from agent interactions.

        Args:
            interactions: List of agent interactions

        Returns:
            NetworkX directed graph representing interactions
        """
        graph = nx.DiGraph()

        for interaction in interactions:
            graph.add_edge(
                interaction.from_agent,
                interaction.to_agent,
                interaction_type=interaction.interaction_type,
                timestamp=interaction.timestamp,
                metadata=interaction.metadata,
            )

        return graph

    def calculate_density(self, graph: nx.DiGraph) -> float:
        """Calculate graph density metric.

        Args:
            graph: NetworkX directed graph

        Returns:
            Density value between 0.0 and 1.0
        """
        if graph.number_of_nodes() == 0:
            return 0.0
        return nx.density(graph)

    def calculate_clustering_coefficient(self, graph: nx.DiGraph) -> float:
        """Calculate average clustering coefficient.

        Args:
            graph: NetworkX directed graph

        Returns:
            Average clustering coefficient between 0.0 and 1.0
        """
        if graph.number_of_nodes() == 0:
            return 0.0

        # Convert to undirected for clustering calculation
        undirected = graph.to_undirected()
        clustering_dict: dict[Any, float] = nx.clustering(undirected)  # type: ignore[assignment]

        if not clustering_dict:
            return 0.0

        clustering_values = list(clustering_dict.values())
        return sum(clustering_values) / len(clustering_values)

    def calculate_betweenness_centrality(self, graph: nx.DiGraph) -> float:
        """Calculate average betweenness centrality.

        Args:
            graph: NetworkX directed graph

        Returns:
            Average betweenness centrality between 0.0 and 1.0
        """
        if graph.number_of_nodes() == 0:
            return 0.0

        centrality = nx.betweenness_centrality(graph)
        if not centrality:
            return 0.0

        return sum(centrality.values()) / len(centrality)

    def calculate_metrics(self, interactions: list[AgentInteraction]) -> GraphMetrics:
        """Calculate all graph complexity metrics from interactions.

        Args:
            interactions: List of agent interactions

        Returns:
            GraphMetrics model with all calculated metrics
        """
        graph = self.build_graph(interactions)

        return GraphMetrics(
            density=self.calculate_density(graph),
            avg_clustering_coefficient=self.calculate_clustering_coefficient(graph),
            avg_betweenness_centrality=self.calculate_betweenness_centrality(graph),
            num_nodes=graph.number_of_nodes(),
            num_edges=graph.number_of_edges(),
        )

    def identify_coordination_patterns(
        self, interactions: list[AgentInteraction]
    ) -> dict[str, list[Any]]:
        """Identify coordination patterns between agents.

        Args:
            interactions: List of agent interactions

        Returns:
            Dictionary with identified patterns including bidirectional_pairs and hub_agents
        """
        graph = self.build_graph(interactions)

        # Find bidirectional pairs (agents with mutual interactions)
        bidirectional_pairs = []
        for node1 in graph.nodes():
            for node2 in graph.successors(node1):
                if graph.has_edge(node2, node1):
                    pair = tuple(sorted([node1, node2]))
                    if pair not in bidirectional_pairs:
                        bidirectional_pairs.append(pair)

        # Find hub agents (agents with high out-degree)
        if graph.number_of_nodes() > 0:
            avg_degree = sum(dict(graph.out_degree()).values()) / graph.number_of_nodes()
            hub_agents = [node for node in graph.nodes() if graph.out_degree(node) > avg_degree]
        else:
            hub_agents = []

        return {"bidirectional_pairs": bidirectional_pairs, "hub_agents": hub_agents}

    def export_to_json(self, graph: nx.DiGraph) -> str:
        """Export graph to JSON format.

        Args:
            graph: NetworkX directed graph

        Returns:
            JSON string representation of the graph
        """
        data = {
            "nodes": [{"id": node} for node in graph.nodes()],
            "edges": [
                {
                    "source": u,
                    "target": v,
                    "interaction_type": data.get("interaction_type"),
                    "timestamp": data.get("timestamp"),
                    "metadata": data.get("metadata"),
                }
                for u, v, data in graph.edges(data=True)
            ],
        }
        return json.dumps(data, indent=2)

    def export_to_graphml(self, graph: nx.DiGraph) -> str:
        """Export graph to GraphML format.

        Args:
            graph: NetworkX directed graph

        Returns:
            GraphML XML string representation of the graph
        """
        # Create a clean copy without None values (GraphML doesn't support None)
        clean_graph = nx.DiGraph()
        for u, v, data in graph.edges(data=True):
            clean_data = {k: v for k, v in data.items() if v is not None}
            clean_graph.add_edge(u, v, **clean_data)

        output = BytesIO()
        nx.write_graphml(clean_graph, output)
        return output.getvalue().decode("utf-8")
