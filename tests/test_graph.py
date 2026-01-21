"""Tests for graph-based complexity analysis."""

import json
from pathlib import Path

import networkx as nx
import pytest

from agenteval.metrics.graph import (
    GraphMetrics,
    build_interaction_graph,
    calculate_graph_density,
    calculate_centrality_metrics,
    calculate_clustering_coefficient,
    identify_coordination_patterns,
    export_graph_to_json,
    export_graph_to_graphml,
)


def test_build_interaction_graph_simple():
    """Test building a simple interaction graph from agent interactions."""
    interactions = [
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
        {"from_agent": "agent_2", "to_agent": "agent_3", "interaction_type": "message"},
        {"from_agent": "agent_1", "to_agent": "agent_3", "interaction_type": "message"},
    ]

    graph = build_interaction_graph(interactions)

    assert isinstance(graph, nx.DiGraph)
    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 3


def test_build_interaction_graph_with_weights():
    """Test building interaction graph with edge weights for repeated interactions."""
    interactions = [
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
        {"from_agent": "agent_2", "to_agent": "agent_1", "interaction_type": "response"},
    ]

    graph = build_interaction_graph(interactions)

    # Should have weighted edges
    assert graph["agent_1"]["agent_2"]["weight"] == 2
    assert graph["agent_2"]["agent_1"]["weight"] == 1


def test_build_interaction_graph_empty():
    """Test building graph from empty interactions."""
    interactions = []

    graph = build_interaction_graph(interactions)

    assert graph.number_of_nodes() == 0
    assert graph.number_of_edges() == 0


def test_calculate_graph_density_full():
    """Test density calculation for fully connected graph."""
    interactions = [
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
        {"from_agent": "agent_2", "to_agent": "agent_1", "interaction_type": "message"},
        {"from_agent": "agent_1", "to_agent": "agent_3", "interaction_type": "message"},
        {"from_agent": "agent_3", "to_agent": "agent_1", "interaction_type": "message"},
        {"from_agent": "agent_2", "to_agent": "agent_3", "interaction_type": "message"},
        {"from_agent": "agent_3", "to_agent": "agent_2", "interaction_type": "message"},
    ]

    graph = build_interaction_graph(interactions)
    density = calculate_graph_density(graph)

    # Fully connected: density = 1.0
    assert density == 1.0


def test_calculate_graph_density_sparse():
    """Test density calculation for sparse graph."""
    interactions = [
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
    ]

    graph = build_interaction_graph(interactions)
    density = calculate_graph_density(graph)

    # Sparse graph: low density
    assert 0.0 <= density < 0.5


def test_calculate_graph_density_empty():
    """Test density calculation for empty graph."""
    graph = nx.DiGraph()

    density = calculate_graph_density(graph)

    assert density == 0.0


def test_calculate_centrality_metrics():
    """Test centrality metrics calculation for agents."""
    interactions = [
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
        {"from_agent": "agent_1", "to_agent": "agent_3", "interaction_type": "message"},
        {"from_agent": "agent_2", "to_agent": "agent_3", "interaction_type": "message"},
    ]

    graph = build_interaction_graph(interactions)
    centrality = calculate_centrality_metrics(graph)

    # agent_1 has highest out-degree centrality (sends to 2 agents)
    # agent_3 has highest in-degree centrality (receives from 2 agents)
    assert isinstance(centrality, dict)
    assert "agent_1" in centrality
    assert "agent_2" in centrality
    assert "agent_3" in centrality
    assert all(0.0 <= v <= 1.0 for v in centrality.values())


def test_calculate_centrality_metrics_single_node():
    """Test centrality metrics for single node graph."""
    interactions = []
    graph = nx.DiGraph()
    graph.add_node("agent_1")

    centrality = calculate_centrality_metrics(graph)

    assert centrality == {"agent_1": 0.0}


def test_calculate_centrality_metrics_empty():
    """Test centrality metrics for empty graph."""
    graph = nx.DiGraph()

    centrality = calculate_centrality_metrics(graph)

    assert centrality == {}


def test_calculate_clustering_coefficient():
    """Test clustering coefficient calculation."""
    interactions = [
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
        {"from_agent": "agent_2", "to_agent": "agent_3", "interaction_type": "message"},
        {"from_agent": "agent_3", "to_agent": "agent_1", "interaction_type": "message"},
    ]

    graph = build_interaction_graph(interactions)
    clustering = calculate_clustering_coefficient(graph)

    # Triangle structure should have clustering > 0
    assert 0.0 <= clustering <= 1.0


def test_calculate_clustering_coefficient_no_clustering():
    """Test clustering coefficient for linear graph (no clustering)."""
    interactions = [
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
        {"from_agent": "agent_2", "to_agent": "agent_3", "interaction_type": "message"},
    ]

    graph = build_interaction_graph(interactions)
    clustering = calculate_clustering_coefficient(graph)

    # Linear chain has no clustering
    assert clustering == 0.0


def test_calculate_clustering_coefficient_empty():
    """Test clustering coefficient for empty graph."""
    graph = nx.DiGraph()

    clustering = calculate_clustering_coefficient(graph)

    assert clustering == 0.0


