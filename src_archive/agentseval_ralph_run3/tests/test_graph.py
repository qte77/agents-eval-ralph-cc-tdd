"""Tests for Graph Complexity Analyzer.

Following TDD RED phase - these tests should FAIL until implementation is complete.
Tests validate graph-based structural analysis of agent interactions to understand
coordination complexity.
"""

import json

import networkx as nx
import pytest
from agenteval.metrics.graph import (
    AgentInteraction,
    GraphComplexityAnalyzer,
    GraphMetrics,
)


class TestAgentInteraction:
    """Test AgentInteraction Pydantic model."""

    def test_agent_interaction_model(self):
        """Test AgentInteraction model has required fields."""
        interaction = AgentInteraction(
            from_agent="agent_001",
            to_agent="agent_002",
            interaction_type="message",
            timestamp="2026-01-19T10:00:00Z",
            metadata={"message_id": "msg_001"},
        )
        assert interaction.from_agent == "agent_001"
        assert interaction.to_agent == "agent_002"
        assert interaction.interaction_type == "message"
        assert interaction.timestamp == "2026-01-19T10:00:00Z"
        assert interaction.metadata["message_id"] == "msg_001"

    def test_agent_interaction_without_metadata(self):
        """Test AgentInteraction model without optional metadata."""
        interaction = AgentInteraction(
            from_agent="agent_001",
            to_agent="agent_002",
            interaction_type="task_assignment",
            timestamp="2026-01-19T10:00:00Z",
        )
        assert interaction.from_agent == "agent_001"
        assert interaction.to_agent == "agent_002"
        assert interaction.metadata is None


class TestGraphMetrics:
    """Test GraphMetrics Pydantic model."""

    def test_graph_metrics_model(self):
        """Test GraphMetrics model has required fields."""
        metrics = GraphMetrics(
            density=0.75,
            avg_clustering_coefficient=0.65,
            avg_betweenness_centrality=0.45,
            avg_closeness_centrality=0.55,
            num_nodes=5,
            num_edges=8,
        )
        assert metrics.density == 0.75
        assert metrics.avg_clustering_coefficient == 0.65
        assert metrics.avg_betweenness_centrality == 0.45
        assert metrics.avg_closeness_centrality == 0.55
        assert metrics.num_nodes == 5
        assert metrics.num_edges == 8

    def test_graph_metrics_validation(self):
        """Test GraphMetrics validates metric values are between 0 and 1."""
        with pytest.raises(ValueError):
            GraphMetrics(
                density=1.5,  # Invalid: > 1.0
                avg_clustering_coefficient=0.5,
                avg_betweenness_centrality=0.5,
                avg_closeness_centrality=0.5,
                num_nodes=5,
                num_edges=8,
            )


