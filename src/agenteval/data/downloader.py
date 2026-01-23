"""PeerRead dataset downloader with versioning and checksums.

This module provides functionality to download the PeerRead dataset,
save it locally with versioning, and verify integrity using checksums.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path

import httpx
from pydantic import BaseModel


class DatasetMetadata(BaseModel):
    """Metadata for dataset versioning and integrity verification."""

    version: str
    checksum: str
    download_date: str
    source_url: str


class DatasetDownloader:
    """Downloads and manages PeerRead dataset with versioning."""

    def __init__(
        self,
        base_path: Path,
        source_url: str = "https://api.github.com/repos/allenai/PeerRead/contents/data",
    ) -> None:
        """Initialize downloader with base storage path.

        Args:
            base_path: Directory where dataset will be stored
            source_url: URL to download dataset from
        """
        self.base_path = base_path
        self.source_url = source_url

    def download(self) -> bool:
        """Download PeerRead dataset from source.

        Returns:
            True if download successful, False otherwise
        """
        try:
            dataset_dir = self.base_path / "peerread"
            dataset_dir.mkdir(parents=True, exist_ok=True)

            with httpx.Client() as client:
                response = client.get(self.source_url)
                response.raise_for_status()
                data = response.json()

            data_json = json.dumps(data)
            reviews_file = dataset_dir / "reviews.json"
            reviews_file.write_text(data_json)

            checksum = hashlib.sha256(data_json.encode()).hexdigest()
            metadata = DatasetMetadata(
                version="1.0",
                checksum=checksum,
                download_date=datetime.now().isoformat(),
                source_url=self.source_url,
            )

            metadata_file = dataset_dir / "metadata.json"
            metadata_file.write_text(metadata.model_dump_json(indent=2))

            return True
        except Exception:
            return False


def download_peerread_dataset(base_path: Path) -> bool:
    """Convenience function to download PeerRead dataset.

    Args:
        base_path: Directory where dataset will be stored

    Returns:
        True if download successful, False otherwise
    """
    downloader = DatasetDownloader(base_path=base_path)
    return downloader.download()


def verify_dataset(dataset_path: Path) -> bool:
    """Verify dataset completeness and checksum integrity.

    Args:
        dataset_path: Path to dataset directory

    Returns:
        True if verification passes, False otherwise
    """
    try:
        metadata_file = dataset_path / "metadata.json"
        if not metadata_file.exists():
            return False

        metadata = json.loads(metadata_file.read_text())

        data_files = list(dataset_path.glob("*.json"))
        data_files = [f for f in data_files if f.name != "metadata.json"]

        if not data_files:
            return False

        reviews_file = dataset_path / "reviews.json"
        if not reviews_file.exists():
            return False

        data_content = reviews_file.read_text()
        actual_checksum = hashlib.sha256(data_content.encode()).hexdigest()

        expected_checksum = metadata.get("checksum")
        if actual_checksum != expected_checksum:
            return False

        return True
    except Exception:
        return False
