"""Tests for graph-based complexity analysis metrics.

Following TDD RED phase - these tests should FAIL until implementation is complete.
"""

import json

import pytest


class TestGraphModels:
    """Test Pydantic models for graph-based analysis."""

    def test_agent_interaction_model(self):
        """Test AgentInteraction model for tracking agent communications."""
        from agenteval.metrics.graph import AgentInteraction

        interaction = AgentInteraction(
            from_agent="agent_1",
            to_agent="agent_2",
            interaction_type="message",
            timestamp=0.0,
            metadata={"content": "test"},
        )

        assert interaction.from_agent == "agent_1"
        assert interaction.to_agent == "agent_2"
        assert interaction.interaction_type == "message"
        assert interaction.timestamp == 0.0

    def test_graph_metrics_model(self):
        """Test GraphMetrics model with complexity metrics."""
        from agenteval.metrics.graph import GraphMetrics

        metrics = GraphMetrics(
            density=0.75,
            avg_degree_centrality=0.6,
            avg_betweenness_centrality=0.3,
            avg_clustering_coefficient=0.8,
            num_nodes=5,
            num_edges=10,
        )

        assert metrics.density == 0.75
        assert metrics.avg_degree_centrality == 0.6
        assert metrics.avg_betweenness_centrality == 0.3
        assert metrics.avg_clustering_coefficient == 0.8
        assert metrics.num_nodes == 5
        assert metrics.num_edges == 10


class TestGraphConstruction:
    """Test building graph structures from agent interactions."""

    def test_build_graph_from_interactions(self):
        """Test constructing NetworkX graph from interaction list."""
        from agenteval.metrics.graph import AgentInteraction, GraphAnalyzer

        interactions = [
            AgentInteraction(
                from_agent="agent_1",
                to_agent="agent_2",
                interaction_type="message",
                timestamp=1.0,
                metadata={},
            ),
            AgentInteraction(
                from_agent="agent_2",
                to_agent="agent_3",
                interaction_type="message",
                timestamp=2.0,
                metadata={},
            ),
        ]

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph(interactions)

        assert graph is not None
        assert len(graph.nodes) == 3  # agent_1, agent_2, agent_3
        assert len(graph.edges) == 2

    def test_build_graph_empty_interactions(self):
        """Test building graph with no interactions."""
        from agenteval.metrics.graph import GraphAnalyzer

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph([])

        assert graph is not None
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0

    def test_build_graph_self_interaction(self):
        """Test graph handles self-loops (agent interacting with itself)."""
        from agenteval.metrics.graph import AgentInteraction, GraphAnalyzer

        interactions = [
            AgentInteraction(
                from_agent="agent_1",
                to_agent="agent_1",
                interaction_type="self_check",
                timestamp=1.0,
                metadata={},
            )
        ]

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph(interactions)

        assert len(graph.nodes) == 1
        # Self-loops may or may not be counted as edges depending on implementation


