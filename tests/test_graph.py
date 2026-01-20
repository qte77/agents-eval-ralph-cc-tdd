"""Tests for graph-based complexity analysis.

Following TDD approach - these tests should FAIL initially.
Tests validate graph complexity metrics: density, centrality, clustering coefficient, and coordination patterns.
"""

import json

import pytest

from agenteval.metrics.graph import (
    GraphAnalyzer,
    build_interaction_graph,
    calculate_clustering_coefficient,
    calculate_density,
    calculate_node_centrality,
    export_to_graphml,
    export_to_json,
    identify_coordination_patterns,
)


class TestBuildInteractionGraph:
    """Tests for building interaction graph from mock data."""

    def test_build_interaction_graph_simple(self):
        """Test building a simple interaction graph with two agents."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent2", "target": "agent1", "timestamp": 101.0, "type": "response"},
        ]
        graph = build_interaction_graph(interactions)

        assert graph is not None
        assert graph.number_of_nodes() == 2
        assert graph.number_of_edges() == 2
        assert "agent1" in graph.nodes()
        assert "agent2" in graph.nodes()

    def test_build_interaction_graph_multiple_agents(self):
        """Test building graph with multiple agents and complex interactions."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent2", "target": "agent3", "timestamp": 101.0, "type": "message"},
            {"source": "agent3", "target": "agent1", "timestamp": 102.0, "type": "message"},
            {"source": "agent1", "target": "agent3", "timestamp": 103.0, "type": "response"},
        ]
        graph = build_interaction_graph(interactions)

        assert graph.number_of_nodes() == 3
        assert graph.number_of_edges() == 4
        assert set(graph.nodes()) == {"agent1", "agent2", "agent3"}

    def test_build_interaction_graph_self_loop(self):
        """Test handling of self-loop interactions."""
        interactions = [
            {"source": "agent1", "target": "agent1", "timestamp": 100.0, "type": "self-message"},
        ]
        graph = build_interaction_graph(interactions)

        assert graph.number_of_nodes() == 1
        # Self-loops should be included
        assert graph.number_of_edges() == 1

    def test_build_interaction_graph_empty_raises(self):
        """Test that empty interactions raises error."""
        with pytest.raises(ValueError, match="Interactions cannot be empty"):
            build_interaction_graph([])

    def test_build_interaction_graph_weighted_edges(self):
        """Test that repeated interactions create weighted edges."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent1", "target": "agent2", "timestamp": 101.0, "type": "message"},
            {"source": "agent1", "target": "agent2", "timestamp": 102.0, "type": "message"},
        ]
        graph = build_interaction_graph(interactions)

        assert graph.number_of_nodes() == 2
        # Should have edge with weight 3
        edge_data = graph.get_edge_data("agent1", "agent2")
        assert edge_data is not None
        assert edge_data["weight"] == 3


class TestCalculateDensity:
    """Tests for graph density calculation."""

    def test_calculate_density_complete_graph(self):
        """Test density calculation for a complete graph."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent1", "target": "agent3", "timestamp": 101.0, "type": "message"},
            {"source": "agent2", "target": "agent1", "timestamp": 102.0, "type": "message"},
            {"source": "agent2", "target": "agent3", "timestamp": 103.0, "type": "message"},
            {"source": "agent3", "target": "agent1", "timestamp": 104.0, "type": "message"},
            {"source": "agent3", "target": "agent2", "timestamp": 105.0, "type": "message"},
        ]
        graph = build_interaction_graph(interactions)
        density = calculate_density(graph)

        # Complete graph has density 1.0
        assert density == 1.0

    def test_calculate_density_sparse_graph(self):
        """Test density calculation for a sparse graph."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
        ]
        graph = build_interaction_graph(interactions)
        density = calculate_density(graph)

        # Two nodes with one directed edge: density = 1/(2*1) = 0.5 for directed
        assert 0.0 < density <= 1.0

    def test_calculate_density_single_node(self):
        """Test density with single node graph."""
        interactions = [
            {"source": "agent1", "target": "agent1", "timestamp": 100.0, "type": "self-message"},
        ]
        graph = build_interaction_graph(interactions)
        density = calculate_density(graph)

        # Single node graph density is typically 0.0
        assert density == 0.0


class TestCalculateNodeCentrality:
    """Tests for node centrality calculation."""

    def test_calculate_node_centrality_hub(self):
        """Test centrality calculation with a clear hub node."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent1", "target": "agent3", "timestamp": 101.0, "type": "message"},
            {"source": "agent1", "target": "agent4", "timestamp": 102.0, "type": "message"},
            {"source": "agent2", "target": "agent1", "timestamp": 103.0, "type": "response"},
        ]
        graph = build_interaction_graph(interactions)
        centrality = calculate_node_centrality(graph)

        assert isinstance(centrality, dict)
        assert "agent1" in centrality
        assert "agent2" in centrality
        # agent1 should have highest centrality as the hub
        assert centrality["agent1"] >= centrality["agent2"]
        assert centrality["agent1"] >= centrality.get("agent3", 0)

    def test_calculate_node_centrality_equal_nodes(self):
        """Test centrality with equally connected nodes."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent2", "target": "agent1", "timestamp": 101.0, "type": "message"},
        ]
        graph = build_interaction_graph(interactions)
        centrality = calculate_node_centrality(graph)

        # Both nodes should have equal centrality
        assert centrality["agent1"] == centrality["agent2"]

    def test_calculate_node_centrality_values_normalized(self):
        """Test that centrality values are normalized between 0 and 1."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent2", "target": "agent3", "timestamp": 101.0, "type": "message"},
        ]
        graph = build_interaction_graph(interactions)
        centrality = calculate_node_centrality(graph)

        for node, value in centrality.items():
            assert 0.0 <= value <= 1.0


