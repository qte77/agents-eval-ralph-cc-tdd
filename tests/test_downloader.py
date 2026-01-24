"""Tests for PeerRead dataset downloader.

Tests verify downloading, saving, versioning, checksum validation, and completeness checks.
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from agenteval.data.downloader import (
    DatasetDownloader,
    DatasetMetadata,
    download_peerread_dataset,
    verify_dataset,
)


def test_dataset_downloader_downloads_from_source(tmp_path: Path):
    """Test that downloader can download dataset from source URL."""
    downloader = DatasetDownloader(base_path=tmp_path)

    with patch("httpx.Client") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 1,
                "title": "Test Paper",
                "abstract": "Test abstract",
                "accepted": True,
                "reviews": [],
            }
        ]
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = downloader.download()

        assert result is True
        assert (tmp_path / "peerread").exists()


def test_dataset_saves_in_structured_format(tmp_path: Path):
    """Test that dataset is saved in structured directory format."""
    downloader = DatasetDownloader(base_path=tmp_path)

    with patch("httpx.Client") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1, "title": "Test"}]
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        downloader.download()

        dataset_dir = tmp_path / "peerread"
        assert dataset_dir.exists()
        assert dataset_dir.is_dir()
        # Should have data files in structured format
        assert len(list(dataset_dir.glob("*.json"))) > 0


def test_dataset_metadata_has_version_and_checksum():
    """Test that DatasetMetadata model includes version and checksum fields."""
    metadata = DatasetMetadata(
        version="1.0",
        checksum="abc123",
        download_date="2026-01-21",
        source_url="https://example.com/data",
    )

    assert metadata.version == "1.0"
    assert metadata.checksum == "abc123"
    assert metadata.download_date == "2026-01-21"
    assert metadata.source_url == "https://example.com/data"


def test_downloader_saves_metadata_file(tmp_path: Path):
    """Test that downloader saves metadata.json with version and checksum."""
    downloader = DatasetDownloader(base_path=tmp_path)

    with patch("httpx.Client") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1}]
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        downloader.download()

        metadata_file = tmp_path / "peerread" / "metadata.json"
        assert metadata_file.exists()

        import json
        metadata = json.loads(metadata_file.read_text())
        assert "version" in metadata
        assert "checksum" in metadata
        assert "download_date" in metadata


def test_verify_dataset_checks_completeness(tmp_path: Path):
    """Test that verify_dataset checks for required files and validates checksums."""
    dataset_path = tmp_path / "peerread"
    dataset_path.mkdir(parents=True)

    # Create mock data files
    (dataset_path / "reviews.json").write_text('[{"id": 1}]')

    # Create metadata file
    import json
    import hashlib

    data = '[{"id": 1}]'
    checksum = hashlib.sha256(data.encode()).hexdigest()

    metadata = {
        "version": "1.0",
        "checksum": checksum,
        "download_date": "2026-01-21",
        "source_url": "https://example.com",
    }
    (dataset_path / "metadata.json").write_text(json.dumps(metadata))

    # Verification should pass
    result = verify_dataset(dataset_path)
    assert result is True


def test_verify_dataset_fails_on_checksum_mismatch(tmp_path: Path):
    """Test that verify_dataset fails when checksum doesn't match."""
    dataset_path = tmp_path / "peerread"
    dataset_path.mkdir(parents=True)

    # Create mock data files
    (dataset_path / "reviews.json").write_text('[{"id": 1}]')

    # Create metadata with wrong checksum
    import json

    metadata = {
        "version": "1.0",
        "checksum": "wrong_checksum",
        "download_date": "2026-01-21",
        "source_url": "https://example.com",
    }
    (dataset_path / "metadata.json").write_text(json.dumps(metadata))

    # Verification should fail
    result = verify_dataset(dataset_path)
    assert result is False


def test_verify_dataset_fails_on_missing_files(tmp_path: Path):
    """Test that verify_dataset fails when required files are missing."""
    dataset_path = tmp_path / "peerread"
    dataset_path.mkdir(parents=True)

    # Only create metadata, no data files
    import json

    metadata = {
        "version": "1.0",
        "checksum": "abc123",
        "download_date": "2026-01-21",
        "source_url": "https://example.com",
    }
    (dataset_path / "metadata.json").write_text(json.dumps(metadata))

    # Verification should fail due to missing data files
    result = verify_dataset(dataset_path)
    assert result is False


def test_download_peerread_dataset_convenience_function(tmp_path: Path):
    """Test convenience function for downloading PeerRead dataset."""
    with patch("httpx.Client") as mock_client:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [{"id": 1}]
        mock_client.return_value.__enter__.return_value.get.return_value = mock_response

        result = download_peerread_dataset(base_path=tmp_path)

        assert result is True
        assert (tmp_path / "peerread").exists()


def test_downloader_handles_network_errors(tmp_path: Path):
    """Test that downloader handles network errors gracefully."""
    downloader = DatasetDownloader(base_path=tmp_path)

    with patch("httpx.Client") as mock_client:
        mock_client.return_value.__enter__.return_value.get.side_effect = Exception(
            "Network error"
        )

        result = downloader.download()

        assert result is False
