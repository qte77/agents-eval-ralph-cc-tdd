"""Tests for graph-based complexity analysis module.

Tests verify graph structure modeling, complexity metric calculation,
coordination pattern identification, and graph data export functionality.
"""

import json
from pathlib import Path

import networkx as nx
import pytest
from agenteval.metrics.graph import (  # type: ignore[import-not-found]
    GraphAnalyzer,
    export_graph,
)


def test_model_agent_interactions_as_graph():
    """Test that agent interactions are modeled as NetworkX graph structures."""
    # Mock agent interaction data
    interactions = [
        {"source": "agent1", "target": "agent2", "interaction_type": "request"},
        {"source": "agent2", "target": "agent3", "interaction_type": "response"},
        {"source": "agent1", "target": "agent3", "interaction_type": "request"},
    ]

    analyzer = GraphAnalyzer()
    graph = analyzer.build_graph(interactions)

    assert isinstance(graph, nx.DiGraph)
    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 3
    assert "agent1" in graph.nodes()
    assert "agent2" in graph.nodes()
    assert "agent3" in graph.nodes()
    assert graph.has_edge("agent1", "agent2")
    assert graph.has_edge("agent2", "agent3")
    assert graph.has_edge("agent1", "agent3")


def test_build_graph_with_edge_attributes():
    """Test that edge attributes are preserved when building graph."""
    interactions = [
        {
            "source": "agent1",
            "target": "agent2",
            "interaction_type": "request",
            "weight": 1.0,
        },
        {
            "source": "agent2",
            "target": "agent3",
            "interaction_type": "response",
            "weight": 0.5,
        },
    ]

    analyzer = GraphAnalyzer()
    graph = analyzer.build_graph(interactions)

    edge_data = graph.get_edge_data("agent1", "agent2")
    assert edge_data is not None
    assert edge_data["interaction_type"] == "request"
    assert edge_data["weight"] == 1.0


def test_calculate_graph_density():
    """Test calculation of graph density metric."""
    interactions = [
        {"source": "agent1", "target": "agent2", "interaction_type": "request"},
        {"source": "agent2", "target": "agent3", "interaction_type": "response"},
        {"source": "agent3", "target": "agent1", "interaction_type": "request"},
    ]

    analyzer = GraphAnalyzer()
    graph = analyzer.build_graph(interactions)
    density = analyzer.calculate_density(graph)

    # For a directed graph with 3 nodes and 3 edges:
    # density = edges / (nodes * (nodes - 1)) = 3 / (3 * 2) = 0.5
    assert density == pytest.approx(0.5, abs=0.01)
    assert 0.0 <= density <= 1.0


def test_calculate_graph_density_fully_connected():
    """Test density for fully connected graph."""
    # All possible edges in a 3-node directed graph
    interactions = [
        {"source": "a1", "target": "a2"},
        {"source": "a1", "target": "a3"},
        {"source": "a2", "target": "a1"},
        {"source": "a2", "target": "a3"},
        {"source": "a3", "target": "a1"},
        {"source": "a3", "target": "a2"},
    ]

    analyzer = GraphAnalyzer()
    graph = analyzer.build_graph(interactions)
    density = analyzer.calculate_density(graph)

    assert density == 1.0


def test_calculate_centrality_metrics():
    """Test calculation of node centrality metrics."""
    interactions = [
        {"source": "agent1", "target": "agent2"},
        {"source": "agent1", "target": "agent3"},
        {"source": "agent2", "target": "agent3"},
        {"source": "agent3", "target": "agent4"},
    ]

    analyzer = GraphAnalyzer()
    graph = analyzer.build_graph(interactions)
    centrality = analyzer.calculate_centrality(graph)

    assert isinstance(centrality, dict)
    assert "agent1" in centrality
    assert "agent2" in centrality
    assert "agent3" in centrality
    assert "agent4" in centrality

    # All centrality values should be between 0 and 1
    for node, value in centrality.items():
        assert 0.0 <= value <= 1.0

    # agent3 should have high centrality (hub)
    assert centrality["agent3"] > 0


def test_calculate_clustering_coefficient():
    """Test calculation of clustering coefficient."""
    # Create a triangle: agent1 -> agent2 -> agent3 -> agent1
    interactions = [
        {"source": "agent1", "target": "agent2"},
        {"source": "agent2", "target": "agent3"},
        {"source": "agent3", "target": "agent1"},
        {"source": "agent1", "target": "agent4"},
    ]

    analyzer = GraphAnalyzer()
    graph = analyzer.build_graph(interactions)
    clustering = analyzer.calculate_clustering_coefficient(graph)

    assert isinstance(clustering, float)
    assert 0.0 <= clustering <= 1.0