class TestCalculateClusteringCoefficient:
    """Tests for clustering coefficient calculation."""

    def test_calculate_clustering_coefficient_complete_graph(self):
        """Test clustering coefficient for complete graph (all nodes connected)."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent1", "target": "agent3", "timestamp": 101.0, "type": "message"},
            {"source": "agent2", "target": "agent1", "timestamp": 102.0, "type": "message"},
            {"source": "agent2", "target": "agent3", "timestamp": 103.0, "type": "message"},
            {"source": "agent3", "target": "agent1", "timestamp": 104.0, "type": "message"},
            {"source": "agent3", "target": "agent2", "timestamp": 105.0, "type": "message"},
        ]
        graph = build_interaction_graph(interactions)
        clustering = calculate_clustering_coefficient(graph)

        # Complete graph has clustering coefficient of 1.0
        assert clustering == 1.0

    def test_calculate_clustering_coefficient_no_clustering(self):
        """Test clustering coefficient for linear chain (no clustering)."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent2", "target": "agent3", "timestamp": 101.0, "type": "message"},
        ]
        graph = build_interaction_graph(interactions)
        clustering = calculate_clustering_coefficient(graph)

        # Linear chain has low/zero clustering
        assert 0.0 <= clustering < 0.5

    def test_calculate_clustering_coefficient_partial(self):
        """Test clustering coefficient with partial clustering."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent2", "target": "agent3", "timestamp": 101.0, "type": "message"},
            {"source": "agent1", "target": "agent3", "timestamp": 102.0, "type": "message"},
            {"source": "agent3", "target": "agent4", "timestamp": 103.0, "type": "message"},
        ]
        graph = build_interaction_graph(interactions)
        clustering = calculate_clustering_coefficient(graph)

        # Partial clustering - should be between 0 and 1
        assert 0.0 <= clustering <= 1.0


class TestIdentifyCoordinationPatterns:
    """Tests for identifying coordination patterns in interaction graphs."""

    def test_identify_coordination_patterns_hub_and_spoke(self):
        """Test identification of hub-and-spoke coordination pattern."""
        interactions = [
            {"source": "coordinator", "target": "agent1", "timestamp": 100.0, "type": "assign"},
            {"source": "coordinator", "target": "agent2", "timestamp": 101.0, "type": "assign"},
            {"source": "coordinator", "target": "agent3", "timestamp": 102.0, "type": "assign"},
            {"source": "agent1", "target": "coordinator", "timestamp": 103.0, "type": "report"},
            {"source": "agent2", "target": "coordinator", "timestamp": 104.0, "type": "report"},
        ]
        graph = build_interaction_graph(interactions)
        patterns = identify_coordination_patterns(graph)

        assert isinstance(patterns, dict)
        assert "pattern_type" in patterns
        assert patterns["pattern_type"] == "hub_and_spoke"
        assert "hub_nodes" in patterns
        assert "coordinator" in patterns["hub_nodes"]

    def test_identify_coordination_patterns_mesh(self):
        """Test identification of mesh/peer-to-peer coordination pattern."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent2", "target": "agent3", "timestamp": 101.0, "type": "message"},
            {"source": "agent3", "target": "agent1", "timestamp": 102.0, "type": "message"},
            {"source": "agent1", "target": "agent3", "timestamp": 103.0, "type": "message"},
            {"source": "agent2", "target": "agent1", "timestamp": 104.0, "type": "message"},
            {"source": "agent3", "target": "agent2", "timestamp": 105.0, "type": "message"},
        ]
        graph = build_interaction_graph(interactions)
        patterns = identify_coordination_patterns(graph)

        assert patterns["pattern_type"] == "mesh"

    def test_identify_coordination_patterns_hierarchical(self):
        """Test identification of hierarchical coordination pattern."""
        interactions = [
            {"source": "manager", "target": "supervisor1", "timestamp": 100.0, "type": "assign"},
            {"source": "manager", "target": "supervisor2", "timestamp": 101.0, "type": "assign"},
            {"source": "supervisor1", "target": "worker1", "timestamp": 102.0, "type": "assign"},
            {"source": "supervisor1", "target": "worker2", "timestamp": 103.0, "type": "assign"},
            {"source": "supervisor2", "target": "worker3", "timestamp": 104.0, "type": "assign"},
        ]
        graph = build_interaction_graph(interactions)
        patterns = identify_coordination_patterns(graph)

        assert patterns["pattern_type"] in ["hierarchical", "hub_and_spoke"]
        # Hierarchical should have multiple levels
        if patterns["pattern_type"] == "hierarchical":
            assert "levels" in patterns or "hub_nodes" in patterns


