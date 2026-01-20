"""Tests for graph complexity analyzer.

Following TDD RED phase - these tests should FAIL until implementation is complete.
Tests validate graph modeling, complexity metrics, coordination pattern identification,
and export functionality for agent interactions.
"""

import json

import pytest


class TestGraphComplexityAnalyzer:
    """Test GraphComplexityAnalyzer functionality for graph-based metrics."""

    def test_analyzer_initialization(self):
        """Test GraphComplexityAnalyzer can be initialized."""
        from agenteval.metrics.graph import GraphComplexityAnalyzer

        analyzer = GraphComplexityAnalyzer()
        assert analyzer is not None

    def test_analyzer_models_agent_interactions_as_graph(self):
        """Test analyzer models agent interactions as graph structures using NetworkX."""
        from agenteval.metrics.graph import AgentInteraction, GraphComplexityAnalyzer

        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent1",
                to_agent="agent2",
                interaction_type="message",
                timestamp="2024-01-01T10:00:00",
            ),
            AgentInteraction(
                from_agent="agent2",
                to_agent="agent3",
                interaction_type="task_delegation",
                timestamp="2024-01-01T10:01:00",
            ),
        ]

        graph = analyzer.build_graph(interactions)

        # Verify graph structure
        assert graph is not None
        assert len(list(graph.nodes())) == 3  # 3 unique agents
        assert len(list(graph.edges())) == 2  # 2 interactions

    def test_analyzer_calculates_density_metric(self):
        """Test analyzer calculates density metric from interaction graph."""
        from agenteval.metrics.graph import AgentInteraction, GraphComplexityAnalyzer

        analyzer = GraphComplexityAnalyzer()

        # Complete graph: 3 agents with all possible interactions
        interactions = [
            AgentInteraction(
                from_agent="agent1",
                to_agent="agent2",
                interaction_type="message",
                timestamp="2024-01-01T10:00:00",
            ),
            AgentInteraction(
                from_agent="agent1",
                to_agent="agent3",
                interaction_type="message",
                timestamp="2024-01-01T10:01:00",
            ),
            AgentInteraction(
                from_agent="agent2",
                to_agent="agent1",
                interaction_type="message",
                timestamp="2024-01-01T10:02:00",
            ),
            AgentInteraction(
                from_agent="agent2",
                to_agent="agent3",
                interaction_type="message",
                timestamp="2024-01-01T10:03:00",
            ),
            AgentInteraction(
                from_agent="agent3",
                to_agent="agent1",
                interaction_type="message",
                timestamp="2024-01-01T10:04:00",
            ),
            AgentInteraction(
                from_agent="agent3",
                to_agent="agent2",
                interaction_type="message",
                timestamp="2024-01-01T10:05:00",
            ),
        ]

        metrics = analyzer.calculate_metrics(interactions)

        # Density should be 1.0 for complete graph
        assert metrics.density == pytest.approx(1.0, abs=0.01)

    def test_analyzer_calculates_centrality_metrics(self):
        """Test analyzer calculates centrality metrics from interaction graph."""
        from agenteval.metrics.graph import AgentInteraction, GraphComplexityAnalyzer

        analyzer = GraphComplexityAnalyzer()

        # Hub-and-spoke pattern: agent1 interacts with all others
        interactions = [
            AgentInteraction(
                from_agent="agent1",
                to_agent="agent2",
                interaction_type="message",
                timestamp="2024-01-01T10:00:00",
            ),
            AgentInteraction(
                from_agent="agent1",
                to_agent="agent3",
                interaction_type="message",
                timestamp="2024-01-01T10:01:00",
            ),
            AgentInteraction(
                from_agent="agent1",
                to_agent="agent4",
                interaction_type="message",
                timestamp="2024-01-01T10:02:00",
            ),
        ]

        metrics = analyzer.calculate_metrics(interactions)

        # Verify centrality metrics are calculated
        assert metrics.avg_betweenness_centrality >= 0.0
        assert metrics.avg_betweenness_centrality <= 1.0

    def test_analyzer_calculates_clustering_coefficient(self):
        """Test analyzer calculates clustering coefficient from interaction graph."""
        from agenteval.metrics.graph import AgentInteraction, GraphComplexityAnalyzer

        analyzer = GraphComplexityAnalyzer()

        # Triangle pattern: all agents interact with each other
        interactions = [
            AgentInteraction(
                from_agent="agent1",
                to_agent="agent2",
                interaction_type="message",
                timestamp="2024-01-01T10:00:00",
            ),
            AgentInteraction(
                from_agent="agent2",
                to_agent="agent3",
                interaction_type="message",
                timestamp="2024-01-01T10:01:00",
            ),
            AgentInteraction(
                from_agent="agent3",
                to_agent="agent1",
                interaction_type="message",
                timestamp="2024-01-01T10:02:00",
            ),
        ]

        metrics = analyzer.calculate_metrics(interactions)

        # Triangle should have high clustering coefficient
        assert metrics.avg_clustering_coefficient >= 0.0
        assert metrics.avg_clustering_coefficient <= 1.0

    def test_analyzer_identifies_coordination_patterns(self):
        """Test analyzer identifies coordination patterns between agents."""
        from agenteval.metrics.graph import AgentInteraction, GraphComplexityAnalyzer

        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent1",
                to_agent="agent2",
                interaction_type="message",
                timestamp="2024-01-01T10:00:00",
            ),
            AgentInteraction(
                from_agent="agent2",
                to_agent="agent1",
                interaction_type="message",
                timestamp="2024-01-01T10:01:00",
            ),
            AgentInteraction(
                from_agent="agent1",
                to_agent="agent3",
                interaction_type="message",
                timestamp="2024-01-01T10:02:00",
            ),
        ]

        patterns = analyzer.identify_coordination_patterns(interactions)

        # Should identify patterns
        assert isinstance(patterns, dict)
        assert "bidirectional_pairs" in patterns or "hub_agents" in patterns

    def test_analyzer_exports_graph_to_json(self):
        """Test analyzer exports graph data in JSON format for external analysis."""
        from agenteval.metrics.graph import AgentInteraction, GraphComplexityAnalyzer

        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent1",
                to_agent="agent2",
                interaction_type="message",
                timestamp="2024-01-01T10:00:00",
            ),
        ]

        graph = analyzer.build_graph(interactions)
        json_output = analyzer.export_to_json(graph)

        # Verify valid JSON
        parsed = json.loads(json_output)
        assert "nodes" in parsed
        assert "edges" in parsed
        assert len(parsed["nodes"]) == 2
        assert len(parsed["edges"]) == 1

    def test_analyzer_exports_graph_to_graphml(self):
        """Test analyzer exports graph data in GraphML format for external analysis."""
        from agenteval.metrics.graph import AgentInteraction, GraphComplexityAnalyzer

        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent1",
                to_agent="agent2",
                interaction_type="message",
                timestamp="2024-01-01T10:00:00",
            ),
        ]

        graph = analyzer.build_graph(interactions)
        graphml_output = analyzer.export_to_graphml(graph)

        # Verify valid GraphML (should contain XML tags)
        assert "<?xml" in graphml_output
        assert "<graphml" in graphml_output
        assert "</graphml>" in graphml_output

    def test_analyzer_uses_mock_interaction_data(self):
        """Test analyzer uses mock/sample interaction data for testing."""
        from agenteval.metrics.graph import AgentInteraction, GraphComplexityAnalyzer

        analyzer = GraphComplexityAnalyzer()

        # Mock interaction data
        mock_interactions = [
            AgentInteraction(
                from_agent="mock_agent1",
                to_agent="mock_agent2",
                interaction_type="mock_message",
                timestamp="2024-01-01T10:00:00",
                metadata={"test": "data"},
            ),
        ]

        graph = analyzer.build_graph(mock_interactions)

        assert len(list(graph.nodes())) == 2

    def test_analyzer_handles_empty_interactions(self):
        """Test analyzer handles empty interactions list."""
        from agenteval.metrics.graph import GraphComplexityAnalyzer

        analyzer = GraphComplexityAnalyzer()

        metrics = analyzer.calculate_metrics([])

        assert metrics.density == 0.0
        assert metrics.num_nodes == 0
        assert metrics.num_edges == 0

    def test_analyzer_calculates_all_required_metrics(self):
        """Test analyzer calculates all required complexity metrics."""
        from agenteval.metrics.graph import AgentInteraction, GraphComplexityAnalyzer

        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent1",
                to_agent="agent2",
                interaction_type="message",
                timestamp="2024-01-01T10:00:00",
            ),
            AgentInteraction(
                from_agent="agent2",
                to_agent="agent3",
                interaction_type="message",
                timestamp="2024-01-01T10:01:00",
            ),
        ]

        metrics = analyzer.calculate_metrics(interactions)

        # Verify all metrics are present
        assert hasattr(metrics, "density")
        assert hasattr(metrics, "avg_clustering_coefficient")
        assert hasattr(metrics, "avg_betweenness_centrality")
        assert hasattr(metrics, "num_nodes")
        assert hasattr(metrics, "num_edges")


