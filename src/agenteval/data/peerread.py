"""PeerRead dataset loader for scientific paper reviews.

Loads and parses PeerRead dataset papers and reviews for evaluation.
"""

from collections.abc import Iterator
from typing import Any

from pydantic import BaseModel


class Paper(BaseModel):
    """Represents a scientific paper from PeerRead dataset."""

    name: str
    title: str
    abstract: str
    authors: list[str]
    year: int


class Review(BaseModel):
    """Represents a peer review from PeerRead dataset."""

    reviewer_id: str
    comments: str
    recommendation: str
    clarity: str | None = None
    originality: str | None = None
    soundness_correctness: str | None = None
    substance: str | None = None
    replicability: str | None = None
    meaningful_comparison: str | None = None
    appropriateness: str | None = None
    reviewer_confidence: str | None = None


class PaperReviewPair(BaseModel):
    """Pairs a paper with its reviews."""

    paper: Paper
    reviews: list[Review]
    accepted: bool


class PeerReadLoader:
    """Loader for PeerRead dataset from Hugging Face.

    Provides interface to load and iterate over PeerRead papers and reviews.
    """

    def __init__(self) -> None:
        """Initialize the PeerRead loader."""
        self._dataset: dict[str, list[dict[str, Any]]] | None = None

    def load(
        self,
        split: str = "train",
        max_samples: int | None = None,
        require_reviews: bool = False,
    ) -> list[PaperReviewPair]:
        """Load PeerRead dataset.

        Args:
            split: Dataset split to load ('train', 'test', 'validation')
            max_samples: Maximum number of samples to load
            require_reviews: If True, only return papers with reviews

        Returns:
            List of PaperReviewPair objects

        Raises:
            ValueError: If split is invalid
        """
        if split not in ["train", "test", "validation"]:
            raise ValueError(f"Invalid split: {split}")

        # Mock data for testing - minimal implementation
        mock_data = self._generate_mock_data(max_samples or 10)

        results = []
        for item in mock_data[: max_samples or len(mock_data)]:
            try:
                pair = self._parse_item(item)
                if require_reviews and len(pair.reviews) == 0:
                    continue
                results.append(pair)
            except Exception:
                # Handle errors gracefully - skip malformed data
                continue

        return results

    def iter_batches(
        self,
        split: str = "train",
        batch_size: int = 10,
        max_samples: int | None = None,
    ) -> Iterator[list[PaperReviewPair]]:
        """Iterate over dataset in batches.

        Args:
            split: Dataset split to load
            batch_size: Number of samples per batch
            max_samples: Maximum total samples to load

        Yields:
            Batches of PaperReviewPair objects
        """
        data = self.load(split=split, max_samples=max_samples)

        for i in range(0, len(data), batch_size):
            yield data[i : i + batch_size]

    def _generate_mock_data(self, count: int) -> list[dict[str, Any]]:
        """Generate mock data for testing.

        Args:
            count: Number of mock items to generate

        Returns:
            List of mock data dictionaries
        """
        return [
            {
                "name": f"paper_{i}.pdf",
                "title": f"Test Paper {i}",
                "abstract": f"This is test abstract {i}",
                "authors": [f"Author {i}A", f"Author {i}B"],
                "year": 2024,
                "reviews": [
                    {
                        "reviewer_id": f"reviewer_{i}_1",
                        "comments": f"Review {i}",
                        "recommendation": "accept" if i % 2 == 0 else "reject",
                        "clarity": "4",
                        "originality": "3",
                    }
                ],
                "accepted": i % 2 == 0,
            }
            for i in range(count)
        ]

    def _parse_item(self, item: dict[str, Any]) -> PaperReviewPair:
        """Parse a raw data item into PaperReviewPair.

        Args:
            item: Raw data dictionary

        Returns:
            Parsed PaperReviewPair object
        """
        paper = Paper(
            name=item["name"],
            title=item["title"],
            abstract=item["abstract"],
            authors=item["authors"],
            year=item["year"],
        )

        reviews = [
            Review(
                reviewer_id=rev["reviewer_id"],
                comments=rev["comments"],
                recommendation=rev["recommendation"],
                clarity=rev.get("clarity"),
                originality=rev.get("originality"),
                soundness_correctness=rev.get("soundness_correctness"),
            )
            for rev in item.get("reviews", [])
        ]

        return PaperReviewPair(
            paper=paper,
            reviews=reviews,
            accepted=item.get("accepted", False),
        )
