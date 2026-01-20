"""Dataset downloader for PeerRead dataset."""

import hashlib
import json
from datetime import datetime
from pathlib import Path

import httpx
from pydantic import BaseModel, Field


class DatasetMetadata(BaseModel):
    """Metadata for downloaded dataset."""

    version: str
    source_url: str
    checksum: str
    download_date: str
    file_count: int = Field(..., ge=0)


class DatasetDownloader:
    """Download and manage PeerRead dataset with versioning."""

    METADATA_FILENAME = "metadata.json"

    def __init__(self, output_dir: Path):
        """Initialize downloader with output directory.

        Args:
            output_dir: Directory to save downloaded dataset
        """
        self.output_dir = output_dir

    def download(self, url: str) -> Path:
        """Download dataset from URL to local storage.

        Args:
            url: URL to download dataset from

        Returns:
            Path: Path to downloaded file

        Raises:
            Exception: If download fails
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        response = httpx.get(url)
        response.raise_for_status()

        filename = Path(url).name
        output_path = self.output_dir / filename
        output_path.write_bytes(response.content)

        return output_path

    def compute_checksum(self, file_path: Path) -> str:
        """Compute SHA256 checksum for file.

        Args:
            file_path: Path to file to checksum

        Returns:
            str: Hex digest of SHA256 checksum
        """
        sha256 = hashlib.sha256()
        sha256.update(file_path.read_bytes())
        return sha256.hexdigest()

    def save_metadata(self, metadata: DatasetMetadata) -> None:
        """Save dataset metadata to JSON file.

        Args:
            metadata: Metadata to save
        """
        metadata_file = self.output_dir / self.METADATA_FILENAME
        metadata_file.write_text(metadata.model_dump_json(indent=2))

    def count_dataset_files(self) -> int:
        """Count number of dataset files in output directory.

        Returns:
            int: Number of JSON files in directory (excluding metadata.json)
        """
        json_files = [f for f in self.output_dir.glob("*.json") if f.name != self.METADATA_FILENAME]
        return len(json_files)

    def load_metadata(self) -> DatasetMetadata:
        """Load metadata from existing metadata.json file.

        Returns:
            DatasetMetadata: Loaded metadata

        Raises:
            FileNotFoundError: If metadata file doesn't exist
        """
        metadata_file = self.output_dir / self.METADATA_FILENAME
        metadata_data = json.loads(metadata_file.read_text())
        return DatasetMetadata(**metadata_data)

    def download_and_save(self, url: str, version: str) -> DatasetMetadata:
        """Download dataset and save with metadata.

        Args:
            url: URL to download from
            version: Version string for dataset

        Returns:
            DatasetMetadata: Metadata for downloaded dataset
        """
        dataset_path = self.download(url)
        checksum = self.compute_checksum(dataset_path)
        file_count = self.count_dataset_files()

        metadata = DatasetMetadata(
            version=version,
            source_url=url,
            checksum=checksum,
            download_date=datetime.now().strftime("%Y-%m-%d"),
            file_count=file_count,
        )

        self.save_metadata(metadata)
        return metadata
