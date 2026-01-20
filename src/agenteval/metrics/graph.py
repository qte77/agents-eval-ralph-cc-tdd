"""Graph-based complexity analysis for agent interactions.

This module provides NetworkX-based graph analysis of agent interactions,
calculating complexity metrics and identifying coordination patterns.
"""

from typing import Any

import networkx as nx


def build_interaction_graph(interactions: list[dict[str, Any]]) -> nx.DiGraph:
    """Build a directed graph from agent interactions.

    Args:
        interactions: List of interaction dicts with 'source', 'target', 'timestamp', 'type'

    Returns:
        NetworkX DiGraph with agents as nodes and interactions as edges

    Raises:
        ValueError: If interactions list is empty
    """
    if not interactions:
        raise ValueError("Interactions cannot be empty")

    graph = nx.DiGraph()

    for interaction in interactions:
        source = interaction["source"]
        target = interaction["target"]

        # Add nodes if they don't exist
        if source not in graph:
            graph.add_node(source)
        if target not in graph:
            graph.add_node(target)

        # Add or update edge with weight
        if graph.has_edge(source, target):
            graph[source][target]["weight"] += 1
        else:
            graph.add_edge(source, target, weight=1)

    return graph


def calculate_density(graph: nx.DiGraph) -> float:
    """Calculate the density of the interaction graph.

    Density is the ratio of actual edges to possible edges.
    For a single node, density is 0.0.

    Args:
        graph: NetworkX DiGraph

    Returns:
        Density value between 0.0 and 1.0
    """
    if graph.number_of_nodes() <= 1:
        return 0.0

    return nx.density(graph)


def calculate_node_centrality(graph: nx.DiGraph) -> dict[str, float]:
    """Calculate degree centrality for each node in the graph.

    Degree centrality measures the importance of a node based on
    the number of connections it has.

    Args:
        graph: NetworkX DiGraph

    Returns:
        Dictionary mapping node IDs to centrality values (0.0 to 1.0)
    """
    return nx.degree_centrality(graph)


def calculate_clustering_coefficient(graph: nx.DiGraph) -> float:
    """Calculate the average clustering coefficient of the graph.

    Clustering coefficient measures how much nodes tend to cluster together.
    For directed graphs, we use the undirected version.

    Args:
        graph: NetworkX DiGraph

    Returns:
        Average clustering coefficient between 0.0 and 1.0
    """
    # Convert to undirected for clustering calculation
    undirected = graph.to_undirected()
    return nx.average_clustering(undirected)


def identify_coordination_patterns(graph: nx.DiGraph) -> dict[str, Any]:
    """Identify coordination patterns in the interaction graph.

    Analyzes the graph structure to determine if it follows
    hub-and-spoke, mesh, or hierarchical patterns.

    Args:
        graph: NetworkX DiGraph

    Returns:
        Dictionary with pattern_type and relevant metadata
    """
    centrality = calculate_node_centrality(graph)
    density = calculate_density(graph)

    # Sort nodes by centrality
    sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

    # Mesh: High density, nodes are equally connected
    # Check mesh first as it has specific density requirement
    if density >= 0.8:
        return {"pattern_type": "mesh"}

    # Hub-and-spoke: One or few nodes have much higher centrality
    if len(sorted_nodes) > 0:
        max_centrality = sorted_nodes[0][1]
        hub_threshold = 0.7  # Node must have high centrality

        if max_centrality >= hub_threshold:
            hub_nodes = [node for node, cent in sorted_nodes if cent >= hub_threshold]
            return {"pattern_type": "hub_and_spoke", "hub_nodes": hub_nodes}

    # Hierarchical: Multiple levels (detect through graph structure)
    # Simplification: If we have moderate connectivity but not hub-and-spoke
    # Add hub_nodes for hierarchical pattern too
    hub_nodes = [node for node, cent in sorted_nodes[: min(2, len(sorted_nodes))]]
    return {"pattern_type": "hierarchical", "hub_nodes": hub_nodes}


def export_to_json(graph: nx.DiGraph) -> str:
    """Export graph to JSON format.

    Args:
        graph: NetworkX DiGraph

    Returns:
        JSON string representation of the graph

    Raises:
        ValueError: If graph is empty
    """
    if graph.number_of_nodes() == 0:
        raise ValueError("Graph cannot be empty")

    # Convert to node-link format
    data = nx.node_link_data(graph)

    # Convert to JSON string
    import json

    return json.dumps(data)


def export_to_graphml(graph: nx.DiGraph) -> str:
    """Export graph to GraphML format.

    Args:
        graph: NetworkX DiGraph

    Returns:
        GraphML XML string representation of the graph

    Raises:
        ValueError: If graph is empty
    """
    if graph.number_of_nodes() == 0:
        raise ValueError("Graph cannot be empty")

    # Use BytesIO to capture the output and decode to string
    from io import BytesIO

    output = BytesIO()
    nx.write_graphml(graph, output)
    return output.getvalue().decode("utf-8")


class GraphAnalyzer:
    """Analyzer for agent interaction graphs.

    Combines graph building, metric calculation, and export functionality
    into a single interface.
    """

    def __init__(self, interactions: list[dict[str, Any]]):
        """Initialize analyzer with interaction data.

        Args:
            interactions: List of interaction dicts with 'source', 'target', 'timestamp', 'type'
        """
        self.graph = build_interaction_graph(interactions)

    def analyze(self) -> dict[str, Any]:
        """Perform complete graph analysis.

        Returns:
            Dictionary with all calculated metrics:
            - density: Graph density
            - centrality: Node centrality values
            - clustering_coefficient: Average clustering coefficient
            - coordination_patterns: Identified patterns
        """
        return {
            "density": calculate_density(self.graph),
            "centrality": calculate_node_centrality(self.graph),
            "clustering_coefficient": calculate_clustering_coefficient(self.graph),
            "coordination_patterns": identify_coordination_patterns(self.graph),
        }

    def export_json(self) -> str:
        """Export graph to JSON format.

        Returns:
            JSON string representation of the graph
        """
        return export_to_json(self.graph)

    def export_graphml(self) -> str:
        """Export graph to GraphML format.

        Returns:
            GraphML XML string representation of the graph
        """
        return export_to_graphml(self.graph)
