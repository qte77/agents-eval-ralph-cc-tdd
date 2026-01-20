"""Tests for PeerRead dataset loader and parser.

Following TDD approach - these tests should FAIL initially.
Tests validate loading dataset from local storage and parsing into Pydantic models.
"""

import json
from pathlib import Path

from agenteval.data.peerread import PeerReadLoader

from agenteval.models.data import Paper, Review


def test_peerread_loader_initialization():
    """Test PeerReadLoader can be initialized with dataset directory."""
    loader = PeerReadLoader(data_dir=Path("data/peerread"))
    assert loader.data_dir == Path("data/peerread")
    assert isinstance(loader, PeerReadLoader)


def test_load_papers_from_local_storage(tmp_path: Path):
    """Test loading papers from local JSON files into Paper models."""
    data_dir = tmp_path / "peerread"
    data_dir.mkdir()

    # Create sample paper JSON file
    paper_data = {
        "id": "paper_001",
        "title": "Deep Learning for NLP",
        "abstract": "This paper explores deep learning techniques for NLP tasks.",
        "authors": ["Alice Smith", "Bob Jones"],
        "venue": "ACL",
        "year": 2024,
        "keywords": ["nlp", "deep learning"]
    }
    paper_file = data_dir / "paper_001.json"
    paper_file.write_text(json.dumps(paper_data))

    loader = PeerReadLoader(data_dir=data_dir)
    papers = loader.load_papers()

    assert len(papers) == 1
    assert isinstance(papers[0], Paper)
    assert papers[0].id == "paper_001"
    assert papers[0].title == "Deep Learning for NLP"
    assert len(papers[0].authors) == 2


def test_load_reviews_from_local_storage(tmp_path: Path):
    """Test loading reviews from local JSON files into Review models."""
    data_dir = tmp_path / "peerread"
    data_dir.mkdir()

    # Create sample review JSON file
    review_data = {
        "id": "review_001",
        "paper_id": "paper_001",
        "rating": 8,
        "confidence": 4,
        "review_text": "This paper presents novel ideas with solid experimental results."
    }
    review_file = data_dir / "review_001.json"
    review_file.write_text(json.dumps(review_data))

    loader = PeerReadLoader(data_dir=data_dir)
    reviews = loader.load_reviews()

    assert len(reviews) == 1
    assert isinstance(reviews[0], Review)
    assert reviews[0].id == "review_001"
    assert reviews[0].paper_id == "paper_001"
    assert reviews[0].rating == 8
    assert reviews[0].confidence == 4


def test_load_multiple_papers_batch(tmp_path: Path):
    """Test batch loading of multiple papers from directory."""
    data_dir = tmp_path / "peerread"
    data_dir.mkdir()

    # Create multiple paper files
    for i in range(5):
        paper_data = {
            "id": f"paper_{i:03d}",
            "title": f"Paper Title {i}",
            "abstract": f"Abstract for paper {i}",
            "authors": [f"Author {i}"],
            "venue": "Conference",
            "year": 2024
        }
        paper_file = data_dir / f"paper_{i:03d}.json"
        paper_file.write_text(json.dumps(paper_data))

    loader = PeerReadLoader(data_dir=data_dir)
    papers = loader.load_papers()

    assert len(papers) == 5
    assert all(isinstance(p, Paper) for p in papers)
    assert papers[0].id == "paper_000"
    assert papers[4].id == "paper_004"


def test_load_papers_with_reviews(tmp_path: Path):
    """Test loading papers along with their associated reviews."""
    data_dir = tmp_path / "peerread"
    data_dir.mkdir()

    # Create paper
    paper_data = {
        "id": "paper_001",
        "title": "Test Paper",
        "abstract": "Test abstract",
        "authors": ["Test Author"],
        "venue": "Test Venue",
        "year": 2024
    }
    (data_dir / "paper_001.json").write_text(json.dumps(paper_data))

    # Create reviews for the paper
    review_data_1 = {
        "id": "review_001",
        "paper_id": "paper_001",
        "rating": 7,
        "confidence": 3,
        "review_text": "Good work"
    }
    review_data_2 = {
        "id": "review_002",
        "paper_id": "paper_001",
        "rating": 9,
        "confidence": 5,
        "review_text": "Excellent paper"
    }
    (data_dir / "review_001.json").write_text(json.dumps(review_data_1))
    (data_dir / "review_002.json").write_text(json.dumps(review_data_2))

    loader = PeerReadLoader(data_dir=data_dir)
    papers_with_reviews = loader.load_papers_with_reviews()

    assert len(papers_with_reviews) == 1
    paper, reviews = papers_with_reviews[0]
    assert isinstance(paper, Paper)
    assert len(reviews) == 2
    assert all(isinstance(r, Review) for r in reviews)
    assert reviews[0].paper_id == "paper_001"
    assert reviews[1].paper_id == "paper_001"


