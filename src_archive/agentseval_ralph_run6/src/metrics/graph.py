"""Graph-based complexity analysis for agent interactions."""

import json
from pathlib import Path

import networkx as nx


def build_interaction_graph(interactions: list[dict]) -> nx.DiGraph:
    """Build directed graph from agent interactions.

    Args:
        interactions: List of interaction dicts with from_agent, to_agent, interaction_type.

    Returns:
        NetworkX directed graph with agents as nodes and interactions as edges.
    """
    graph = nx.DiGraph()

    for interaction in interactions:
        from_agent = interaction["from_agent"]
        to_agent = interaction["to_agent"]

        # Add nodes
        graph.add_node(from_agent)
        graph.add_node(to_agent)

        # Add edge with weight (increment if edge exists)
        if graph.has_edge(from_agent, to_agent):
            graph[from_agent][to_agent]["weight"] += 1
        else:
            graph.add_edge(from_agent, to_agent, weight=1)

    return graph


def calculate_graph_density(graph: nx.DiGraph) -> float:
    """Calculate graph density.

    Args:
        graph: NetworkX directed graph.

    Returns:
        Density value between 0.0 and 1.0.
    """
    if graph.number_of_nodes() == 0:
        return 0.0

    return nx.density(graph)


def calculate_centrality_metrics(graph: nx.DiGraph) -> dict[str, float]:
    """Calculate degree centrality for all agents.

    Args:
        graph: NetworkX directed graph.

    Returns:
        Dict mapping agent_id to centrality score.
    """
    if graph.number_of_nodes() == 0:
        return {}

    if graph.number_of_nodes() == 1:
        return {list(graph.nodes())[0]: 0.0}

    # Use degree centrality (combines in and out degree)
    centrality = nx.degree_centrality(graph)
    return centrality


def calculate_clustering_coefficient(graph: nx.DiGraph) -> float:
    """Calculate average clustering coefficient.

    Args:
        graph: NetworkX directed graph.

    Returns:
        Clustering coefficient between 0.0 and 1.0.
    """
    if graph.number_of_nodes() == 0:
        return 0.0

    # Convert to undirected for clustering calculation
    undirected = graph.to_undirected()
    return nx.average_clustering(undirected)


def identify_coordination_patterns(graph: nx.DiGraph) -> dict:
    """Identify coordination patterns in agent interactions.

    Args:
        graph: NetworkX directed graph.

    Returns:
        Dict with hub_agents and isolated_agents lists.
    """
    if graph.number_of_nodes() == 0:
        return {"hub_agents": [], "isolated_agents": []}

    # Identify hub agents (high degree centrality)
    if graph.number_of_nodes() > 1:
        centrality = nx.degree_centrality(graph)
        avg_centrality = sum(centrality.values()) / len(centrality)
        hub_agents = [agent for agent, cent in centrality.items() if cent > avg_centrality * 1.5]
    else:
        hub_agents = []

    # Identify isolated agents (no connections)
    isolated_agents = [node for node in graph.nodes() if graph.degree(node) == 0]

    return {"hub_agents": hub_agents, "isolated_agents": isolated_agents}


def export_graph_to_json(graph: nx.DiGraph) -> str:
    """Export graph to JSON format.

    Args:
        graph: NetworkX directed graph.

    Returns:
        JSON string with nodes and edges.
    """
    data = {
        "nodes": [{"id": node} for node in graph.nodes()],
        "edges": [
            {
                "source": source,
                "target": target,
                "weight": graph[source][target].get("weight", 1),
            }
            for source, target in graph.edges()
        ],
    }
    return json.dumps(data)


def export_graph_to_graphml(graph: nx.DiGraph, output_path: Path) -> None:
    """Export graph to GraphML format.

    Args:
        graph: NetworkX directed graph.
        output_path: Path to output GraphML file.
    """
    nx.write_graphml(graph, output_path)


class GraphMetrics:
    """Graph-based complexity analyzer."""

    def __init__(self):
        """Initialize GraphMetrics."""
        self.graph = None

    def analyze(self, interactions: list[dict]) -> dict:
        """Analyze all graph metrics from interactions.

        Args:
            interactions: List of interaction dicts.

        Returns:
            Dict with density, centrality, clustering_coefficient, coordination_patterns.
        """
        self.graph = build_interaction_graph(interactions)

        return {
            "density": calculate_graph_density(self.graph),
            "centrality": calculate_centrality_metrics(self.graph),
            "clustering_coefficient": calculate_clustering_coefficient(self.graph),
            "coordination_patterns": identify_coordination_patterns(self.graph),
        }

    def to_json(self, result: dict) -> str:
        """Output metrics in structured JSON format.

        Args:
            result: Result dict from analyze().

        Returns:
            JSON string.
        """
        return json.dumps(result)

    def export_graph_json(self) -> str:
        """Export the analyzed graph to JSON format.

        Returns:
            JSON string with graph data.

        Raises:
            ValueError: If analyze() hasn't been called yet.
        """
        if self.graph is None:
            raise ValueError("Must call analyze() before exporting graph")

        return export_graph_to_json(self.graph)

    def export_graph_graphml(self, output_path: Path) -> None:
        """Export the analyzed graph to GraphML file.

        Args:
            output_path: Path to output GraphML file.

        Raises:
            ValueError: If analyze() hasn't been called yet.
        """
        if self.graph is None:
            raise ValueError("Must call analyze() before exporting graph")

        export_graph_to_graphml(self.graph, output_path)
