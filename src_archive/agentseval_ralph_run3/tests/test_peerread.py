"""Tests for PeerRead dataset loader and parser.

Following TDD RED phase - these tests should FAIL until implementation is complete.
Tests validate loading and parsing PeerRead dataset from local storage into Pydantic models.
"""

import json
from pathlib import Path

import pytest

from agenteval.data.peerread import PeerReadLoader
from agenteval.models.data import Paper, Review


class TestPeerReadLoader:
    """Test PeerRead dataset loader functionality."""

    def test_loader_initialization(self, tmp_path: Path):
        """Test PeerReadLoader can be initialized with data directory."""
        loader = PeerReadLoader(data_dir=tmp_path)
        assert loader.data_dir == tmp_path
        assert isinstance(loader, PeerReadLoader)

    def test_load_papers_from_local_storage(self, tmp_path: Path):
        """Test loading papers from local storage directory."""
        # Create mock paper data
        paper_data = {
            "id": "paper_001",
            "title": "Test Paper",
            "abstract": "This is a test abstract",
            "authors": ["Author One", "Author Two"],
            "venue": "Test Conference",
            "year": 2024,
        }
        paper_file = tmp_path / "paper_001.json"
        paper_file.write_text(json.dumps(paper_data))

        loader = PeerReadLoader(data_dir=tmp_path)
        papers = loader.load_papers()

        assert len(papers) == 1
        assert isinstance(papers[0], Paper)
        assert papers[0].id == "paper_001"
        assert papers[0].title == "Test Paper"

    def test_load_reviews_from_local_storage(self, tmp_path: Path):
        """Test loading reviews from local storage directory."""
        # Create mock review data
        review_data = {
            "id": "review_001",
            "paper_id": "paper_001",
            "rating": 8,
            "confidence": 4,
            "review_text": "This is a test review",
        }
        review_file = tmp_path / "review_001.json"
        review_file.write_text(json.dumps(review_data))

        loader = PeerReadLoader(data_dir=tmp_path)
        reviews = loader.load_reviews()

        assert len(reviews) == 1
        assert isinstance(reviews[0], Review)
        assert reviews[0].id == "review_001"
        assert reviews[0].paper_id == "paper_001"
        assert reviews[0].rating == 8

    def test_batch_loading_of_multiple_papers(self, tmp_path: Path):
        """Test batch loading of multiple papers efficiently."""
        # Create multiple paper files
        for i in range(5):
            paper_data = {
                "id": f"paper_{i:03d}",
                "title": f"Test Paper {i}",
                "abstract": f"Abstract {i}",
                "authors": [f"Author {i}"],
                "venue": "Test Conference",
                "year": 2024,
            }
            paper_file = tmp_path / f"paper_{i:03d}.json"
            paper_file.write_text(json.dumps(paper_data))

        loader = PeerReadLoader(data_dir=tmp_path)
        papers = loader.load_papers()

        assert len(papers) == 5
        assert all(isinstance(p, Paper) for p in papers)

    def test_returns_structured_data_format(self, tmp_path: Path):
        """Test that loader returns structured data with papers and reviews."""
        # Create paper and review data
        paper_data = {
            "id": "paper_001",
            "title": "Test",
            "abstract": "Abstract",
            "authors": ["Author"],
            "venue": "Venue",
            "year": 2024,
        }
        review_data = {
            "id": "review_001",
            "paper_id": "paper_001",
            "rating": 7,
            "confidence": 3,
            "review_text": "Review text",
        }

        (tmp_path / "paper_001.json").write_text(json.dumps(paper_data))
        (tmp_path / "review_001.json").write_text(json.dumps(review_data))

        loader = PeerReadLoader(data_dir=tmp_path)
        dataset = loader.load_dataset()

        assert "papers" in dataset
        assert "reviews" in dataset
        assert len(dataset["papers"]) == 1
        assert len(dataset["reviews"]) == 1

    def test_handles_missing_directory_gracefully(self):
        """Test loader handles missing data directory gracefully."""
        loader = PeerReadLoader(data_dir=Path("/nonexistent/path"))

        with pytest.raises(FileNotFoundError):
            loader.load_papers()

    def test_handles_corrupted_json_gracefully(self, tmp_path: Path):
        """Test loader handles corrupted JSON files without crashing."""
        # Create corrupted JSON file
        corrupted_file = tmp_path / "corrupted.json"
        corrupted_file.write_text("{invalid json")

        # Create valid file
        valid_data = {
            "id": "paper_001",
            "title": "Valid Paper",
            "abstract": "Valid abstract",
            "authors": ["Author"],
            "venue": "Venue",
            "year": 2024,
        }
        (tmp_path / "paper_001.json").write_text(json.dumps(valid_data))

        loader = PeerReadLoader(data_dir=tmp_path)
        papers = loader.load_papers()

        # Should skip corrupted file and load valid one
        assert len(papers) == 1
        assert papers[0].id == "paper_001"

    def test_handles_invalid_model_data_gracefully(self, tmp_path: Path):
        """Test loader handles data that doesn't match Pydantic model schema."""
        # Create data with missing required fields
        invalid_data = {
            "id": "paper_001",
            "title": "Test",
            # Missing required fields: abstract, authors, venue
        }
        (tmp_path / "paper_001.json").write_text(json.dumps(invalid_data))

        # Create valid data
        valid_data = {
            "id": "paper_002",
            "title": "Valid Paper",
            "abstract": "Valid abstract",
            "authors": ["Author"],
            "venue": "Venue",
            "year": 2024,
        }
        (tmp_path / "paper_002.json").write_text(json.dumps(valid_data))

        loader = PeerReadLoader(data_dir=tmp_path)
        papers = loader.load_papers()

        # Should skip invalid and load valid
        assert len(papers) == 1
        assert papers[0].id == "paper_002"

    def test_load_papers_returns_empty_list_when_no_papers(self, tmp_path: Path):
        """Test load_papers returns empty list when no paper files exist."""
        # Create only review file
        review_data = {
            "id": "review_001",
            "paper_id": "paper_001",
            "rating": 7,
            "confidence": 3,
            "review_text": "Review",
        }
        (tmp_path / "review_001.json").write_text(json.dumps(review_data))

        loader = PeerReadLoader(data_dir=tmp_path)
        papers = loader.load_papers()

        assert papers == []

    def test_batch_loading_with_limit(self, tmp_path: Path):
        """Test batch loading with max_count parameter."""
        # Create 10 paper files
        for i in range(10):
            paper_data = {
                "id": f"paper_{i:03d}",
                "title": f"Paper {i}",
                "abstract": "Abstract",
                "authors": ["Author"],
                "venue": "Venue",
                "year": 2024,
            }
            (tmp_path / f"paper_{i:03d}.json").write_text(json.dumps(paper_data))

        loader = PeerReadLoader(data_dir=tmp_path)
        papers = loader.load_papers(max_count=5)

        assert len(papers) == 5

    def test_get_reviews_for_paper(self, tmp_path: Path):
        """Test retrieving all reviews for a specific paper."""
        # Create paper
        paper_data = {
            "id": "paper_001",
            "title": "Test Paper",
            "abstract": "Abstract",
            "authors": ["Author"],
            "venue": "Venue",
            "year": 2024,
        }
        (tmp_path / "paper_001.json").write_text(json.dumps(paper_data))

        # Create multiple reviews for the paper
        for i in range(3):
            review_data = {
                "id": f"review_{i:03d}",
                "paper_id": "paper_001",
                "rating": 7 + i,
                "confidence": 3,
                "review_text": f"Review {i}",
            }
            (tmp_path / f"review_{i:03d}.json").write_text(json.dumps(review_data))

        loader = PeerReadLoader(data_dir=tmp_path)
        reviews = loader.get_reviews_for_paper("paper_001")

        assert len(reviews) == 3
        assert all(r.paper_id == "paper_001" for r in reviews)


