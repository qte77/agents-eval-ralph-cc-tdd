"""PeerRead dataset loader and parser.

Load and parse PeerRead dataset from local storage into structured Pydantic models.
"""

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from agenteval.models.data import Paper, Review

T = TypeVar("T", bound=BaseModel)


class PeerReadLoader:
    """Load and parse PeerRead dataset from local storage."""

    def __init__(self, data_dir: Path):
        """Initialize loader with data directory.

        Args:
            data_dir: Path to directory containing PeerRead dataset files
        """
        self.data_dir = data_dir

    def _load_items(
        self, pattern: str, model_class: type[T], max_items: int | None = None
    ) -> list[T]:
        """Load items from JSON files matching pattern.

        Args:
            pattern: Glob pattern for files to load
            model_class: Pydantic model class to parse into
            max_items: Maximum number of items to load

        Returns:
            List of parsed model instances
        """
        items = []

        if not self.data_dir.exists():
            return items

        json_files = sorted(self.data_dir.glob(pattern))

        for json_file in json_files:
            if max_items and len(items) >= max_items:
                break

            try:
                data = json.loads(json_file.read_text())
                item = model_class(**data)
                items.append(item)
            except (json.JSONDecodeError, ValidationError):
                continue

        return items

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
        papers = self._load_items("paper*.json", Paper, max_items=None)

        if paper_ids:
            papers = [p for p in papers if p.id in paper_ids]

        if max_papers:
            papers = papers[:max_papers]

        return papers

    def load_reviews(self) -> list[Review]:
        """Load reviews from local JSON files.

        Returns:
            List of Review objects
        """
        return self._load_items("review*.json", Review)

    def load_dataset(self) -> dict[str, list[Paper] | list[Review]]:
        """Load complete dataset with papers and reviews.

        Returns:
            Dictionary with 'papers' and 'reviews' keys
        """
        return {
            "papers": self.load_papers(),
            "reviews": self.load_reviews(),
        }