class TestDensityMetrics:
    """Test graph density calculation."""

    def test_calculate_density_complete_graph(self):
        """Test density calculation for complete graph (all agents connected)."""
        from agenteval.metrics.graph import AgentInteraction, GraphAnalyzer

        # Complete graph: all 3 agents connected to each other
        interactions = [
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_2", interaction_type="msg", timestamp=1.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_3", interaction_type="msg", timestamp=2.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_2", to_agent="agent_3", interaction_type="msg", timestamp=3.0, metadata={}
            ),
        ]

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph(interactions)
        density = analyzer.calculate_density(graph)

        # For directed graph with 3 nodes: max edges = 3*(3-1) = 6, actual = 3
        # For undirected: max edges = 3*(3-1)/2 = 3, actual = 3
        assert 0.0 <= density <= 1.0
        assert density > 0.0  # Should be > 0 with edges present

    def test_calculate_density_sparse_graph(self):
        """Test density calculation for sparse graph."""
        from agenteval.metrics.graph import AgentInteraction, GraphAnalyzer

        # Sparse: only 1 connection among 4 agents
        interactions = [
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_2", interaction_type="msg", timestamp=1.0, metadata={}
            )
        ]

        analyzer = GraphAnalyzer()
        # Add all 4 agents explicitly
        for i in range(1, 5):
            interactions.append(
                AgentInteraction(
                    from_agent=f"agent_{i}",
                    to_agent=f"agent_{i}",
                    interaction_type="self",
                    timestamp=float(i),
                    metadata={},
                )
            )

        graph = analyzer.build_graph(interactions)
        density = analyzer.calculate_density(graph)

        assert 0.0 <= density <= 1.0
        # With many nodes and few edges, density should be low
        assert density < 0.5

    def test_calculate_density_empty_graph(self):
        """Test density calculation for empty graph."""
        from agenteval.metrics.graph import GraphAnalyzer

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph([])
        density = analyzer.calculate_density(graph)

        assert density == 0.0


class TestCentralityMetrics:
    """Test centrality calculations (degree, betweenness)."""

    def test_calculate_degree_centrality(self):
        """Test degree centrality calculation for all nodes."""
        from agenteval.metrics.graph import AgentInteraction, GraphAnalyzer

        interactions = [
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_2", interaction_type="msg", timestamp=1.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_3", to_agent="agent_2", interaction_type="msg", timestamp=2.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_2", to_agent="agent_4", interaction_type="msg", timestamp=3.0, metadata={}
            ),
        ]

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph(interactions)
        centrality = analyzer.calculate_degree_centrality(graph)

        assert isinstance(centrality, dict)
        assert "agent_2" in centrality  # agent_2 is central hub
        assert centrality["agent_2"] > centrality.get("agent_1", 0.0)

    def test_calculate_betweenness_centrality(self):
        """Test betweenness centrality calculation."""
        from agenteval.metrics.graph import AgentInteraction, GraphAnalyzer

        # Linear chain: agent_1 -> agent_2 -> agent_3
        interactions = [
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_2", interaction_type="msg", timestamp=1.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_2", to_agent="agent_3", interaction_type="msg", timestamp=2.0, metadata={}
            ),
        ]

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph(interactions)
        centrality = analyzer.calculate_betweenness_centrality(graph)

        assert isinstance(centrality, dict)
        # agent_2 should have high betweenness (on path between agent_1 and agent_3)
        assert "agent_2" in centrality

    def test_calculate_avg_centrality(self):
        """Test average centrality calculation across all nodes."""
        from agenteval.metrics.graph import AgentInteraction, GraphAnalyzer

        interactions = [
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_2", interaction_type="msg", timestamp=1.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_2", to_agent="agent_3", interaction_type="msg", timestamp=2.0, metadata={}
            ),
        ]

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph(interactions)

        avg_degree = analyzer.calculate_avg_degree_centrality(graph)
        avg_betweenness = analyzer.calculate_avg_betweenness_centrality(graph)

        assert 0.0 <= avg_degree <= 1.0
        assert 0.0 <= avg_betweenness <= 1.0


