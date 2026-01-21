"""PeerRead dataset loader and parser."""

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from agenteval.models.data import Paper, Review

T = TypeVar("T", bound=BaseModel)


class PeerReadLoader:
    """Load and parse PeerRead dataset from local storage."""

    def __init__(self, data_path: str):
        """Initialize loader.

        Args:
            data_path: Local directory path containing dataset files
        """
        self.data_path = Path(data_path)

    def _load_json_files(self, pattern: str, model_class: type[T]) -> list[T]:
        """Load and parse JSON files matching pattern into Pydantic models.

        Args:
            pattern: Glob pattern for file matching
            model_class: Pydantic model class to validate against

        Returns:
            List of parsed model instances
        """
        if not self.data_path.exists():
            return []

        results = []
        for file_path in self.data_path.glob(pattern):
            try:
                data = json.loads(file_path.read_text())
                model = model_class.model_validate(data)
                results.append(model)
            except (json.JSONDecodeError, ValueError):
                # Skip corrupted or invalid files
                continue

        return results

    async def load_papers(self) -> list[Paper]:
        """Load papers from local storage into Paper models.

        Returns:
            List of Paper objects parsed from JSON files
        """
        return self._load_json_files("paper_*.json", Paper)

    async def load_reviews(self) -> list[Review]:
        """Load reviews from local storage into Review models.

        Returns:
            List of Review objects parsed from JSON files
        """
        return self._load_json_files("review_*.json", Review)

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