def test_identify_coordination_patterns():
    """Test identification of coordination patterns between agents."""
    # Create pattern: agent1 coordinates with agent2, agent2 with agent3
    interactions = [
        {"source": "agent1", "target": "agent2", "interaction_type": "request"},
        {"source": "agent2", "target": "agent1", "interaction_type": "response"},
        {"source": "agent2", "target": "agent3", "interaction_type": "request"},
        {"source": "agent3", "target": "agent2", "interaction_type": "response"},
    ]

    analyzer = GraphAnalyzer()
    graph = analyzer.build_graph(interactions)
    patterns = analyzer.identify_coordination_patterns(graph)

    assert isinstance(patterns, dict)
    assert "bidirectional_pairs" in patterns
    assert "central_coordinators" in patterns

    # Should identify bidirectional coordination between agent1-agent2 and agent2-agent3
    bidirectional = patterns["bidirectional_pairs"]
    assert isinstance(bidirectional, list)
    assert len(bidirectional) > 0


def test_identify_central_coordinators():
    """Test identification of central coordinator agents."""
    # agent2 is a central hub
    interactions = [
        {"source": "agent1", "target": "agent2"},
        {"source": "agent2", "target": "agent3"},
        {"source": "agent2", "target": "agent4"},
        {"source": "agent5", "target": "agent2"},
    ]

    analyzer = GraphAnalyzer()
    graph = analyzer.build_graph(interactions)
    patterns = analyzer.identify_coordination_patterns(graph)

    central_coordinators = patterns["central_coordinators"]
    assert isinstance(central_coordinators, list)
    assert "agent2" in central_coordinators


def test_export_graph_to_json(tmp_path: Path):
    """Test export of graph data in JSON format."""
    interactions = [
        {"source": "agent1", "target": "agent2", "weight": 1.0},
        {"source": "agent2", "target": "agent3", "weight": 0.5},
    ]

    analyzer = GraphAnalyzer()
    graph = analyzer.build_graph(interactions)

    output_path = tmp_path / "graph.json"
    export_graph(graph, output_path, format="json")

    assert output_path.exists()

    # Verify JSON structure
    with open(output_path) as f:
        data = json.load(f)

    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) == 3
    assert len(data["edges"]) == 2


def test_export_graph_to_graphml(tmp_path: Path):
    """Test export of graph data in GraphML format."""
    interactions = [
        {"source": "agent1", "target": "agent2"},
        {"source": "agent2", "target": "agent3"},
    ]

    analyzer = GraphAnalyzer()
    graph = analyzer.build_graph(interactions)

    output_path = tmp_path / "graph.graphml"
    export_graph(graph, output_path, format="graphml")

    assert output_path.exists()

    # Verify GraphML can be read back
    loaded_graph = nx.read_graphml(output_path)
    assert loaded_graph.number_of_nodes() == 3
    assert loaded_graph.number_of_edges() == 2


def test_calculate_all_metrics_at_once():
    """Test calculating all graph metrics together."""
    interactions = [
        {"source": "agent1", "target": "agent2"},
        {"source": "agent2", "target": "agent3"},
        {"source": "agent3", "target": "agent1"},
    ]

    analyzer = GraphAnalyzer()
    graph = analyzer.build_graph(interactions)
    metrics = analyzer.calculate_all_metrics(graph)

    assert isinstance(metrics, dict)
    assert "density" in metrics
    assert "avg_centrality" in metrics
    assert "clustering_coefficient" in metrics

    # All metrics should be valid floats between 0 and 1
    assert 0.0 <= metrics["density"] <= 1.0
    assert 0.0 <= metrics["avg_centrality"] <= 1.0
    assert 0.0 <= metrics["clustering_coefficient"] <= 1.0


def test_empty_interactions_returns_empty_graph():
    """Test that empty interactions list returns empty graph."""
    analyzer = GraphAnalyzer()
    graph = analyzer.build_graph([])

    assert isinstance(graph, nx.DiGraph)
    assert graph.number_of_nodes() == 0
    assert graph.number_of_edges() == 0


def test_density_of_empty_graph():
    """Test that density of empty graph returns 0.0."""
    analyzer = GraphAnalyzer()
    graph = nx.DiGraph()
    density = analyzer.calculate_density(graph)

    assert density == 0.0


def test_single_node_graph_metrics():
    """Test metrics calculation for single-node graph."""
    interactions = [{"source": "agent1", "target": "agent1"}]  # Self-loop

    analyzer = GraphAnalyzer()
    graph = analyzer.build_graph(interactions)
    metrics = analyzer.calculate_all_metrics(graph)

    assert metrics["density"] >= 0.0
    assert metrics["avg_centrality"] >= 0.0
    assert metrics["clustering_coefficient"] >= 0.0


def test_invalid_export_format_raises_error(tmp_path: Path):
    """Test that invalid export format raises ValueError."""
    analyzer = GraphAnalyzer()
    graph = analyzer.build_graph([{"source": "a1", "target": "a2"}])

    output_path = tmp_path / "graph.txt"

    with pytest.raises(ValueError, match="Unsupported format"):
        export_graph(graph, output_path, format="invalid")


def test_graph_with_isolated_nodes():
    """Test graph analysis with isolated nodes."""
    # Create graph with isolated node
    interactions = [
        {"source": "agent1", "target": "agent2"},
        {"source": "agent3", "target": "agent3"},  # Isolated self-loop
    ]

    analyzer = GraphAnalyzer()
    graph = analyzer.build_graph(interactions)

    assert graph.number_of_nodes() == 3
    centrality = analyzer.calculate_centrality(graph)
    assert "agent3" in centrality