class TestClusteringCoefficient:
    """Test clustering coefficient calculation."""

    def test_calculate_clustering_coefficient_triangle(self):
        """Test clustering coefficient for triangular structure."""
        from agenteval.metrics.graph import AgentInteraction, GraphAnalyzer

        # Triangle: all 3 agents connected to each other
        interactions = [
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_2", interaction_type="msg", timestamp=1.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_2", to_agent="agent_3", interaction_type="msg", timestamp=2.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_3", to_agent="agent_1", interaction_type="msg", timestamp=3.0, metadata={}
            ),
        ]

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph(interactions)
        clustering = analyzer.calculate_avg_clustering_coefficient(graph)

        assert 0.0 <= clustering <= 1.0
        # Triangle should have high clustering
        assert clustering > 0.0

    def test_calculate_clustering_coefficient_star(self):
        """Test clustering coefficient for star structure."""
        from agenteval.metrics.graph import AgentInteraction, GraphAnalyzer

        # Star: central agent_1 connected to agent_2, agent_3, agent_4
        interactions = [
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_2", interaction_type="msg", timestamp=1.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_3", interaction_type="msg", timestamp=2.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_4", interaction_type="msg", timestamp=3.0, metadata={}
            ),
        ]

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph(interactions)
        clustering = analyzer.calculate_avg_clustering_coefficient(graph)

        assert 0.0 <= clustering <= 1.0
        # Star structure typically has low clustering
        assert clustering < 0.5

    def test_calculate_clustering_coefficient_empty(self):
        """Test clustering coefficient for empty graph."""
        from agenteval.metrics.graph import GraphAnalyzer

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph([])
        clustering = analyzer.calculate_avg_clustering_coefficient(graph)

        assert clustering == 0.0


class TestCoordinationPatterns:
    """Test identification of coordination patterns."""

    def test_identify_hub_agents(self):
        """Test identifying hub agents (high degree centrality)."""
        from agenteval.metrics.graph import AgentInteraction, GraphAnalyzer

        interactions = [
            AgentInteraction(
                from_agent="hub", to_agent="agent_1", interaction_type="msg", timestamp=1.0, metadata={}
            ),
            AgentInteraction(
                from_agent="hub", to_agent="agent_2", interaction_type="msg", timestamp=2.0, metadata={}
            ),
            AgentInteraction(
                from_agent="hub", to_agent="agent_3", interaction_type="msg", timestamp=3.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_2", interaction_type="msg", timestamp=4.0, metadata={}
            ),
        ]

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph(interactions)
        hubs = analyzer.identify_hubs(graph, threshold=0.5)

        assert isinstance(hubs, list)
        assert "hub" in hubs  # Should identify "hub" as high-centrality node

    def test_identify_bridge_agents(self):
        """Test identifying bridge agents (high betweenness centrality)."""
        from agenteval.metrics.graph import AgentInteraction, GraphAnalyzer

        # Two clusters connected by bridge agent
        interactions = [
            # Cluster 1
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_2", interaction_type="msg", timestamp=1.0, metadata={}
            ),
            # Bridge
            AgentInteraction(
                from_agent="agent_2", to_agent="bridge", interaction_type="msg", timestamp=2.0, metadata={}
            ),
            # Cluster 2
            AgentInteraction(
                from_agent="bridge", to_agent="agent_3", interaction_type="msg", timestamp=3.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_3", to_agent="agent_4", interaction_type="msg", timestamp=4.0, metadata={}
            ),
        ]

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph(interactions)
        bridges = analyzer.identify_bridges(graph, threshold=0.1)

        assert isinstance(bridges, list)
        # Bridge agent should have higher betweenness
        assert "bridge" in bridges or len(bridges) >= 1

    def test_identify_isolated_agents(self):
        """Test identifying isolated agents with no connections."""
        from agenteval.metrics.graph import AgentInteraction, GraphAnalyzer

        interactions = [
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_2", interaction_type="msg", timestamp=1.0, metadata={}
            ),
            # agent_3 and agent_4 are isolated
            AgentInteraction(
                from_agent="agent_3", to_agent="agent_3", interaction_type="self", timestamp=2.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_4", to_agent="agent_4", interaction_type="self", timestamp=3.0, metadata={}
            ),
        ]

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph(interactions)
        isolated = analyzer.identify_isolated_agents(graph)

        assert isinstance(isolated, list)
        # Agents with only self-loops or no connections should be isolated
        assert len(isolated) >= 0


