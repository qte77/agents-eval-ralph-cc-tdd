"""Dataset loader and parser for PeerRead data."""

import json
from pathlib import Path

from agenteval.models.data import Paper, Review


class PeerReadLoader:
    """Loads and parses PeerRead dataset from local storage."""

    def __init__(self, dataset_path: Path | None = None) -> None:
        """Initialize the PeerRead loader.

        Args:
            dataset_path: Path to dataset directory
        """
        self.dataset_path = dataset_path or Path("data/peerread")

    def load(self) -> list[Paper]:
        """Load the complete dataset.

        Returns:
            List of Paper objects

        Raises:
            FileNotFoundError: If dataset file doesn't exist
        """
        data_file = self.dataset_path / "reviews.json"
        if not data_file.exists():
            raise FileNotFoundError(f"Dataset file not found: {data_file}")

        with open(data_file) as f:
            raw_data = json.load(f)

        papers = []
        for item in raw_data:
            paper = Paper(
                paper_id=item["id"],
                title=item["title"],
                abstract=item["abstract"],
                content=item["content"],
                metadata=item.get("metadata", {}),
            )
            papers.append(paper)

        return papers

    def load_dataset(self) -> list[Paper]:
        """Load the complete dataset.

        Returns:
            List of Paper objects
        """
        return self.load()

    def load_batch(self, batch_size: int = 10) -> list[Paper]:
        """Load a batch of records.

        Args:
            batch_size: Number of records per batch

        Returns:
            Batch of Paper objects
        """
        all_papers = self.load()
        return all_papers[:batch_size]

    def load_with_reviews(self) -> tuple[list[Paper], list[Review]]:
        """Load dataset with reviews.

        Returns:
            Tuple of (papers list, reviews list)

        Raises:
            FileNotFoundError: If dataset file doesn't exist
        """
        data_file = self.dataset_path / "reviews.json"
        if not data_file.exists():
            raise FileNotFoundError(f"Dataset file not found: {data_file}")

        with open(data_file) as f:
            raw_data = json.load(f)

        papers = []
        reviews = []

        for item in raw_data:
            paper = Paper(
                paper_id=item["id"],
                title=item["title"],
                abstract=item["abstract"],
                content=item["content"],
                metadata=item.get("metadata", {}),
            )
            papers.append(paper)

            for review_data in item.get("reviews", []):
                review = Review(
                    review_id=review_data["id"],
                    paper_id=review_data["paper_id"],
                    rating=review_data["rating"],
                    confidence=review_data["confidence"],
                    summary=review_data["summary"],
                    strengths=review_data.get("strengths", []),
                    weaknesses=review_data.get("weaknesses", []),
                    detailed_comments=review_data["detailed_comments"],
                    is_agent_generated=review_data["is_agent_generated"],
                )
                reviews.append(review)

        return papers, reviews


def load_peerread_dataset(dataset_path: Path | None = None) -> list[Paper]:
    """Load PeerRead dataset from local storage.

    Args:
        dataset_path: Path to dataset directory

    Returns:
        List of Paper objects
    """
    loader = PeerReadLoader(dataset_path=dataset_path)
    return loader.load()
