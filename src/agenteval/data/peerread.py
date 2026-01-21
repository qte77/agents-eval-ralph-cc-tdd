"""PeerRead dataset loader and parser.

Loads and parses PeerRead dataset from local storage into structured Pydantic models.
"""

from __future__ import annotations

import json
from pathlib import Path

from agenteval.models.data import Paper, Review


class PeerReadLoader:
    """Loads PeerRead dataset from local storage."""

    def __init__(self, dataset_path: Path) -> None:
        """Initialize loader with dataset path.

        Args:
            dataset_path: Path to dataset directory
        """
        self.dataset_path = Path(dataset_path)

    def _load_raw_data(self) -> list[dict]:
        """Load raw JSON data from dataset file.

        Returns:
            List of raw data dictionaries

        Raises:
            FileNotFoundError: If dataset file doesn't exist
            json.JSONDecodeError: If dataset file contains invalid JSON
        """
        data_file = self.dataset_path / "reviews.json"

        if not data_file.exists():
            raise FileNotFoundError(f"Dataset file not found: {data_file}")

        data_content = data_file.read_text()
        return json.loads(data_content)

    def _parse_paper(self, item: dict) -> Paper:
        """Parse raw paper data into Paper model.

        Args:
            item: Raw paper data dictionary

        Returns:
            Paper object
        """
        return Paper(
            paper_id=item["id"],
            title=item["title"],
            abstract=item["abstract"],
            content=item["content"],
            metadata=item.get("metadata", {}),
        )

    def _parse_review(self, review_data: dict) -> Review:
        """Parse raw review data into Review model.

        Args:
            review_data: Raw review data dictionary

        Returns:
            Review object
        """
        return Review(
            review_id=review_data["id"],
            paper_id=review_data["paper_id"],
            rating=review_data["rating"],
            confidence=review_data["confidence"],
            summary=review_data["summary"],
            strengths=review_data["strengths"],
            weaknesses=review_data["weaknesses"],
            detailed_comments=review_data["detailed_comments"],
            is_agent_generated=review_data["is_agent_generated"],
        )

    def load(self) -> list[Paper]:
        """Load dataset from local storage and parse into Paper models.

        Returns:
            List of Paper objects

        Raises:
            FileNotFoundError: If dataset file doesn't exist
            json.JSONDecodeError: If dataset file contains invalid JSON
        """
        raw_data = self._load_raw_data()
        return [self._parse_paper(item) for item in raw_data]

    def load_with_reviews(self) -> tuple[list[Paper], list[Review]]:
        """Load dataset with reviews from local storage.

        Returns:
            Tuple of (list of Paper objects, list of Review objects)

        Raises:
            FileNotFoundError: If dataset file doesn't exist
            json.JSONDecodeError: If dataset file contains invalid JSON
        """
        raw_data = self._load_raw_data()

        papers = []
        reviews = []

        for item in raw_data:
            papers.append(self._parse_paper(item))

            for review_data in item.get("reviews", []):
                reviews.append(self._parse_review(review_data))

        return papers, reviews


def load_peerread_dataset(dataset_path: Path | None = None) -> list[Paper]:
    """Convenience function to load PeerRead dataset.

    Args:
        dataset_path: Path to dataset directory. Defaults to data/peerread

    Returns:
        List of Paper objects
    """
    if dataset_path is None:
        dataset_path = Path("data/peerread")

    loader = PeerReadLoader(dataset_path=dataset_path)
    return loader.load()