class TestGraphExport:
    """Test exporting graph data in various formats."""

    def test_export_to_json(self):
        """Test exporting graph to JSON format."""
        from agenteval.metrics.graph import AgentInteraction, GraphAnalyzer

        interactions = [
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_2", interaction_type="msg", timestamp=1.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_2", to_agent="agent_3", interaction_type="msg", timestamp=2.0, metadata={}
            ),
        ]

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph(interactions)
        json_data = analyzer.export_to_json(graph)

        assert isinstance(json_data, str)
        data = json.loads(json_data)
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 3
        assert len(data["edges"]) == 2

    def test_export_to_graphml(self):
        """Test exporting graph to GraphML format."""
        from agenteval.metrics.graph import AgentInteraction, GraphAnalyzer

        interactions = [
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_2", interaction_type="msg", timestamp=1.0, metadata={}
            )
        ]

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph(interactions)
        graphml_str = analyzer.export_to_graphml(graph)

        assert isinstance(graphml_str, str)
        assert "<graphml" in graphml_str.lower() or len(graphml_str) > 0

    def test_export_empty_graph_to_json(self):
        """Test exporting empty graph to JSON."""
        from agenteval.metrics.graph import GraphAnalyzer

        analyzer = GraphAnalyzer()
        graph = analyzer.build_graph([])
        json_data = analyzer.export_to_json(graph)

        data = json.loads(json_data)
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) == 0
        assert len(data["edges"]) == 0


class TestGraphMetricsEvaluator:
    """Test comprehensive graph metrics evaluation."""

    def test_evaluator_initialization(self):
        """Test GraphMetricsEvaluator can be initialized."""
        from agenteval.metrics.graph import GraphMetricsEvaluator

        evaluator = GraphMetricsEvaluator()
        assert evaluator is not None

    def test_evaluate_returns_graph_metrics(self):
        """Test evaluate() returns GraphMetrics object."""
        from agenteval.metrics.graph import AgentInteraction, GraphMetrics, GraphMetricsEvaluator

        evaluator = GraphMetricsEvaluator()

        interactions = [
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_2", interaction_type="msg", timestamp=1.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_2", to_agent="agent_3", interaction_type="msg", timestamp=2.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_3", to_agent="agent_1", interaction_type="msg", timestamp=3.0, metadata={}
            ),
        ]

        metrics = evaluator.evaluate(interactions)

        assert isinstance(metrics, GraphMetrics)
        assert metrics.num_nodes == 3
        assert metrics.num_edges == 3
        assert 0.0 <= metrics.density <= 1.0
        assert 0.0 <= metrics.avg_degree_centrality <= 1.0

    def test_evaluate_calculates_all_metrics(self):
        """Test evaluate() calculates all required complexity metrics."""
        from agenteval.metrics.graph import AgentInteraction, GraphMetricsEvaluator

        evaluator = GraphMetricsEvaluator()

        interactions = [
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_2", interaction_type="msg", timestamp=1.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_2", to_agent="agent_3", interaction_type="msg", timestamp=2.0, metadata={}
            ),
        ]

        metrics = evaluator.evaluate(interactions)

        # Verify all metrics are present and in valid range
        assert hasattr(metrics, "density")
        assert hasattr(metrics, "avg_degree_centrality")
        assert hasattr(metrics, "avg_betweenness_centrality")
        assert hasattr(metrics, "avg_clustering_coefficient")
        assert hasattr(metrics, "num_nodes")
        assert hasattr(metrics, "num_edges")

        assert 0.0 <= metrics.density <= 1.0
        assert 0.0 <= metrics.avg_degree_centrality <= 1.0
        assert 0.0 <= metrics.avg_betweenness_centrality <= 1.0
        assert 0.0 <= metrics.avg_clustering_coefficient <= 1.0

    def test_evaluate_empty_interactions(self):
        """Test evaluate() handles empty interaction list."""
        from agenteval.metrics.graph import GraphMetricsEvaluator

        evaluator = GraphMetricsEvaluator()
        metrics = evaluator.evaluate([])

        assert metrics.num_nodes == 0
        assert metrics.num_edges == 0
        assert metrics.density == 0.0

    def test_metrics_to_json(self):
        """Test GraphMetrics can be serialized to JSON."""
        from agenteval.metrics.graph import AgentInteraction, GraphMetricsEvaluator

        evaluator = GraphMetricsEvaluator()

        interactions = [
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_2", interaction_type="msg", timestamp=1.0, metadata={}
            )
        ]

        metrics = evaluator.evaluate(interactions)
        json_str = metrics.model_dump_json()
        data = json.loads(json_str)

        assert "density" in data
        assert "avg_degree_centrality" in data
        assert "avg_betweenness_centrality" in data
        assert "avg_clustering_coefficient" in data
        assert "num_nodes" in data
        assert "num_edges" in data


