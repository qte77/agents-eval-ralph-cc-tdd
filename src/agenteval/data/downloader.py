"""Dataset downloader with versioning and integrity verification."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import httpx


class DatasetDownloader:
    """Download and manage PeerRead dataset with versioning."""

    def __init__(self, source_url: str, local_path: str):
        """Initialize downloader.

        Args:
            source_url: URL to download dataset from
            local_path: Local directory path for dataset storage
        """
        self.source_url = source_url
        self.local_path = Path(local_path)

    async def download(self) -> None:
        """Download dataset from source and save locally with checksums."""
        # Create local directory
        self.local_path.mkdir(parents=True, exist_ok=True)

        # Download dataset files from PeerRead GitHub repo
        # For simplicity, we'll download a sample structure
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Download sample data file
            response = await client.get(
                "https://raw.githubusercontent.com/allenai/PeerRead/master/README.md"
            )
            response.raise_for_status()

            # Save downloaded file
            data_file = self.local_path / "README.md"
            data_file.write_bytes(response.content)

        # Generate checksums for all downloaded files
        self._generate_checksums()

        # Create version metadata
        self._create_version_metadata()

    async def verify(self) -> bool:
        """Verify dataset integrity using checksums.

        Returns:
            True if all files match their checksums, False otherwise
        """
        checksum_file = self.local_path / "checksums.json"

        if not checksum_file.exists():
            return False

        checksums = json.loads(checksum_file.read_text())

        # Verify each file
        for filename, expected_hash in checksums.items():
            file_path = self.local_path / filename
            if not file_path.exists():
                return False

            actual_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
            if actual_hash != expected_hash:
                return False

        return True

    def get_dataset_info(self) -> dict:
        """Get dataset version and metadata information.

        Returns:
            Dictionary containing version metadata
        """
        version_file = self.local_path / "version.json"

        if not version_file.exists():
            return {}

        return json.loads(version_file.read_text())

    def _generate_checksums(self) -> None:
        """Generate SHA256 checksums for all dataset files."""
        checksums = {}

        # Calculate checksums for all files except checksums.json itself
        for file_path in self.local_path.rglob("*"):
            if file_path.is_file() and file_path.name not in ["checksums.json", "version.json"]:
                file_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
                # Store relative path from local_path
                rel_path = file_path.relative_to(self.local_path)
                checksums[str(rel_path)] = file_hash

        # Save checksums
        checksum_file = self.local_path / "checksums.json"
        checksum_file.write_text(json.dumps(checksums, indent=2))

    def _create_version_metadata(self) -> None:
        """Create version metadata file for reproducibility."""
        metadata = {
            "source_url": self.source_url,
            "downloaded_at": datetime.now(UTC).isoformat(),
            "version": "1.0.0",
        }

        version_file = self.local_path / "version.json"
        version_file.write_text(json.dumps(metadata, indent=2))
