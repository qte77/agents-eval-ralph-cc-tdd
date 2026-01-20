"""PeerRead dataset downloader with versioning and integrity checks."""

import hashlib
import json
from datetime import datetime
from pathlib import Path

import httpx
from pydantic import BaseModel


class DatasetMetadata(BaseModel):
    """Metadata for downloaded dataset."""

    version: str
    source_url: str
    checksum: str
    download_date: str
    file_count: int


class DatasetDownloader:
    """Download and manage PeerRead dataset with versioning."""

    def __init__(self, output_dir: Path):
        """Initialize downloader with output directory.

        Args:
            output_dir: Directory to save downloaded dataset
        """
        self.output_dir = Path(output_dir)

    def download(self, url: str) -> Path:
        """Download dataset from URL.

        Args:
            url: Source URL for dataset

        Returns:
            Path: Path to downloaded file
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        response = httpx.get(url)
        response.raise_for_status()

        filename = url.split("/")[-1]
        output_path = self.output_dir / filename
        output_path.write_bytes(response.content)

        return output_path

    def compute_checksum(self, file_path: Path) -> str:
        """Compute SHA256 checksum for file.

        Args:
            file_path: Path to file

        Returns:
            str: Hex-encoded SHA256 checksum
        """
        sha256 = hashlib.sha256()
        sha256.update(file_path.read_bytes())
        return sha256.hexdigest()

    def save_metadata(self, metadata: DatasetMetadata) -> None:
        """Save metadata to JSON file.

        Args:
            metadata: Dataset metadata to save
        """
        metadata_path = self.output_dir / "metadata.json"
        metadata_path.write_text(metadata.model_dump_json(indent=2))

    def count_dataset_files(self) -> int:
        """Count JSON files in dataset directory.

        Returns:
            int: Number of JSON files
        """
        return len(list(self.output_dir.glob("*.json")))

    def load_metadata(self) -> DatasetMetadata:
        """Load metadata from JSON file.

        Returns:
            DatasetMetadata: Loaded metadata
        """
        metadata_path = self.output_dir / "metadata.json"
        metadata_data = json.loads(metadata_path.read_text())
        return DatasetMetadata(**metadata_data)

    def download_and_save(self, url: str, version: str) -> DatasetMetadata:
        """Download dataset and save with metadata.

        Args:
            url: Source URL for dataset
            version: Dataset version string

        Returns:
            DatasetMetadata: Metadata for downloaded dataset
        """
        downloaded_path = self.download(url)
        checksum = self.compute_checksum(downloaded_path)

        metadata = DatasetMetadata(
            version=version,
            source_url=url,
            checksum=checksum,
            download_date=datetime.now().strftime("%Y-%m-%d"),
            file_count=self.count_dataset_files(),
        )

        self.save_metadata(metadata)
        return metadata