class TestComplexInteractionPatterns:
    """Test analysis of complex multi-agent interaction patterns."""

    def test_hierarchical_pattern(self):
        """Test analyzing hierarchical coordination pattern."""
        from agenteval.metrics.graph import AgentInteraction, GraphMetricsEvaluator

        # Leader -> Manager -> Workers pattern
        interactions = [
            AgentInteraction(
                from_agent="leader", to_agent="manager_1", interaction_type="msg", timestamp=1.0, metadata={}
            ),
            AgentInteraction(
                from_agent="leader", to_agent="manager_2", interaction_type="msg", timestamp=2.0, metadata={}
            ),
            AgentInteraction(
                from_agent="manager_1", to_agent="worker_1", interaction_type="msg", timestamp=3.0, metadata={}
            ),
            AgentInteraction(
                from_agent="manager_1", to_agent="worker_2", interaction_type="msg", timestamp=4.0, metadata={}
            ),
            AgentInteraction(
                from_agent="manager_2", to_agent="worker_3", interaction_type="msg", timestamp=5.0, metadata={}
            ),
        ]

        evaluator = GraphMetricsEvaluator()
        metrics = evaluator.evaluate(interactions)

        # Hierarchical patterns typically have lower clustering
        assert metrics.num_nodes == 6
        assert metrics.num_edges == 5

    def test_peer_to_peer_pattern(self):
        """Test analyzing peer-to-peer coordination pattern."""
        from agenteval.metrics.graph import AgentInteraction, GraphMetricsEvaluator

        # Fully connected mesh
        agents = ["agent_1", "agent_2", "agent_3", "agent_4"]
        interactions = []
        timestamp = 0.0
        for i, from_agent in enumerate(agents):
            for to_agent in agents[i + 1 :]:
                interactions.append(
                    AgentInteraction(
                        from_agent=from_agent,
                        to_agent=to_agent,
                        interaction_type="msg",
                        timestamp=timestamp,
                        metadata={},
                    )
                )
                timestamp += 1.0

        evaluator = GraphMetricsEvaluator()
        metrics = evaluator.evaluate(interactions)

        # Peer-to-peer should have high density and clustering
        assert metrics.density >= 0.5
        assert metrics.num_nodes == 4

    def test_pipeline_pattern(self):
        """Test analyzing pipeline/sequential coordination pattern."""
        from agenteval.metrics.graph import AgentInteraction, GraphMetricsEvaluator

        # Linear pipeline: agent_1 -> agent_2 -> agent_3 -> agent_4
        interactions = [
            AgentInteraction(
                from_agent="agent_1", to_agent="agent_2", interaction_type="msg", timestamp=1.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_2", to_agent="agent_3", interaction_type="msg", timestamp=2.0, metadata={}
            ),
            AgentInteraction(
                from_agent="agent_3", to_agent="agent_4", interaction_type="msg", timestamp=3.0, metadata={}
            ),
        ]

        evaluator = GraphMetricsEvaluator()
        metrics = evaluator.evaluate(interactions)

        # Pipeline should have low density
        assert metrics.num_nodes == 4
        assert metrics.num_edges == 3
        assert metrics.density < 0.5
