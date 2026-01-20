"""Tests for PeerRead dataset loader.

Following TDD RED phase - these tests should FAIL until implementation is complete.
Tests validate loading and parsing PeerRead dataset from local storage into Pydantic models.
"""

from pathlib import Path

import pytest

from agenteval.models.data import Paper, Review


class TestPeerReadLoader:
    """Test PeerReadLoader functionality for loading dataset from local storage."""

    def test_loader_initialization(self):
        """Test PeerReadLoader can be initialized with data directory."""
        from agenteval.data.peerread import PeerReadLoader

        loader = PeerReadLoader(data_dir=Path("data/peerread"))
        assert loader is not None
        assert loader.data_dir == Path("data/peerread")

    def test_loader_loads_papers_from_local_storage(self, tmp_path: Path):
        """Test loader can load papers from local JSON files."""
        from agenteval.data.peerread import PeerReadLoader

        # Create test data directory
        data_dir = tmp_path / "peerread"
        data_dir.mkdir()

        # Create sample paper JSON file
        paper_file = data_dir / "paper1.json"
        paper_file.write_text(
            """{
            "id": "paper1",
            "title": "Test Paper",
            "abstract": "This is a test abstract",
            "authors": ["Author One", "Author Two"],
            "venue": "Test Conference",
            "year": 2024,
            "keywords": ["test", "paper"]
        }"""
        )

        loader = PeerReadLoader(data_dir=data_dir)
        papers = loader.load_papers()

        assert len(papers) == 1
        assert isinstance(papers[0], Paper)
        assert papers[0].title == "Test Paper"

    def test_loader_parses_into_pydantic_models(self, tmp_path: Path):
        """Test loader parses JSON into Paper and Review Pydantic models."""
        from agenteval.data.peerread import PeerReadLoader

        data_dir = tmp_path / "peerread"
        data_dir.mkdir()

        paper_file = data_dir / "paper1.json"
        paper_file.write_text(
            """{
            "id": "paper1",
            "title": "ML Paper",
            "abstract": "Machine learning research",
            "authors": ["ML Author"],
            "venue": "ICML"
        }"""
        )

        loader = PeerReadLoader(data_dir=data_dir)
        papers = loader.load_papers()

        paper = papers[0]
        assert isinstance(paper, Paper)
        assert paper.id == "paper1"
        assert paper.title == "ML Paper"
        assert paper.authors == ["ML Author"]
        assert paper.venue == "ICML"

    def test_loader_loads_reviews_from_local_storage(self, tmp_path: Path):
        """Test loader can load reviews from local JSON files."""
        from agenteval.data.peerread import PeerReadLoader

        data_dir = tmp_path / "peerread"
        data_dir.mkdir()

        review_file = data_dir / "review1.json"
        review_file.write_text(
            """{
            "id": "review1",
            "paper_id": "paper1",
            "rating": 8,
            "confidence": 4,
            "review_text": "This is a good paper with solid contributions."
        }"""
        )

        loader = PeerReadLoader(data_dir=data_dir)
        reviews = loader.load_reviews()

        assert len(reviews) == 1
        assert isinstance(reviews[0], Review)
        assert reviews[0].paper_id == "paper1"
        assert reviews[0].rating == 8

    def test_loader_supports_batch_loading(self, tmp_path: Path):
        """Test loader supports batch loading of multiple papers."""
        from agenteval.data.peerread import PeerReadLoader

        data_dir = tmp_path / "peerread"
        data_dir.mkdir()

        # Create multiple paper files
        for i in range(5):
            paper_file = data_dir / f"paper{i}.json"
            paper_file.write_text(
                f"""{{
                "id": "paper{i}",
                "title": "Paper {i}",
                "abstract": "Abstract {i}",
                "authors": ["Author {i}"],
                "venue": "Conference"
            }}"""
            )

        loader = PeerReadLoader(data_dir=data_dir)
        papers = loader.load_papers(max_papers=3)

        assert len(papers) == 3
        assert all(isinstance(p, Paper) for p in papers)

    def test_loader_returns_structured_data_format(self, tmp_path: Path):
        """Test loader returns structured data for downstream processing."""
        from agenteval.data.peerread import PeerReadLoader

        data_dir = tmp_path / "peerread"
        data_dir.mkdir()

        paper_file = data_dir / "paper1.json"
        paper_file.write_text(
            """{
            "id": "p1",
            "title": "Test",
            "abstract": "Abstract",
            "authors": ["A"],
            "venue": "V"
        }"""
        )

        review_file = data_dir / "review1.json"
        review_file.write_text(
            """{
            "id": "r1",
            "paper_id": "p1",
            "rating": 7,
            "confidence": 3,
            "review_text": "Good work"
        }"""
        )

        loader = PeerReadLoader(data_dir=data_dir)
        dataset = loader.load_dataset()

        assert isinstance(dataset, dict)
        assert "papers" in dataset
        assert "reviews" in dataset
        assert isinstance(dataset["papers"], list)
        assert isinstance(dataset["reviews"], list)

    def test_loader_handles_missing_optional_fields(self, tmp_path: Path):
        """Test loader handles missing optional fields gracefully."""
        from agenteval.data.peerread import PeerReadLoader

        data_dir = tmp_path / "peerread"
        data_dir.mkdir()

        # Paper with minimal required fields (no year, no keywords)
        paper_file = data_dir / "paper1.json"
        paper_file.write_text(
            """{
            "id": "paper1",
            "title": "Minimal Paper",
            "abstract": "Abstract",
            "authors": ["Author"],
            "venue": "Venue"
        }"""
        )

        loader = PeerReadLoader(data_dir=data_dir)
        papers = loader.load_papers()

        assert len(papers) == 1
        paper = papers[0]
        assert paper.year is None
        assert paper.keywords == []

    def test_loader_handles_empty_directory(self, tmp_path: Path):
        """Test loader handles empty data directory gracefully."""
        from agenteval.data.peerread import PeerReadLoader

        data_dir = tmp_path / "empty"
        data_dir.mkdir()

        loader = PeerReadLoader(data_dir=data_dir)
        papers = loader.load_papers()

        assert papers == []

    def test_loader_handles_invalid_json(self, tmp_path: Path):
        """Test loader handles invalid JSON files gracefully."""
        from agenteval.data.peerread import PeerReadLoader

        data_dir = tmp_path / "peerread"
        data_dir.mkdir()

        # Create invalid JSON file
        invalid_file = data_dir / "invalid.json"
        invalid_file.write_text("not valid json {")

        loader = PeerReadLoader(data_dir=data_dir)
        papers = loader.load_papers()

        # Should skip invalid files
        assert papers == []

    def test_loader_validates_data_with_pydantic(self, tmp_path: Path):
        """Test loader uses Pydantic validation on parsed data."""
        from agenteval.data.peerread import PeerReadLoader

        data_dir = tmp_path / "peerread"
        data_dir.mkdir()

        # Create review with invalid rating (out of 1-10 range)
        review_file = data_dir / "review1.json"
        review_file.write_text(
            """{
            "id": "r1",
            "paper_id": "p1",
            "rating": 15,
            "confidence": 3,
            "review_text": "Review"
        }"""
        )

        loader = PeerReadLoader(data_dir=data_dir)
        reviews = loader.load_reviews()

        # Should skip invalid reviews
        assert reviews == []

    def test_loader_filters_by_paper_ids(self, tmp_path: Path):
        """Test loader can filter papers by specific IDs."""
        from agenteval.data.peerread import PeerReadLoader

        data_dir = tmp_path / "peerread"
        data_dir.mkdir()

        for i in range(3):
            paper_file = data_dir / f"paper{i}.json"
            paper_file.write_text(
                f"""{{
                "id": "p{i}",
                "title": "Paper {i}",
                "abstract": "Abstract",
                "authors": ["A"],
                "venue": "V"
            }}"""
            )

        loader = PeerReadLoader(data_dir=data_dir)
        papers = loader.load_papers(paper_ids=["p0", "p2"])

        assert len(papers) == 2
        assert {p.id for p in papers} == {"p0", "p2"}


class TestPeerReadDataIntegrity:
    """Test data integrity and validation."""

    def test_paper_model_validation(self):
        """Test Paper model validates required fields."""
        with pytest.raises(Exception):  # ValidationError
            Paper(id="", title="Test", abstract="A", authors=[], venue="V")

    def test_review_model_validation(self):
        """Test Review model validates rating ranges."""
        with pytest.raises(Exception):  # ValidationError
            Review(id="r1", paper_id="p1", rating=0, confidence=3, review_text="Bad rating")

        with pytest.raises(Exception):  # ValidationError
            Review(id="r1", paper_id="p1", rating=11, confidence=3, review_text="Bad rating")