def test_identify_coordination_patterns_hub():
    """Test identifying hub coordination pattern."""
    # Create hub-and-spoke pattern: agent_1 as central hub
    interactions = [
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
        {"from_agent": "agent_1", "to_agent": "agent_3", "interaction_type": "message"},
        {"from_agent": "agent_1", "to_agent": "agent_4", "interaction_type": "message"},
        {"from_agent": "agent_2", "to_agent": "agent_1", "interaction_type": "response"},
        {"from_agent": "agent_3", "to_agent": "agent_1", "interaction_type": "response"},
        {"from_agent": "agent_4", "to_agent": "agent_1", "interaction_type": "response"},
    ]

    graph = build_interaction_graph(interactions)
    patterns = identify_coordination_patterns(graph)

    assert isinstance(patterns, dict)
    assert "hub_agents" in patterns
    assert "agent_1" in patterns["hub_agents"]


def test_identify_coordination_patterns_isolated():
    """Test identifying isolated agents."""
    interactions = [
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
    ]

    graph = build_interaction_graph(interactions)
    graph.add_node("agent_3")  # Isolated node

    patterns = identify_coordination_patterns(graph)

    assert "isolated_agents" in patterns
    assert "agent_3" in patterns["isolated_agents"]


def test_identify_coordination_patterns_empty():
    """Test coordination patterns for empty graph."""
    graph = nx.DiGraph()

    patterns = identify_coordination_patterns(graph)

    assert patterns == {"hub_agents": [], "isolated_agents": []}


def test_export_graph_to_json():
    """Test exporting graph to JSON format."""
    interactions = [
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
        {"from_agent": "agent_2", "to_agent": "agent_3", "interaction_type": "message"},
    ]

    graph = build_interaction_graph(interactions)
    json_data = export_graph_to_json(graph)

    # Should be valid JSON with nodes and edges
    data = json.loads(json_data)
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) == 3
    assert len(data["edges"]) == 2


def test_export_graph_to_json_with_attributes():
    """Test JSON export includes node and edge attributes."""
    interactions = [
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
    ]

    graph = build_interaction_graph(interactions)
    json_data = export_graph_to_json(graph)

    data = json.loads(json_data)
    # Check edge has weight attribute
    assert "weight" in data["edges"][0]


def test_export_graph_to_graphml(tmp_path: Path):
    """Test exporting graph to GraphML format."""
    interactions = [
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
        {"from_agent": "agent_2", "to_agent": "agent_3", "interaction_type": "message"},
    ]

    graph = build_interaction_graph(interactions)
    output_path = tmp_path / "test_graph.graphml"

    export_graph_to_graphml(graph, output_path)

    # Verify file was created and is valid GraphML
    assert output_path.exists()
    loaded_graph = nx.read_graphml(output_path)
    assert loaded_graph.number_of_nodes() == 3
    assert loaded_graph.number_of_edges() == 2


def test_export_graph_to_graphml_empty(tmp_path: Path):
    """Test exporting empty graph to GraphML."""
    graph = nx.DiGraph()
    output_path = tmp_path / "empty_graph.graphml"

    export_graph_to_graphml(graph, output_path)

    assert output_path.exists()
    loaded_graph = nx.read_graphml(output_path)
    assert loaded_graph.number_of_nodes() == 0


def test_graph_metrics_class_initialization():
    """Test GraphMetrics class can be initialized."""
    metrics = GraphMetrics()

    assert metrics is not None


def test_graph_metrics_analyze_all():
    """Test analyzing all graph metrics together."""
    metrics = GraphMetrics()

    interactions = [
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
        {"from_agent": "agent_2", "to_agent": "agent_3", "interaction_type": "message"},
        {"from_agent": "agent_3", "to_agent": "agent_1", "interaction_type": "message"},
    ]

    result = metrics.analyze(interactions)

    assert "density" in result
    assert "centrality" in result
    assert "clustering_coefficient" in result
    assert "coordination_patterns" in result
    assert isinstance(result["centrality"], dict)
    assert isinstance(result["coordination_patterns"], dict)


def test_graph_metrics_analyze_empty():
    """Test analyzing empty interactions."""
    metrics = GraphMetrics()

    result = metrics.analyze([])

    assert result["density"] == 0.0
    assert result["centrality"] == {}
    assert result["clustering_coefficient"] == 0.0


def test_graph_metrics_to_json():
    """Test metrics can be output in structured JSON format."""
    metrics = GraphMetrics()

    interactions = [
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
    ]

    result = metrics.analyze(interactions)
    json_output = metrics.to_json(result)

    assert isinstance(json_output, str)
    assert "density" in json_output
    assert "centrality" in json_output
    assert "clustering_coefficient" in json_output


def test_graph_metrics_export_graph():
    """Test GraphMetrics can export the analyzed graph."""
    metrics = GraphMetrics()

    interactions = [
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
        {"from_agent": "agent_2", "to_agent": "agent_3", "interaction_type": "message"},
    ]

    # Analyze first to build internal graph
    metrics.analyze(interactions)

    # Export to JSON
    json_data = metrics.export_graph_json()
    data = json.loads(json_data)

    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) == 3


def test_graph_metrics_export_graphml(tmp_path: Path):
    """Test GraphMetrics can export graph to GraphML file."""
    metrics = GraphMetrics()

    interactions = [
        {"from_agent": "agent_1", "to_agent": "agent_2", "interaction_type": "message"},
    ]

    metrics.analyze(interactions)

    output_path = tmp_path / "metrics_graph.graphml"
    metrics.export_graph_graphml(output_path)

    assert output_path.exists()
    loaded_graph = nx.read_graphml(output_path)
    assert loaded_graph.number_of_nodes() == 2