def test_load_papers_returns_structured_data(tmp_path: Path):
    """Test that loaded papers return properly structured Pydantic models."""
    data_dir = tmp_path / "peerread"
    data_dir.mkdir()

    paper_data = {
        "id": "paper_001",
        "title": "Structured Paper",
        "abstract": "Testing structure",
        "authors": ["Author A", "Author B"],
        "venue": "ICML",
        "year": 2024,
        "keywords": ["ml", "ai"]
    }
    (data_dir / "paper_001.json").write_text(json.dumps(paper_data))

    loader = PeerReadLoader(data_dir=data_dir)
    papers = loader.load_papers()

    # Verify Paper model structure and validation
    paper = papers[0]
    assert hasattr(paper, "id")
    assert hasattr(paper, "title")
    assert hasattr(paper, "abstract")
    assert hasattr(paper, "authors")
    assert hasattr(paper, "venue")
    assert hasattr(paper, "year")
    assert hasattr(paper, "keywords")

    # Verify data can be serialized back to dict
    paper_dict = paper.model_dump()
    assert paper_dict["id"] == "paper_001"
    assert isinstance(paper_dict["authors"], list)


def test_load_handles_missing_optional_fields(tmp_path: Path):
    """Test loading papers with missing optional fields like year and keywords."""
    data_dir = tmp_path / "peerread"
    data_dir.mkdir()

    # Paper with minimal required fields
    paper_data = {
        "id": "paper_001",
        "title": "Minimal Paper",
        "abstract": "Minimal abstract",
        "authors": ["Author"],
        "venue": "Venue"
    }
    (data_dir / "paper_001.json").write_text(json.dumps(paper_data))

    loader = PeerReadLoader(data_dir=data_dir)
    papers = loader.load_papers()

    assert len(papers) == 1
    assert papers[0].year is None
    assert papers[0].keywords == []


def test_load_handles_invalid_json_gracefully(tmp_path: Path):
    """Test that loader handles invalid JSON files gracefully."""
    data_dir = tmp_path / "peerread"
    data_dir.mkdir()

    # Create invalid JSON file
    invalid_file = data_dir / "invalid.json"
    invalid_file.write_text("{ this is not valid json }")

    # Create valid file
    valid_data = {
        "id": "paper_001",
        "title": "Valid Paper",
        "abstract": "Valid abstract",
        "authors": ["Author"],
        "venue": "Venue"
    }
    (data_dir / "paper_001.json").write_text(json.dumps(valid_data))

    loader = PeerReadLoader(data_dir=data_dir)
    papers = loader.load_papers()

    # Should load valid paper and skip invalid one
    assert len(papers) == 1
    assert papers[0].id == "paper_001"


def test_load_reviews_for_specific_paper(tmp_path: Path):
    """Test loading reviews for a specific paper ID."""
    data_dir = tmp_path / "peerread"
    data_dir.mkdir()

    # Create reviews for different papers
    review_1 = {
        "id": "review_001",
        "paper_id": "paper_001",
        "rating": 8,
        "confidence": 4,
        "review_text": "Review for paper 1"
    }
    review_2 = {
        "id": "review_002",
        "paper_id": "paper_002",
        "rating": 6,
        "confidence": 3,
        "review_text": "Review for paper 2"
    }
    review_3 = {
        "id": "review_003",
        "paper_id": "paper_001",
        "rating": 7,
        "confidence": 4,
        "review_text": "Another review for paper 1"
    }

    (data_dir / "review_001.json").write_text(json.dumps(review_1))
    (data_dir / "review_002.json").write_text(json.dumps(review_2))
    (data_dir / "review_003.json").write_text(json.dumps(review_3))

    loader = PeerReadLoader(data_dir=data_dir)
    reviews_for_paper_1 = loader.get_reviews_for_paper("paper_001")

    assert len(reviews_for_paper_1) == 2
    assert all(r.paper_id == "paper_001" for r in reviews_for_paper_1)
    assert reviews_for_paper_1[0].id == "review_001"
    assert reviews_for_paper_1[1].id == "review_003"


def test_loader_handles_empty_directory(tmp_path: Path):
    """Test that loader handles empty data directory gracefully."""
    data_dir = tmp_path / "peerread"
    data_dir.mkdir()

    loader = PeerReadLoader(data_dir=data_dir)
    papers = loader.load_papers()
    reviews = loader.load_reviews()

    assert papers == []
    assert reviews == []


def test_batch_loading_returns_correct_count(tmp_path: Path):
    """Test batch loading returns expected number of papers."""
    data_dir = tmp_path / "peerread"
    data_dir.mkdir()

    # Create 10 papers
    for i in range(10):
        paper_data = {
            "id": f"paper_{i:03d}",
            "title": f"Paper {i}",
            "abstract": f"Abstract {i}",
            "authors": [f"Author {i}"],
            "venue": "Conference"
        }
        (data_dir / f"paper_{i:03d}.json").write_text(json.dumps(paper_data))

    loader = PeerReadLoader(data_dir=data_dir)
    papers = loader.load_papers(limit=5)

    assert len(papers) == 5