class TestGraphComplexityAnalyzer:
    """Test Graph Complexity Analyzer functionality."""

    def test_analyzer_initialization(self):
        """Test GraphComplexityAnalyzer can be initialized."""
        analyzer = GraphComplexityAnalyzer()
        assert isinstance(analyzer, GraphComplexityAnalyzer)

    def test_build_graph_from_interactions(self):
        """Test building a NetworkX graph from agent interactions."""
        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent_001",
                to_agent="agent_002",
                interaction_type="message",
                timestamp="2026-01-19T10:00:00Z",
            ),
            AgentInteraction(
                from_agent="agent_002",
                to_agent="agent_003",
                interaction_type="task_assignment",
                timestamp="2026-01-19T10:01:00Z",
            ),
        ]

        graph = analyzer.build_graph(interactions)

        assert isinstance(graph, nx.DiGraph)
        assert graph.number_of_nodes() == 3
        assert graph.number_of_edges() == 2
        assert graph.has_edge("agent_001", "agent_002")
        assert graph.has_edge("agent_002", "agent_003")

    def test_build_graph_empty_interactions(self):
        """Test building graph with no interactions."""
        analyzer = GraphComplexityAnalyzer()

        graph = analyzer.build_graph([])

        assert isinstance(graph, nx.DiGraph)
        assert graph.number_of_nodes() == 0
        assert graph.number_of_edges() == 0

    def test_calculate_density(self):
        """Test calculating graph density metric."""
        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent_001",
                to_agent="agent_002",
                interaction_type="message",
                timestamp="2026-01-19T10:00:00Z",
            ),
            AgentInteraction(
                from_agent="agent_002",
                to_agent="agent_003",
                interaction_type="message",
                timestamp="2026-01-19T10:01:00Z",
            ),
            AgentInteraction(
                from_agent="agent_001",
                to_agent="agent_003",
                interaction_type="message",
                timestamp="2026-01-19T10:02:00Z",
            ),
        ]

        graph = analyzer.build_graph(interactions)
        density = analyzer.calculate_density(graph)

        assert isinstance(density, float)
        assert 0.0 <= density <= 1.0

    def test_calculate_clustering_coefficient(self):
        """Test calculating average clustering coefficient."""
        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent_001",
                to_agent="agent_002",
                interaction_type="message",
                timestamp="2026-01-19T10:00:00Z",
            ),
            AgentInteraction(
                from_agent="agent_002",
                to_agent="agent_003",
                interaction_type="message",
                timestamp="2026-01-19T10:01:00Z",
            ),
        ]

        graph = analyzer.build_graph(interactions)
        clustering = analyzer.calculate_clustering_coefficient(graph)

        assert isinstance(clustering, float)
        assert 0.0 <= clustering <= 1.0

    def test_calculate_centrality_metrics(self):
        """Test calculating centrality metrics (betweenness and closeness)."""
        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent_001",
                to_agent="agent_002",
                interaction_type="message",
                timestamp="2026-01-19T10:00:00Z",
            ),
            AgentInteraction(
                from_agent="agent_002",
                to_agent="agent_003",
                interaction_type="message",
                timestamp="2026-01-19T10:01:00Z",
            ),
            AgentInteraction(
                from_agent="agent_003",
                to_agent="agent_004",
                interaction_type="message",
                timestamp="2026-01-19T10:02:00Z",
            ),
        ]

        graph = analyzer.build_graph(interactions)
        betweenness = analyzer.calculate_betweenness_centrality(graph)
        closeness = analyzer.calculate_closeness_centrality(graph)

        assert isinstance(betweenness, float)
        assert isinstance(closeness, float)
        assert 0.0 <= betweenness <= 1.0
        assert 0.0 <= closeness <= 1.0

    def test_calculate_graph_metrics_returns_model(self):
        """Test calculate_metrics returns GraphMetrics Pydantic model."""
        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent_001",
                to_agent="agent_002",
                interaction_type="message",
                timestamp="2026-01-19T10:00:00Z",
            ),
            AgentInteraction(
                from_agent="agent_002",
                to_agent="agent_003",
                interaction_type="message",
                timestamp="2026-01-19T10:01:00Z",
            ),
        ]

        metrics = analyzer.calculate_metrics(interactions)

        assert isinstance(metrics, GraphMetrics)
        assert 0.0 <= metrics.density <= 1.0
        assert 0.0 <= metrics.avg_clustering_coefficient <= 1.0
        assert 0.0 <= metrics.avg_betweenness_centrality <= 1.0
        assert 0.0 <= metrics.avg_closeness_centrality <= 1.0
        assert metrics.num_nodes == 3
        assert metrics.num_edges == 2

    def test_identify_coordination_patterns(self):
        """Test identifying coordination patterns between agents."""
        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent_001",
                to_agent="agent_002",
                interaction_type="message",
                timestamp="2026-01-19T10:00:00Z",
            ),
            AgentInteraction(
                from_agent="agent_002",
                to_agent="agent_001",
                interaction_type="message",
                timestamp="2026-01-19T10:01:00Z",
            ),
            AgentInteraction(
                from_agent="agent_002",
                to_agent="agent_003",
                interaction_type="task_assignment",
                timestamp="2026-01-19T10:02:00Z",
            ),
        ]

        patterns = analyzer.identify_coordination_patterns(interactions)

        assert isinstance(patterns, dict)
        assert "bidirectional_pairs" in patterns
        assert "hub_agents" in patterns
        assert isinstance(patterns["bidirectional_pairs"], list)
        assert isinstance(patterns["hub_agents"], list)

    def test_export_to_json(self):
        """Test exporting graph data to JSON format."""
        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent_001",
                to_agent="agent_002",
                interaction_type="message",
                timestamp="2026-01-19T10:00:00Z",
            ),
        ]

        graph = analyzer.build_graph(interactions)
        json_data = analyzer.export_to_json(graph)

        assert isinstance(json_data, str)
        # Validate it's valid JSON
        parsed = json.loads(json_data)
        assert "nodes" in parsed
        assert "edges" in parsed

    def test_export_to_graphml(self):
        """Test exporting graph data to GraphML format."""
        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent_001",
                to_agent="agent_002",
                interaction_type="message",
                timestamp="2026-01-19T10:00:00Z",
            ),
        ]

        graph = analyzer.build_graph(interactions)
        graphml_data = analyzer.export_to_graphml(graph)

        assert isinstance(graphml_data, str)
        assert "<?xml" in graphml_data  # GraphML is XML-based
        assert "<graphml" in graphml_data

    def test_complex_interaction_network(self):
        """Test analyzing a complex multi-agent interaction network."""
        analyzer = GraphComplexityAnalyzer()

        # Create a more complex network with 5 agents
        interactions = [
            AgentInteraction(
                from_agent=f"agent_{i:03d}",
                to_agent=f"agent_{(i+1) % 5:03d}",
                interaction_type="message",
                timestamp=f"2026-01-19T10:0{i}:00Z",
            )
            for i in range(5)
        ]
        # Add some cross connections
        interactions.extend(
            [
                AgentInteraction(
                    from_agent="agent_000",
                    to_agent="agent_002",
                    interaction_type="task_assignment",
                    timestamp="2026-01-19T10:05:00Z",
                ),
                AgentInteraction(
                    from_agent="agent_001",
                    to_agent="agent_003",
                    interaction_type="message",
                    timestamp="2026-01-19T10:06:00Z",
                ),
            ]
        )

        metrics = analyzer.calculate_metrics(interactions)

        assert metrics.num_nodes == 5
        assert metrics.num_edges == 7
        assert 0.0 <= metrics.density <= 1.0
        assert 0.0 <= metrics.avg_clustering_coefficient <= 1.0

    def test_single_interaction(self):
        """Test handling a single interaction between two agents."""
        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent_001",
                to_agent="agent_002",
                interaction_type="message",
                timestamp="2026-01-19T10:00:00Z",
            ),
        ]

        metrics = analyzer.calculate_metrics(interactions)

        assert metrics.num_nodes == 2
        assert metrics.num_edges == 1
        assert isinstance(metrics.density, float)

    def test_bidirectional_interactions(self):
        """Test handling bidirectional interactions between agents."""
        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent_001",
                to_agent="agent_002",
                interaction_type="message",
                timestamp="2026-01-19T10:00:00Z",
            ),
            AgentInteraction(
                from_agent="agent_002",
                to_agent="agent_001",
                interaction_type="response",
                timestamp="2026-01-19T10:01:00Z",
            ),
        ]

        graph = analyzer.build_graph(interactions)
        patterns = analyzer.identify_coordination_patterns(interactions)

        assert graph.number_of_nodes() == 2
        assert graph.number_of_edges() == 2
        # Should identify this as a bidirectional pair
        assert len(patterns["bidirectional_pairs"]) > 0

    def test_hub_agent_identification(self):
        """Test identifying hub agents with high connectivity."""
        analyzer = GraphComplexityAnalyzer()

        # Create a hub-and-spoke pattern where agent_hub connects to all others
        interactions = [
            AgentInteraction(
                from_agent="agent_hub",
                to_agent=f"agent_{i:03d}",
                interaction_type="message",
                timestamp=f"2026-01-19T10:0{i}:00Z",
            )
            for i in range(5)
        ]

        patterns = analyzer.identify_coordination_patterns(interactions)

        assert "hub_agents" in patterns
        assert "agent_hub" in patterns["hub_agents"]

    def test_metrics_to_json_format(self):
        """Test graph metrics can be serialized to JSON format."""
        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent_001",
                to_agent="agent_002",
                interaction_type="message",
                timestamp="2026-01-19T10:00:00Z",
            ),
        ]

        metrics = analyzer.calculate_metrics(interactions)
        json_output = metrics.model_dump_json()

        assert isinstance(json_output, str)
        assert "density" in json_output
        assert "avg_clustering_coefficient" in json_output
        assert "avg_betweenness_centrality" in json_output
        assert "avg_closeness_centrality" in json_output
        assert "num_nodes" in json_output
        assert "num_edges" in json_output

    def test_empty_graph_metrics(self):
        """Test calculating metrics on an empty graph."""
        analyzer = GraphComplexityAnalyzer()

        metrics = analyzer.calculate_metrics([])

        assert metrics.num_nodes == 0
        assert metrics.num_edges == 0
        # Empty graph should have zero metrics
        assert metrics.density == 0.0
        assert metrics.avg_clustering_coefficient == 0.0
        assert metrics.avg_betweenness_centrality == 0.0
        assert metrics.avg_closeness_centrality == 0.0

    def test_interaction_with_metadata(self):
        """Test interactions with metadata are properly captured in graph."""
        analyzer = GraphComplexityAnalyzer()

        interactions = [
            AgentInteraction(
                from_agent="agent_001",
                to_agent="agent_002",
                interaction_type="message",
                timestamp="2026-01-19T10:00:00Z",
                metadata={"priority": "high", "message_id": "msg_001"},
            ),
        ]

        graph = analyzer.build_graph(interactions)
        json_data = analyzer.export_to_json(graph)

        assert isinstance(json_data, str)
        parsed = json.loads(json_data)
        # Check that edge data includes interaction details
        assert len(parsed["edges"]) == 1
