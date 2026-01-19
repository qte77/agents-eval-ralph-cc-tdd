"""PeerRead dataset loader and parser.

Load and parse PeerRead dataset from local storage into structured Pydantic models.
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
            data_dir: Path to directory containing PeerRead dataset files
        """
        self.data_dir = data_dir

    def load_papers(
        self, max_papers: int | None = None, paper_ids: list[str] | None = None
    ) -> list[Paper]:
        """Load papers from local JSON files.

        Args:
            max_papers: Maximum number of papers to load
            paper_ids: Filter to only load papers with these IDs

        Returns:
            List of Paper objects
        """
        papers = []

        if not self.data_dir.exists():
            return papers

        # Find all JSON files that match paper pattern
        json_files = sorted(self.data_dir.glob("paper*.json"))

        for json_file in json_files:
            if max_papers and len(papers) >= max_papers:
                break

            try:
                data = json.loads(json_file.read_text())
                paper = Paper(**data)

                # Filter by paper_ids if provided
                if paper_ids and paper.id not in paper_ids:
                    continue

                papers.append(paper)
            except (json.JSONDecodeError, ValidationError):
                # Skip invalid files
                continue

        return papers

    def load_reviews(self) -> list[Review]:
        """Load reviews from local JSON files.

        Returns:
            List of Review objects
        """
        reviews = []

        if not self.data_dir.exists():
            return reviews

        # Find all JSON files that match review pattern
        json_files = sorted(self.data_dir.glob("review*.json"))

        for json_file in json_files:
            try:
                data = json.loads(json_file.read_text())
                review = Review(**data)
                reviews.append(review)
            except (json.JSONDecodeError, ValidationError):
                # Skip invalid files
                continue

        return reviews

    def load_dataset(self) -> dict[str, list[Paper] | list[Review]]:
        """Load complete dataset with papers and reviews.

        Returns:
            Dictionary with 'papers' and 'reviews' keys
        """
        return {
            "papers": self.load_papers(),
            "reviews": self.load_reviews(),
        }
