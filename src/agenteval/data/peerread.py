"""PeerRead dataset loader and parser.

Loads and parses PeerRead dataset from local storage into structured Pydantic models.
"""

import json
from pathlib import Path

from pydantic import ValidationError

from agenteval.models.data import Paper, Review


class PeerReadLoader:
    """Load and parse PeerRead dataset from local storage."""

    def __init__(self, data_dir: Path):
        """Initialize loader with data directory.

        Args:
            data_dir: Directory containing PeerRead dataset files
        """
        self.data_dir = data_dir

    def load_papers(self, max_count: int | None = None) -> list[Paper]:
        """Load papers from local storage.

        Args:
            max_count: Maximum number of papers to load (None for all)

        Returns:
            List of Paper objects

        Raises:
            FileNotFoundError: If data directory doesn't exist
        """
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

        papers = []
        json_files = sorted(self.data_dir.glob("paper_*.json"))

        for file_path in json_files:
            if max_count is not None and len(papers) >= max_count:
                break

            try:
                data = json.loads(file_path.read_text())
                paper = Paper(**data)
                papers.append(paper)
            except (json.JSONDecodeError, ValidationError):
                # Skip corrupted or invalid files
                continue

        return papers

    def load_reviews(self, max_count: int | None = None) -> list[Review]:
        """Load reviews from local storage.

        Args:
            max_count: Maximum number of reviews to load (None for all)

        Returns:
            List of Review objects

        Raises:
            FileNotFoundError: If data directory doesn't exist
        """
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")

        reviews = []
        json_files = sorted(self.data_dir.glob("review_*.json"))

        for file_path in json_files:
            if max_count is not None and len(reviews) >= max_count:
                break

            try:
                data = json.loads(file_path.read_text())
                review = Review(**data)
                reviews.append(review)
            except (json.JSONDecodeError, ValidationError):
                # Skip corrupted or invalid files
                continue

        return reviews

    def load_dataset(self) -> dict[str, list[Paper] | list[Review]]:
        """Load complete dataset with papers and reviews.

        Returns:
            Dictionary with 'papers' and 'reviews' keys containing respective lists
        """
        return {
            "papers": self.load_papers(),
            "reviews": self.load_reviews(),
        }

    def get_reviews_for_paper(self, paper_id: str) -> list[Review]:
        """Get all reviews for a specific paper.

        Args:
            paper_id: ID of the paper

        Returns:
            List of Review objects for the paper
        """
        all_reviews = self.load_reviews()
        return [review for review in all_reviews if review.paper_id == paper_id]
