"""Tests for graph-based complexity analysis.

Following TDD RED phase - these tests should FAIL until implementation is complete.
"""

import json

import pytest


class TestGraphConstruction:
    """Test modeling agent interactions as graph structures."""

    def test_create_interaction_graph_from_edges(self):
        """Test creating a graph from agent interaction edges."""
        from agenteval.metrics.graph import InteractionGraph

        graph = InteractionGraph()

        # Add agent interactions
        graph.add_interaction("agent1", "agent2", weight=1.0)
        graph.add_interaction("agent2", "agent3", weight=1.5)
        graph.add_interaction("agent1", "agent3", weight=0.5)

        # Should have 3 nodes
        assert graph.node_count() == 3
        # Should have 3 edges
        assert graph.edge_count() == 3

    def test_create_interaction_graph_from_dict(self):
        """Test creating graph from interaction dictionary."""
        from agenteval.metrics.graph import InteractionGraph

        interactions = {
            ("agent1", "agent2"): {"weight": 1.0, "message_count": 5},
            ("agent2", "agent3"): {"weight": 2.0, "message_count": 10},
        }

        graph = InteractionGraph.from_interactions(interactions)

        assert graph.node_count() == 3
        assert graph.edge_count() == 2

    def test_graph_handles_self_loops(self):
        """Test graph can handle self-loops (agent interacting with itself)."""
        from agenteval.metrics.graph import InteractionGraph

        graph = InteractionGraph()
        graph.add_interaction("agent1", "agent1", weight=0.5)

        assert graph.node_count() == 1
        assert graph.edge_count() == 1


class TestComplexityMetrics:
    """Test calculation of complexity metrics from interaction graphs."""

    def test_calculate_graph_density(self):
        """Test graph density metric calculation."""
        from agenteval.metrics.graph import ComplexityAnalyzer

        analyzer = ComplexityAnalyzer()

        # Create a simple graph with 3 nodes and 2 edges
        # Density = edges / max_possible_edges = 2 / 3 = 0.667
        from agenteval.metrics.graph import InteractionGraph
        graph = InteractionGraph()
        graph.add_interaction("agent1", "agent2")
        graph.add_interaction("agent2", "agent3")

        result = analyzer.calculate_density(graph)

        assert "density" in result
        assert 0.0 <= result["density"] <= 1.0
        assert result["density"] == pytest.approx(0.667, rel=0.01)

    def test_calculate_degree_centrality(self):
        """Test degree centrality metric calculation."""
        from agenteval.metrics.graph import ComplexityAnalyzer

        analyzer = ComplexityAnalyzer()

        # Create a star graph with agent1 at center
        from agenteval.metrics.graph import InteractionGraph
        graph = InteractionGraph()
        graph.add_interaction("agent1", "agent2")
        graph.add_interaction("agent1", "agent3")
        graph.add_interaction("agent1", "agent4")

        result = analyzer.calculate_degree_centrality(graph)

        assert "degree_centrality" in result
        # agent1 should have highest centrality
        assert result["degree_centrality"]["agent1"] > result["degree_centrality"]["agent2"]

    def test_calculate_betweenness_centrality(self):
        """Test betweenness centrality metric calculation."""
        from agenteval.metrics.graph import ComplexityAnalyzer

        analyzer = ComplexityAnalyzer()

        # Create a path graph: agent1 -> agent2 -> agent3
        # agent2 should have high betweenness (it's on the path between agent1 and agent3)
        from agenteval.metrics.graph import InteractionGraph
        graph = InteractionGraph()
        graph.add_interaction("agent1", "agent2")
        graph.add_interaction("agent2", "agent3")

        result = analyzer.calculate_betweenness_centrality(graph)

        assert "betweenness_centrality" in result
        # agent2 should have highest betweenness (it connects others)
        assert result["betweenness_centrality"]["agent2"] > 0

    def test_calculate_clustering_coefficient(self):
        """Test clustering coefficient metric calculation."""
        from agenteval.metrics.graph import ComplexityAnalyzer

        analyzer = ComplexityAnalyzer()

        # Create a triangle graph (high clustering)
        from agenteval.metrics.graph import InteractionGraph
        graph = InteractionGraph()
        graph.add_interaction("agent1", "agent2")
        graph.add_interaction("agent2", "agent3")
        graph.add_interaction("agent3", "agent1")

        result = analyzer.calculate_clustering_coefficient(graph)

        assert "clustering_coefficient" in result
        assert 0.0 <= result["clustering_coefficient"] <= 1.0
        # Triangle graph should have high clustering (close to 1.0)
        assert result["clustering_coefficient"] > 0.8

    def test_calculate_all_complexity_metrics(self):
        """Test calculating all complexity metrics at once."""
        from agenteval.metrics.graph import ComplexityAnalyzer

        analyzer = ComplexityAnalyzer()

        from agenteval.metrics.graph import InteractionGraph
        graph = InteractionGraph()
        graph.add_interaction("agent1", "agent2")
        graph.add_interaction("agent2", "agent3")
        graph.add_interaction("agent3", "agent1")

        result = analyzer.calculate_all_metrics(graph)

        assert "density" in result
        assert "degree_centrality" in result
        assert "betweenness_centrality" in result
        assert "clustering_coefficient" in result


