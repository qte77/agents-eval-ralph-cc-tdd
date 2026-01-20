"""PeerRead dataset loader and parser.

Load and parse PeerRead dataset from local storage into structured Pydantic models.
"""

import json
from pathlib import Path

from agenteval.models.data import Paper, Review


class PeerReadLoader:
    """Load and parse PeerRead dataset from local storage."""

    def __init__(self, data_dir: Path):
        """Initialize loader with dataset directory.

        Args:
            data_dir: Path to directory containing PeerRead dataset files
        """
        self.data_dir = Path(data_dir)

    def load_papers(self, limit: int | None = None) -> list[Paper]:
        """Load papers from local storage into Paper models.

        Args:
            limit: Maximum number of papers to load (None = all)

        Returns:
            List of Paper models
        """
        papers = []
        paper_files = sorted(self.data_dir.glob("paper_*.json"))

        if limit:
            paper_files = paper_files[:limit]

        for paper_file in paper_files:
            try:
                paper_data = json.loads(paper_file.read_text())
                paper = Paper(**paper_data)
                papers.append(paper)
            except (json.JSONDecodeError, ValueError):
                # Skip invalid files
                continue

        return papers

    def load_reviews(self) -> list[Review]:
        """Load reviews from local storage into Review models.

        Returns:
            List of Review models
        """
        reviews = []
        review_files = sorted(self.data_dir.glob("review_*.json"))

        for review_file in review_files:
            try:
                review_data = json.loads(review_file.read_text())
                review = Review(**review_data)
                reviews.append(review)
            except (json.JSONDecodeError, ValueError):
                # Skip invalid files
                continue

        return reviews

    def load_papers_with_reviews(self) -> list[tuple[Paper, list[Review]]]:
        """Load papers with their associated reviews.

        Returns:
            List of tuples containing (Paper, list of Reviews)
        """
        papers = self.load_papers()
        reviews = self.load_reviews()

        # Group reviews by paper_id
        reviews_by_paper = {}
        for review in reviews:
            if review.paper_id not in reviews_by_paper:
                reviews_by_paper[review.paper_id] = []
            reviews_by_paper[review.paper_id].append(review)

        # Pair papers with their reviews
        result = []
        for paper in papers:
            paper_reviews = reviews_by_paper.get(paper.id, [])
            result.append((paper, paper_reviews))

        return result

    def get_reviews_for_paper(self, paper_id: str) -> list[Review]:
        """Get all reviews for a specific paper.

        Args:
            paper_id: Paper ID to get reviews for

        Returns:
            List of Review models for the specified paper
        """
        all_reviews = self.load_reviews()
        return [r for r in all_reviews if r.paper_id == paper_id]