class TestExportToJson:
    """Tests for exporting graph data to JSON format."""

    def test_export_to_json_basic(self):
        """Test basic JSON export of graph."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent2", "target": "agent3", "timestamp": 101.0, "type": "message"},
        ]
        graph = build_interaction_graph(interactions)
        json_str = export_to_json(graph)

        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 3
        assert len(data["edges"]) == 2

    def test_export_to_json_with_attributes(self):
        """Test JSON export includes node and edge attributes."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
        ]
        graph = build_interaction_graph(interactions)
        json_str = export_to_json(graph)

        data = json.loads(json_str)
        assert "nodes" in data
        # Should have node IDs
        assert any("id" in node or "agent1" in str(node) for node in data["nodes"])

    def test_export_to_json_empty_graph_raises(self):
        """Test that exporting empty graph raises error."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
        ]
        graph = build_interaction_graph(interactions)
        # Create empty graph by removing all nodes
        graph.clear()

        with pytest.raises(ValueError, match="Graph cannot be empty"):
            export_to_json(graph)


class TestExportToGraphML:
    """Tests for exporting graph data to GraphML format."""

    def test_export_to_graphml_basic(self):
        """Test basic GraphML export of graph."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent2", "target": "agent3", "timestamp": 101.0, "type": "message"},
        ]
        graph = build_interaction_graph(interactions)
        graphml_str = export_to_graphml(graph)

        assert isinstance(graphml_str, str)
        assert "<?xml" in graphml_str
        assert "<graphml" in graphml_str
        assert "<node" in graphml_str
        assert "<edge" in graphml_str

    def test_export_to_graphml_contains_node_ids(self):
        """Test GraphML export contains correct node IDs."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
        ]
        graph = build_interaction_graph(interactions)
        graphml_str = export_to_graphml(graph)

        assert "agent1" in graphml_str
        assert "agent2" in graphml_str

    def test_export_to_graphml_empty_graph_raises(self):
        """Test that exporting empty graph raises error."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
        ]
        graph = build_interaction_graph(interactions)
        graph.clear()

        with pytest.raises(ValueError, match="Graph cannot be empty"):
            export_to_graphml(graph)


class TestGraphAnalyzer:
    """Tests for GraphAnalyzer class that combines all graph operations."""

    def test_graph_analyzer_creation(self):
        """Test creating GraphAnalyzer with interaction data."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent2", "target": "agent3", "timestamp": 101.0, "type": "message"},
        ]
        analyzer = GraphAnalyzer(interactions)

        assert analyzer.graph is not None
        assert analyzer.graph.number_of_nodes() == 3
        assert analyzer.graph.number_of_edges() == 2

    def test_graph_analyzer_analyze(self):
        """Test that analyze() returns complete metrics."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent2", "target": "agent3", "timestamp": 101.0, "type": "message"},
            {"source": "agent3", "target": "agent1", "timestamp": 102.0, "type": "message"},
        ]
        analyzer = GraphAnalyzer(interactions)
        metrics = analyzer.analyze()

        assert isinstance(metrics, dict)
        assert "density" in metrics
        assert "centrality" in metrics
        assert "clustering_coefficient" in metrics
        assert "coordination_patterns" in metrics
        assert 0.0 <= metrics["density"] <= 1.0
        assert isinstance(metrics["centrality"], dict)

    def test_graph_analyzer_export_json(self):
        """Test GraphAnalyzer JSON export."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
        ]
        analyzer = GraphAnalyzer(interactions)
        json_str = analyzer.export_json()

        assert isinstance(json_str, str)
        data = json.loads(json_str)
        assert "nodes" in data or "graph" in data

    def test_graph_analyzer_export_graphml(self):
        """Test GraphAnalyzer GraphML export."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
        ]
        analyzer = GraphAnalyzer(interactions)
        graphml_str = analyzer.export_graphml()

        assert isinstance(graphml_str, str)
        assert "<?xml" in graphml_str or "<graphml" in graphml_str

    def test_graph_analyzer_get_metrics_dict(self):
        """Test that metrics can be converted to dict for JSON serialization."""
        interactions = [
            {"source": "agent1", "target": "agent2", "timestamp": 100.0, "type": "message"},
            {"source": "agent2", "target": "agent1", "timestamp": 101.0, "type": "response"},
        ]
        analyzer = GraphAnalyzer(interactions)
        metrics = analyzer.analyze()

        # Should be serializable to JSON
        json_str = json.dumps(metrics)
        parsed = json.loads(json_str)

        assert "density" in parsed
        assert "centrality" in parsed
        assert "clustering_coefficient" in parsed
        assert "coordination_patterns" in parsed