class TestAgentInteractionModel:
    """Test AgentInteraction Pydantic model."""

    def test_agent_interaction_model_creation(self):
        """Test AgentInteraction model can be created with required fields."""
        from agenteval.metrics.graph import AgentInteraction

        interaction = AgentInteraction(
            from_agent="agent1",
            to_agent="agent2",
            interaction_type="message",
            timestamp="2024-01-01T10:00:00",
        )

        assert interaction.from_agent == "agent1"
        assert interaction.to_agent == "agent2"
        assert interaction.interaction_type == "message"
        assert interaction.timestamp == "2024-01-01T10:00:00"

    def test_agent_interaction_model_with_metadata(self):
        """Test AgentInteraction model supports optional metadata."""
        from agenteval.metrics.graph import AgentInteraction

        interaction = AgentInteraction(
            from_agent="agent1",
            to_agent="agent2",
            interaction_type="message",
            timestamp="2024-01-01T10:00:00",
            metadata={"priority": "high", "content": "test message"},
        )

        assert interaction.metadata is not None
        assert interaction.metadata["priority"] == "high"


class TestGraphMetricsModel:
    """Test GraphMetrics Pydantic model."""

    def test_graph_metrics_model_creation(self):
        """Test GraphMetrics model can be created with valid values."""
        from agenteval.metrics.graph import GraphMetrics

        metrics = GraphMetrics(
            density=0.75,
            avg_clustering_coefficient=0.6,
            avg_betweenness_centrality=0.4,
            num_nodes=5,
            num_edges=8,
        )

        assert metrics.density == 0.75
        assert metrics.avg_clustering_coefficient == 0.6
        assert metrics.avg_betweenness_centrality == 0.4
        assert metrics.num_nodes == 5
        assert metrics.num_edges == 8

    def test_graph_metrics_validates_density_range(self):
        """Test GraphMetrics validates density is between 0 and 1."""
        from agenteval.metrics.graph import GraphMetrics

        with pytest.raises(Exception):  # ValidationError
            GraphMetrics(
                density=1.5,
                avg_clustering_coefficient=0.6,
                avg_betweenness_centrality=0.4,
                num_nodes=5,
                num_edges=8,
            )

    def test_graph_metrics_validates_clustering_coefficient_range(self):
        """Test GraphMetrics validates clustering coefficient is between 0 and 1."""
        from agenteval.metrics.graph import GraphMetrics

        with pytest.raises(Exception):  # ValidationError
            GraphMetrics(
                density=0.75,
                avg_clustering_coefficient=1.5,
                avg_betweenness_centrality=0.4,
                num_nodes=5,
                num_edges=8,
            )

    def test_graph_metrics_model_dumps_to_json(self):
        """Test GraphMetrics can be dumped to JSON."""
        from agenteval.metrics.graph import GraphMetrics

        metrics = GraphMetrics(
            density=0.75,
            avg_clustering_coefficient=0.6,
            avg_betweenness_centrality=0.4,
            num_nodes=5,
            num_edges=8,
        )

        json_output = metrics.model_dump_json()

        assert isinstance(json_output, str)
        assert "density" in json_output
        assert "avg_clustering_coefficient" in json_output