class TestPeerReadDataValidation:
    """Test data validation during loading."""

    def test_paper_model_validates_required_fields(self, tmp_path: Path):
        """Test that Paper model validates required fields during loading."""
        # Data with empty id should be skipped
        paper_data = {
            "id": "",
            "title": "Test",
            "abstract": "Abstract",
            "authors": ["Author"],
            "venue": "Venue",
        }
        (tmp_path / "paper_001.json").write_text(json.dumps(paper_data))

        loader = PeerReadLoader(data_dir=tmp_path)
        papers = loader.load_papers()

        # Should skip paper with invalid id
        assert len(papers) == 0

    def test_review_model_validates_rating_range(self, tmp_path: Path):
        """Test that Review model validates rating is between 1-10."""
        # Review with invalid rating should be skipped
        review_data = {
            "id": "review_001",
            "paper_id": "paper_001",
            "rating": 15,  # Invalid: should be 1-10
            "confidence": 3,
            "review_text": "Review",
        }
        (tmp_path / "review_001.json").write_text(json.dumps(review_data))

        loader = PeerReadLoader(data_dir=tmp_path)
        reviews = loader.load_reviews()

        # Should skip review with invalid rating
        assert len(reviews) == 0

    def test_review_model_validates_confidence_range(self, tmp_path: Path):
        """Test that Review model validates confidence is between 1-5."""
        # Review with invalid confidence should be skipped
        review_data = {
            "id": "review_001",
            "paper_id": "paper_001",
            "rating": 8,
            "confidence": 10,  # Invalid: should be 1-5
            "review_text": "Review",
        }
        (tmp_path / "review_001.json").write_text(json.dumps(review_data))

        loader = PeerReadLoader(data_dir=tmp_path)
        reviews = loader.load_reviews()

        # Should skip review with invalid confidence
        assert len(reviews) == 0