class TestCoordinationPatterns:
    """Test identification of coordination patterns between agents."""

    def test_identify_hub_agents(self):
        """Test identifying hub agents (highly connected nodes)."""
        from agenteval.metrics.graph import PatternDetector

        detector = PatternDetector()

        # Create a star graph with agent1 as hub
        from agenteval.metrics.graph import InteractionGraph
        graph = InteractionGraph()
        graph.add_interaction("agent1", "agent2")
        graph.add_interaction("agent1", "agent3")
        graph.add_interaction("agent1", "agent4")
        graph.add_interaction("agent2", "agent3")

        result = detector.identify_hub_agents(graph, threshold=2)

        assert "hub_agents" in result
        assert "agent1" in result["hub_agents"]

    def test_identify_communities(self):
        """Test identifying communities (clusters of agents)."""
        from agenteval.metrics.graph import PatternDetector

        detector = PatternDetector()

        # Create two separate communities
        from agenteval.metrics.graph import InteractionGraph
        graph = InteractionGraph()
        # Community 1
        graph.add_interaction("agent1", "agent2")
        graph.add_interaction("agent2", "agent3")
        # Community 2
        graph.add_interaction("agent4", "agent5")
        graph.add_interaction("agent5", "agent6")

        result = detector.identify_communities(graph)

        assert "num_communities" in result
        assert result["num_communities"] >= 2

    def test_detect_coordination_bottlenecks(self):
        """Test detecting bottleneck agents (critical for coordination)."""
        from agenteval.metrics.graph import PatternDetector

        detector = PatternDetector()

        # Create a graph with agent2 as bottleneck
        from agenteval.metrics.graph import InteractionGraph
        graph = InteractionGraph()
        graph.add_interaction("agent1", "agent2")
        graph.add_interaction("agent2", "agent3")
        graph.add_interaction("agent2", "agent4")

        result = detector.detect_bottlenecks(graph)

        assert "bottleneck_agents" in result
        assert "agent2" in result["bottleneck_agents"]


class TestGraphExport:
    """Test export of graph data for external analysis."""

    def test_export_to_json(self):
        """Test exporting graph to JSON format."""
        from agenteval.metrics.graph import InteractionGraph

        graph = InteractionGraph()
        graph.add_interaction("agent1", "agent2", weight=1.0)
        graph.add_interaction("agent2", "agent3", weight=2.0)

        json_data = graph.export_json()

        # Should be valid JSON
        parsed = json.loads(json_data)
        assert "nodes" in parsed
        assert "edges" in parsed
        assert len(parsed["nodes"]) == 3
        assert len(parsed["edges"]) == 2

    def test_export_to_graphml(self):
        """Test exporting graph to GraphML format."""
        from agenteval.metrics.graph import InteractionGraph

        graph = InteractionGraph()
        graph.add_interaction("agent1", "agent2", weight=1.0)
        graph.add_interaction("agent2", "agent3", weight=2.0)

        graphml_data = graph.export_graphml()

        # Should be valid GraphML (XML format)
        assert graphml_data.startswith('<?xml version')
        assert '<graphml' in graphml_data
        assert '</graphml>' in graphml_data

    def test_export_includes_edge_attributes(self):
        """Test export includes edge attributes like weight."""
        from agenteval.metrics.graph import InteractionGraph

        graph = InteractionGraph()
        graph.add_interaction("agent1", "agent2", weight=1.5, label="message")

        json_data = graph.export_json()
        parsed = json.loads(json_data)

        # Should include edge attributes
        assert any(
            edge.get("weight") == 1.5
            for edge in parsed["edges"]
        )


class TestGraphMetricsIntegration:
    """Test integration of graph metrics with NetworkX."""

    def test_uses_networkx_library(self):
        """Test that implementation uses NetworkX as specified."""
        from agenteval.metrics.graph import InteractionGraph

        graph = InteractionGraph()
        graph.add_interaction("agent1", "agent2")

        # Should have NetworkX graph internally
        nx_graph = graph.get_networkx_graph()

        # Verify it's a NetworkX graph
        import networkx as nx
        assert isinstance(nx_graph, (nx.Graph, nx.DiGraph))

    def test_directed_vs_undirected_graphs(self):
        """Test support for both directed and undirected graphs."""
        from agenteval.metrics.graph import InteractionGraph

        # Directed graph (default for agent interactions)
        directed_graph = InteractionGraph(directed=True)
        directed_graph.add_interaction("agent1", "agent2")

        # Undirected graph
        undirected_graph = InteractionGraph(directed=False)
        undirected_graph.add_interaction("agent1", "agent2")

        assert directed_graph.is_directed()
        assert not undirected_graph.is_directed()
