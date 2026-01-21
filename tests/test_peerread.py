"""Tests for PeerRead dataset loader and parser.

Tests verify loading from local storage, parsing into Pydantic models,
batch loading, and structured data output.
"""

from pathlib import Path

import pytest
from agenteval.data.peerread import (  # type: ignore[import-not-found]
    PeerReadLoader,
    load_peerread_dataset,
)
from agenteval.models.data import Paper, Review


def test_peerread_loader_loads_from_local_storage(tmp_path: Path):
    """Test that loader can load dataset from local storage path."""
    dataset_path = tmp_path / "peerread"
    dataset_path.mkdir(parents=True)

    # Create mock dataset file
    import json

    mock_data = [
        {
            "id": "paper1",
            "title": "Test Paper 1",
            "abstract": "Test abstract",
            "content": "Full paper content",
            "metadata": {},
            "reviews": []
        }
    ]
    (dataset_path / "reviews.json").write_text(json.dumps(mock_data))

    loader = PeerReadLoader(dataset_path=dataset_path)
    result = loader.load()

    assert result is not None
    assert len(result) > 0


def test_peerread_loader_parses_into_paper_model(tmp_path: Path):
    """Test that loader parses data into Paper Pydantic model."""
    dataset_path = tmp_path / "peerread"
    dataset_path.mkdir(parents=True)

    import json

    mock_data = [
        {
            "id": "paper1",
            "title": "Test Paper",
            "abstract": "Test abstract",
            "content": "Full content",
            "metadata": {"year": 2024},
            "reviews": []
        }
    ]
    (dataset_path / "reviews.json").write_text(json.dumps(mock_data))

    loader = PeerReadLoader(dataset_path=dataset_path)
    result = loader.load()

    assert len(result) == 1
    assert isinstance(result[0], Paper)
    assert result[0].paper_id == "paper1"
    assert result[0].title == "Test Paper"
    assert result[0].abstract == "Test abstract"


def test_peerread_loader_parses_reviews(tmp_path: Path):
    """Test that loader parses review data into Review Pydantic models."""
    dataset_path = tmp_path / "peerread"
    dataset_path.mkdir(parents=True)

    import json

    mock_data = [
        {
            "id": "paper1",
            "title": "Test Paper",
            "abstract": "Abstract",
            "content": "Content",
            "metadata": {},
            "reviews": [
                {
                    "id": "review1",
                    "paper_id": "paper1",
                    "rating": 5,
                    "confidence": 4,
                    "summary": "Good paper",
                    "strengths": ["Clear writing"],
                    "weaknesses": ["Limited scope"],
                    "detailed_comments": "Detailed feedback here",
                    "is_agent_generated": False
                }
            ]
        }
    ]
    (dataset_path / "reviews.json").write_text(json.dumps(mock_data))

    loader = PeerReadLoader(dataset_path=dataset_path)
    papers, reviews = loader.load_with_reviews()

    assert len(reviews) == 1
    assert isinstance(reviews[0], Review)
    assert reviews[0].review_id == "review1"
    assert reviews[0].paper_id == "paper1"
    assert reviews[0].rating == 5


def test_peerread_loader_supports_batch_loading(tmp_path: Path):
    """Test that loader can load multiple papers in batch."""
    dataset_path = tmp_path / "peerread"
    dataset_path.mkdir(parents=True)

    import json

    # Create dataset with multiple papers
    mock_data = [
        {
            "id": f"paper{i}",
            "title": f"Test Paper {i}",
            "abstract": f"Abstract {i}",
            "content": f"Content {i}",
            "metadata": {},
            "reviews": []
        }
        for i in range(10)
    ]
    (dataset_path / "reviews.json").write_text(json.dumps(mock_data))

    loader = PeerReadLoader(dataset_path=dataset_path)
    result = loader.load()

    assert len(result) == 10
    assert all(isinstance(p, Paper) for p in result)
    assert result[0].paper_id == "paper0"
    assert result[9].paper_id == "paper9"


def test_peerread_loader_returns_structured_data(tmp_path: Path):
    """Test that loader returns data in structured format for downstream processing."""
    dataset_path = tmp_path / "peerread"
    dataset_path.mkdir(parents=True)

    import json

    mock_data = [
        {
            "id": "paper1",
            "title": "Test",
            "abstract": "Abstract",
            "content": "Content",
            "metadata": {"venue": "ICML"},
            "reviews": [
                {
                    "id": "review1",
                    "paper_id": "paper1",
                    "rating": 5,
                    "confidence": 4,
                    "summary": "Good",
                    "strengths": ["A"],
                    "weaknesses": ["B"],
                    "detailed_comments": "Comments",
                    "is_agent_generated": False
                }
            ]
        }
    ]
    (dataset_path / "reviews.json").write_text(json.dumps(mock_data))

    loader = PeerReadLoader(dataset_path=dataset_path)
    papers, reviews = loader.load_with_reviews()

    # Check structured output - lists of Pydantic models
    assert isinstance(papers, list)
    assert isinstance(reviews, list)
    assert all(isinstance(p, Paper) for p in papers)
    assert all(isinstance(r, Review) for r in reviews)


def test_load_peerread_dataset_convenience_function(tmp_path: Path):
    """Test convenience function for loading PeerRead dataset."""
    dataset_path = tmp_path / "peerread"
    dataset_path.mkdir(parents=True)

    import json

    mock_data = [
        {
            "id": "paper1",
            "title": "Test",
            "abstract": "Abstract",
            "content": "Content",
            "metadata": {},
            "reviews": []
        }
    ]
    (dataset_path / "reviews.json").write_text(json.dumps(mock_data))

    result = load_peerread_dataset(dataset_path=dataset_path)

    assert len(result) == 1
    assert isinstance(result[0], Paper)


def test_peerread_loader_handles_missing_files(tmp_path: Path):
    """Test that loader handles missing dataset files gracefully."""
    dataset_path = tmp_path / "peerread"
    dataset_path.mkdir(parents=True)

    loader = PeerReadLoader(dataset_path=dataset_path)

    with pytest.raises(FileNotFoundError):
        loader.load()


def test_peerread_loader_handles_invalid_json(tmp_path: Path):
    """Test that loader handles invalid JSON gracefully."""
    dataset_path = tmp_path / "peerread"
    dataset_path.mkdir(parents=True)

    (dataset_path / "reviews.json").write_text("invalid json {")

    loader = PeerReadLoader(dataset_path=dataset_path)

    with pytest.raises(Exception):  # Should raise JSON decode error
        loader.load()


def test_peerread_loader_validates_data_against_models(tmp_path: Path):
    """Test that loader validates data against Pydantic models."""
    dataset_path = tmp_path / "peerread"
    dataset_path.mkdir(parents=True)

    import json

    # Missing required fields
    mock_data = [
        {
            "id": "paper1",
            # Missing title, abstract, content
        }
    ]
    (dataset_path / "reviews.json").write_text(json.dumps(mock_data))

    loader = PeerReadLoader(dataset_path=dataset_path)

    with pytest.raises(Exception):  # Should raise validation error
        loader.load()
