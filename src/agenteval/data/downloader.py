"""PeerRead dataset downloader with versioning and integrity verification.

Downloads PeerRead dataset from source and persists locally with checksums.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path

import httpx
from pydantic import BaseModel, Field


class DatasetMetadata(BaseModel):
    """Metadata for dataset versioning and integrity."""

    version: str = Field(..., description="Dataset version")
    checksum: str = Field(..., description="SHA256 checksum of dataset")
    download_date: str = Field(..., description="Date dataset was downloaded")
    source_url: str = Field(..., description="Source URL of dataset")


class DatasetDownloader:
    """Downloads and manages PeerRead dataset."""

    def __init__(
        self,
        base_path: Path,
        source_url: str = "https://api.github.com/repos/allenai/PeerRead/contents/data",
    ) -> None:
        """Initialize downloader with base path.

        Args:
            base_path: Base directory to save dataset
            source_url: URL to download dataset from
        """
        self.base_path = Path(base_path)
        self.source_url = source_url
        self.dataset_dir = self.base_path / "peerread"

    def download(self) -> bool:
        """Download dataset from source.

        Returns:
            True if download successful, False otherwise
        """
        try:
            self.dataset_dir.mkdir(parents=True, exist_ok=True)

            with httpx.Client() as client:
                response = client.get(self.source_url)
                response.raise_for_status()

                data = response.json()

                # Save dataset
                data_file = self.dataset_dir / "reviews.json"
                data_json = json.dumps(data)
                data_file.write_text(data_json)

                # Calculate checksum
                checksum = hashlib.sha256(data_json.encode()).hexdigest()

                # Save metadata
                metadata = DatasetMetadata(
                    version="1.0",
                    checksum=checksum,
                    download_date=datetime.now().strftime("%Y-%m-%d"),
                    source_url=self.source_url,
                )
                metadata_file = self.dataset_dir / "metadata.json"
                metadata_file.write_text(metadata.model_dump_json(indent=2))

                return True

        except Exception:
            return False


def download_peerread_dataset(base_path: Path | None = None) -> bool:
    """Convenience function to download PeerRead dataset.

    Args:
        base_path: Base directory to save dataset

    Returns:
        True if download successful, False otherwise
    """
    if base_path is None:
        base_path = Path("data")

    downloader = DatasetDownloader(base_path=base_path)
    return downloader.download()


def verify_dataset(dataset_path: Path) -> bool:
    """Verify dataset completeness and integrity.

    Args:
        dataset_path: Path to dataset directory

    Returns:
        True if dataset is complete and valid, False otherwise
    """
    try:
        # Check metadata exists
        metadata_file = dataset_path / "metadata.json"
        if not metadata_file.exists():
            return False

        metadata = json.loads(metadata_file.read_text())

        # Check data files exist
        data_file = dataset_path / "reviews.json"
        if not data_file.exists():
            return False

        # Verify checksum
        data_content = data_file.read_text()
        actual_checksum = hashlib.sha256(data_content.encode()).hexdigest()

        return actual_checksum == metadata["checksum"]

    except Exception:
        return False
