"""PeerRead dataset loader and parser."""

import json
from pathlib import Path

from agenteval.models.data import Paper, Review


class PeerReadLoader:
    """Load and parse PeerRead dataset from local storage."""

    def __init__(self, data_path: str):
        """Initialize loader.

        Args:
            data_path: Local directory path containing dataset files
        """
        self.data_path = Path(data_path)

    async def load_papers(self) -> list[Paper]:
        """Load papers from local storage into Paper models.

        Returns:
            List of Paper objects parsed from JSON files
        """
        if not self.data_path.exists():
            return []

        papers = []
        for file_path in self.data_path.glob("paper_*.json"):
            try:
                data = json.loads(file_path.read_text())
                paper = Paper.model_validate(data)
                papers.append(paper)
            except (json.JSONDecodeError, ValueError):
                # Skip corrupted or invalid files
                continue

        return papers

    async def load_reviews(self) -> list[Review]:
        """Load reviews from local storage into Review models.

        Returns:
            List of Review objects parsed from JSON files
        """
        if not self.data_path.exists():
            return []

        reviews = []
        for file_path in self.data_path.glob("review_*.json"):
            try:
                data = json.loads(file_path.read_text())
                review = Review.model_validate(data)
                reviews.append(review)
            except (json.JSONDecodeError, ValueError):
                # Skip corrupted or invalid files
                continue

        return reviews

    async def load_dataset(self) -> dict[str, list[Paper] | list[Review]]:
        """Load complete dataset with papers and reviews.

        Returns:
            Dictionary with 'papers' and 'reviews' keys containing respective lists
        """
        papers = await self.load_papers()
        reviews = await self.load_reviews()

        return {
            "papers": papers,
            "reviews": reviews,
        }
