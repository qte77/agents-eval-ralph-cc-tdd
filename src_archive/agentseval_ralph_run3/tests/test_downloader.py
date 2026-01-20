"""Tests for PeerRead dataset downloader.

Following TDD approach - these tests should FAIL initially.
Tests validate dataset downloading, persistence, versioning, and integrity.
"""

import hashlib
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from agenteval.data.downloader import DatasetDownloader, DatasetMetadata


def test_downloader_initialization():
    """Test DatasetDownloader can be initialized with output directory."""
    downloader = DatasetDownloader(output_dir=Path("data/peerread"))
    assert downloader.output_dir == Path("data/peerread")
    assert isinstance(downloader, DatasetDownloader)


def test_dataset_metadata_model():
    """Test DatasetMetadata Pydantic model has required fields."""
    metadata = DatasetMetadata(
        version="1.0.0",
        source_url="https://example.com/dataset.zip",
        checksum="abc123",
        download_date="2026-01-19",
        file_count=100,
    )
    assert metadata.version == "1.0.0"
    assert metadata.source_url == "https://example.com/dataset.zip"
    assert metadata.checksum == "abc123"
    assert metadata.file_count == 100


def test_download_creates_output_directory(tmp_path: Path):
    """Test that download creates output directory if it doesn't exist."""
    output_dir = tmp_path / "peerread"
    downloader = DatasetDownloader(output_dir=output_dir)

    with patch("agenteval.data.downloader.httpx.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = b"fake dataset content"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        downloader.download(url="https://example.com/dataset.zip")
        assert output_dir.exists()


def test_download_saves_dataset_locally(tmp_path: Path):
    """Test that download saves dataset to local storage."""
    output_dir = tmp_path / "peerread"
    downloader = DatasetDownloader(output_dir=output_dir)

    fake_content = b"fake dataset content"
    with patch("agenteval.data.downloader.httpx.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = fake_content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result_path = downloader.download(url="https://example.com/dataset.zip")
        assert result_path.exists()
        assert result_path.read_bytes() == fake_content


def test_compute_checksum_for_file(tmp_path: Path):
    """Test checksum computation for downloaded file."""
    test_file = tmp_path / "test.txt"
    test_content = b"test content for checksum"
    test_file.write_bytes(test_content)

    downloader = DatasetDownloader(output_dir=tmp_path)
    checksum = downloader.compute_checksum(test_file)

    expected_checksum = hashlib.sha256(test_content).hexdigest()
    assert checksum == expected_checksum
    assert len(checksum) == 64  # SHA256 produces 64 hex characters


def test_save_metadata_to_json(tmp_path: Path):
    """Test saving dataset metadata to JSON file."""
    output_dir = tmp_path / "peerread"
    output_dir.mkdir()
    downloader = DatasetDownloader(output_dir=output_dir)

    metadata = DatasetMetadata(
        version="1.0.0",
        source_url="https://example.com/dataset.zip",
        checksum="abc123def456",
        download_date="2026-01-19",
        file_count=50,
    )

    downloader.save_metadata(metadata)

    metadata_file = output_dir / "metadata.json"
    assert metadata_file.exists()

    loaded_data = json.loads(metadata_file.read_text())
    assert loaded_data["version"] == "1.0.0"
    assert loaded_data["checksum"] == "abc123def456"
    assert loaded_data["file_count"] == 50


def test_verify_dataset_completeness(tmp_path: Path):
    """Test verification of dataset completeness after download."""
    output_dir = tmp_path / "peerread"
    output_dir.mkdir()

    # Create some fake dataset files
    (output_dir / "file1.json").write_text('{"paper": "data"}')
    (output_dir / "file2.json").write_text('{"paper": "data"}')
    (output_dir / "file3.json").write_text('{"paper": "data"}')

    downloader = DatasetDownloader(output_dir=output_dir)
    file_count = downloader.count_dataset_files()

    assert file_count == 3


def test_load_existing_metadata(tmp_path: Path):
    """Test loading metadata from existing metadata.json file."""
    output_dir = tmp_path / "peerread"
    output_dir.mkdir()

    metadata_file = output_dir / "metadata.json"
    metadata_data = {
        "version": "1.0.0",
        "source_url": "https://example.com/dataset.zip",
        "checksum": "def789",
        "download_date": "2026-01-19",
        "file_count": 25,
    }
    metadata_file.write_text(json.dumps(metadata_data))

    downloader = DatasetDownloader(output_dir=output_dir)
    metadata = downloader.load_metadata()

    assert metadata.version == "1.0.0"
    assert metadata.checksum == "def789"
    assert metadata.file_count == 25


def test_verify_checksum_matches(tmp_path: Path):
    """Test checksum verification against stored metadata."""
    output_dir = tmp_path / "peerread"
    output_dir.mkdir()

    dataset_file = output_dir / "dataset.zip"
    content = b"dataset content"
    dataset_file.write_bytes(content)

    expected_checksum = hashlib.sha256(content).hexdigest()

    downloader = DatasetDownloader(output_dir=output_dir)
    computed_checksum = downloader.compute_checksum(dataset_file)

    assert computed_checksum == expected_checksum


def test_download_with_version(tmp_path: Path):
    """Test downloading dataset with version tracking."""
    output_dir = tmp_path / "peerread"
    downloader = DatasetDownloader(output_dir=output_dir)

    fake_content = b"versioned dataset"
    with patch("agenteval.data.downloader.httpx.get") as mock_get:
        mock_response = MagicMock()
        mock_response.content = fake_content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        metadata = downloader.download_and_save(
            url="https://example.com/dataset.zip", version="1.0.0"
        )

        assert metadata.version == "1.0.0"
        assert metadata.checksum is not None
        assert len(metadata.checksum) == 64


def test_download_fails_on_http_error(tmp_path: Path):
    """Test that download handles HTTP errors appropriately."""
    output_dir = tmp_path / "peerread"
    downloader = DatasetDownloader(output_dir=output_dir)

    with patch("agenteval.data.downloader.httpx.get") as mock_get:
        mock_get.side_effect = Exception("HTTP 404 Not Found")

        with pytest.raises(Exception):
            downloader.download(url="https://example.com/nonexistent.zip")
