"""Tests for PeerRead dataset loader.

Following TDD RED phase - these tests should FAIL until implementation is complete.
"""

import pytest
from pathlib import Path


class TestPeerReadModels:
    """Test Pydantic models for PeerRead dataset."""

    def test_paper_model_basic_fields(self):
        """Test Paper model with basic required fields."""
        from agenteval.data.peerread import Paper

        paper = Paper(
            name="test_paper.pdf",
            title="Test Paper",
            abstract="This is a test abstract",
            authors=["Author One", "Author Two"],
            year=2024,
        )

        assert paper.name == "test_paper.pdf"
        assert paper.title == "Test Paper"
        assert paper.abstract == "This is a test abstract"
        assert len(paper.authors) == 2
        assert paper.year == 2024

    def test_review_model_basic_fields(self):
        """Test Review model with basic required fields."""
        from agenteval.data.peerread import Review

        review = Review(
            reviewer_id="reviewer_1",
            comments="This is a test review",
            recommendation="accept",
        )

        assert review.reviewer_id == "reviewer_1"
        assert review.comments == "This is a test review"
        assert review.recommendation == "accept"

    def test_review_model_with_scores(self):
        """Test Review model with optional aspect scores."""
        from agenteval.data.peerread import Review

        review = Review(
            reviewer_id="reviewer_1",
            comments="Good paper",
            recommendation="accept",
            clarity="4",
            originality="5",
            soundness_correctness="4",
        )

        assert review.clarity == "4"
        assert review.originality == "5"
        assert review.soundness_correctness == "4"

    def test_paper_review_pair_model(self):
        """Test PaperReviewPair model that combines paper and reviews."""
        from agenteval.data.peerread import Paper, Review, PaperReviewPair

        paper = Paper(
            name="test.pdf",
            title="Test",
            abstract="Abstract",
            authors=["Author"],
            year=2024,
        )

        review = Review(
            reviewer_id="r1",
            comments="Good",
            recommendation="accept",
        )

        pair = PaperReviewPair(
            paper=paper,
            reviews=[review],
            accepted=True,
        )

        assert pair.paper.title == "Test"
        assert len(pair.reviews) == 1
        assert pair.accepted is True


class TestPeerReadLoader:
    """Test PeerReadLoader functionality."""

    def test_loader_initialization(self):
        """Test PeerReadLoader can be initialized."""
        from agenteval.data.peerread import PeerReadLoader

        loader = PeerReadLoader()
        assert loader is not None

    def test_loader_loads_from_huggingface(self):
        """Test loader can load data from Hugging Face dataset."""
        from agenteval.data.peerread import PeerReadLoader

        loader = PeerReadLoader()
        # Should not raise an error
        data = loader.load(split="train", max_samples=1)
        assert data is not None
        assert len(data) > 0

    def test_loader_returns_paper_review_pairs(self):
        """Test loader returns list of PaperReviewPair objects."""
        from agenteval.data.peerread import PeerReadLoader, PaperReviewPair

        loader = PeerReadLoader()
        data = loader.load(split="train", max_samples=2)

        assert isinstance(data, list)
        assert len(data) <= 2
        assert all(isinstance(item, PaperReviewPair) for item in data)

    def test_loader_handles_missing_data_gracefully(self):
        """Test loader handles missing fields gracefully with defaults."""
        from agenteval.data.peerread import PeerReadLoader

        loader = PeerReadLoader()
        # Should not crash on malformed data
        data = loader.load(split="train", max_samples=5)
        assert isinstance(data, list)

    def test_loader_supports_iterator_interface(self):
        """Test loader provides iterator interface for batch processing."""
        from agenteval.data.peerread import PeerReadLoader

        loader = PeerReadLoader()
        iterator = loader.iter_batches(split="train", batch_size=2, max_samples=4)

        batches = list(iterator)
        assert len(batches) > 0
        assert all(isinstance(batch, list) for batch in batches)

    def test_loader_filters_papers_with_reviews(self):
        """Test loader can filter to only include papers with reviews."""
        from agenteval.data.peerread import PeerReadLoader

        loader = PeerReadLoader()
        data = loader.load(split="train", max_samples=10, require_reviews=True)

        assert all(len(pair.reviews) > 0 for pair in data)

    def test_loader_respects_max_samples(self):
        """Test loader respects max_samples parameter."""
        from agenteval.data.peerread import PeerReadLoader

        loader = PeerReadLoader()
        data = loader.load(split="train", max_samples=3)

        assert len(data) <= 3

    def test_loader_handles_errors_gracefully(self):
        """Test loader handles dataset errors without crashing."""
        from agenteval.data.peerread import PeerReadLoader

        loader = PeerReadLoader()

        # Should handle invalid split gracefully
        try:
            data = loader.load(split="invalid_split", max_samples=1)
            # If it doesn't raise, it should return empty list
            assert isinstance(data, list)
        except ValueError as e:
            # Or it should raise a clear error
            assert "split" in str(e).lower()


class TestPeerReadDataValidation:
    """Test data validation and error handling."""

    def test_paper_requires_essential_fields(self):
        """Test Paper model validates required fields."""
        from agenteval.data.peerread import Paper
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Paper(name="test.pdf")  # Missing required fields

    def test_review_requires_essential_fields(self):
        """Test Review model validates required fields."""
        from agenteval.data.peerread import Review
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Review(reviewer_id="r1")  # Missing required fields
