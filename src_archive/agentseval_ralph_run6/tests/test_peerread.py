"""Tests for PeerRead dataset loader and parser."""

import json
from pathlib import Path

import pytest

from agenteval.data.peerread import PeerReadLoader
from agenteval.models.data import Paper, Review

pytestmark = pytest.mark.anyio


def test_loader_initialization():
    """Test that loader can be initialized with data path."""
    loader = PeerReadLoader(data_path="data/peerread")

    assert loader.data_path == Path("data/peerread")


async def test_load_papers_from_local_storage(tmp_path):
    """Test loading papers from local storage into Paper models."""
    # Create test dataset structure
    dataset_dir = tmp_path / "peerread"
    dataset_dir.mkdir()

    # Create sample paper file
    paper_file = dataset_dir / "paper_1.json"
    paper_data = {
        "id": "paper_1",
        "title": "Test Paper",
        "abstract": "This is a test abstract.",
        "authors": ["Author One", "Author Two"],
        "content": "This is the paper content."
    }
    paper_file.write_text(json.dumps(paper_data))

    loader = PeerReadLoader(data_path=str(dataset_dir))
    papers = await loader.load_papers()

    assert len(papers) == 1
    assert isinstance(papers[0], Paper)
    assert papers[0].id == "paper_1"
    assert papers[0].title == "Test Paper"
    assert papers[0].authors == ["Author One", "Author Two"]


async def test_load_reviews_from_local_storage(tmp_path):
    """Test loading reviews from local storage into Review models."""
    # Create test dataset structure
    dataset_dir = tmp_path / "peerread"
    dataset_dir.mkdir()

    # Create sample review file
    review_file = dataset_dir / "review_1.json"
    review_data = {
        "id": "review_1",
        "paper_id": "paper_1",
        "reviewer": "Reviewer A",
        "rating": 8.5,
        "summary": "Good paper with solid contributions.",
        "strengths": ["Clear methodology", "Strong results"],
        "weaknesses": ["Limited scope"],
        "confidence": 4
    }
    review_file.write_text(json.dumps(review_data))

    loader = PeerReadLoader(data_path=str(dataset_dir))
    reviews = await loader.load_reviews()

    assert len(reviews) == 1
    assert isinstance(reviews[0], Review)
    assert reviews[0].id == "review_1"
    assert reviews[0].paper_id == "paper_1"
    assert reviews[0].rating == 8.5
    assert reviews[0].confidence == 4


async def test_batch_loading_multiple_papers(tmp_path):
    """Test batch loading of multiple papers."""
    # Create test dataset with multiple papers
    dataset_dir = tmp_path / "peerread"
    dataset_dir.mkdir()

    # Create multiple paper files
    for i in range(3):
        paper_file = dataset_dir / f"paper_{i}.json"
        paper_data = {
            "id": f"paper_{i}",
            "title": f"Test Paper {i}",
            "abstract": f"Abstract {i}",
            "authors": [f"Author {i}"],
            "content": f"Content {i}"
        }
        paper_file.write_text(json.dumps(paper_data))

    loader = PeerReadLoader(data_path=str(dataset_dir))
    papers = await loader.load_papers()

    assert len(papers) == 3
    assert all(isinstance(p, Paper) for p in papers)
    assert {p.id for p in papers} == {"paper_0", "paper_1", "paper_2"}


async def test_batch_loading_multiple_reviews(tmp_path):
    """Test batch loading of multiple reviews."""
    # Create test dataset with multiple reviews
    dataset_dir = tmp_path / "peerread"
    dataset_dir.mkdir()

    # Create multiple review files
    for i in range(3):
        review_file = dataset_dir / f"review_{i}.json"
        review_data = {
            "id": f"review_{i}",
            "paper_id": f"paper_{i}",
            "reviewer": f"Reviewer {i}",
            "rating": 7.0 + i,
            "summary": f"Summary {i}",
            "strengths": [f"Strength {i}"],
            "weaknesses": [f"Weakness {i}"],
            "confidence": 3
        }
        review_file.write_text(json.dumps(review_data))

    loader = PeerReadLoader(data_path=str(dataset_dir))
    reviews = await loader.load_reviews()

    assert len(reviews) == 3
    assert all(isinstance(r, Review) for r in reviews)
    assert {r.id for r in reviews} == {"review_0", "review_1", "review_2"}


async def test_load_papers_and_reviews_together(tmp_path):
    """Test loading both papers and reviews for downstream processing."""
    # Create test dataset
    dataset_dir = tmp_path / "peerread"
    dataset_dir.mkdir()

    # Create paper
    paper_file = dataset_dir / "paper_1.json"
    paper_data = {
        "id": "paper_1",
        "title": "Test Paper",
        "abstract": "Abstract",
        "authors": ["Author"],
        "content": "Content"
    }
    paper_file.write_text(json.dumps(paper_data))

    # Create review for the paper
    review_file = dataset_dir / "review_1.json"
    review_data = {
        "id": "review_1",
        "paper_id": "paper_1",
        "reviewer": "Reviewer",
        "rating": 8.0,
        "summary": "Summary",
        "strengths": ["Good"],
        "weaknesses": ["Could improve"],
        "confidence": 4
    }
    review_file.write_text(json.dumps(review_data))

    loader = PeerReadLoader(data_path=str(dataset_dir))
    dataset = await loader.load_dataset()

    assert "papers" in dataset
    assert "reviews" in dataset
    assert len(dataset["papers"]) == 1
    assert len(dataset["reviews"]) == 1
    assert isinstance(dataset["papers"][0], Paper)
    assert isinstance(dataset["reviews"][0], Review)


async def test_handles_missing_directory():
    """Test handling of missing dataset directory."""
    loader = PeerReadLoader(data_path="nonexistent/path")

    papers = await loader.load_papers()
    assert papers == []


async def test_handles_corrupted_json(tmp_path):
    """Test handling of corrupted JSON files."""
    dataset_dir = tmp_path / "peerread"
    dataset_dir.mkdir()

    # Create corrupted JSON file
    corrupted_file = dataset_dir / "paper_bad.json"
    corrupted_file.write_text("{invalid json content")

    loader = PeerReadLoader(data_path=str(dataset_dir))
    papers = await loader.load_papers()

    # Should skip corrupted files and return empty list
    assert papers == []


async def test_filters_paper_vs_review_files(tmp_path):
    """Test that loader correctly identifies paper vs review files."""
    dataset_dir = tmp_path / "peerread"
    dataset_dir.mkdir()

    # Create paper file
    paper_file = dataset_dir / "paper_1.json"
    paper_data = {
        "id": "paper_1",
        "title": "Test",
        "abstract": "Abstract",
        "authors": ["Author"],
        "content": "Content"
    }
    paper_file.write_text(json.dumps(paper_data))

    # Create review file
    review_file = dataset_dir / "review_1.json"
    review_data = {
        "id": "review_1",
        "paper_id": "paper_1",
        "reviewer": "Reviewer",
        "rating": 8.0,
        "summary": "Summary",
        "strengths": ["Good"],
        "weaknesses": ["OK"],
        "confidence": 3
    }
    review_file.write_text(json.dumps(review_data))

    loader = PeerReadLoader(data_path=str(dataset_dir))

    papers = await loader.load_papers()
    reviews = await loader.load_reviews()

    # Should load only papers in load_papers
    assert len(papers) == 1
    assert papers[0].id == "paper_1"

    # Should load only reviews in load_reviews
    assert len(reviews) == 1
    assert reviews[0].id == "review_1"
