"""Tests for dataset downloader."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from agenteval.data.downloader import DatasetDownloader

pytestmark = pytest.mark.anyio


def test_downloader_initialization():
    """Test that downloader can be initialized with config."""
    downloader = DatasetDownloader(
        source_url="https://github.com/allenai/PeerRead", local_path="data/peerread"
    )

    assert downloader.source_url == "https://github.com/allenai/PeerRead"
    assert downloader.local_path == Path("data/peerread")


async def test_download_dataset_creates_directory(tmp_path):
    """Test that download creates local directory structure."""
    downloader = DatasetDownloader(
        source_url="https://example.com/dataset", local_path=str(tmp_path / "test_dataset")
    )

    with patch("agenteval.data.downloader.httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = b"test content"
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        await downloader.download()

    assert downloader.local_path.exists()


async def test_download_dataset_saves_files(tmp_path):
    """Test that download saves dataset files locally."""
    downloader = DatasetDownloader(
        source_url="https://example.com/dataset", local_path=str(tmp_path / "test_dataset")
    )

    # Mock HTTP responses for file downloads
    mock_file_content = b'{"paper": "test data"}'

    with patch("agenteval.data.downloader.httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = mock_file_content
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        await downloader.download()

    # Verify files were saved
    assert any(downloader.local_path.rglob("*.json"))


async def test_download_generates_checksum_file(tmp_path):
    """Test that download generates checksums for integrity verification."""
    downloader = DatasetDownloader(
        source_url="https://example.com/dataset", local_path=str(tmp_path / "test_dataset")
    )

    with patch("agenteval.data.downloader.httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = b'{"test": "data"}'
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        await downloader.download()

    # Check for checksum file
    checksum_file = downloader.local_path / "checksums.json"
    assert checksum_file.exists()


async def test_verify_dataset_integrity(tmp_path):
    """Test that verify checks dataset integrity using checksums."""
    downloader = DatasetDownloader(
        source_url="https://example.com/dataset", local_path=str(tmp_path / "test_dataset")
    )

    # Create test files and checksums
    downloader.local_path.mkdir(parents=True)
    test_file = downloader.local_path / "test.json"
    test_file.write_text('{"test": "data"}')

    checksum_file = downloader.local_path / "checksums.json"
    import hashlib

    file_hash = hashlib.sha256(test_file.read_bytes()).hexdigest()
    checksum_file.write_text(f'{{"test.json": "{file_hash}"}}')

    # Verify should pass
    result = await downloader.verify()
    assert result is True


async def test_verify_fails_on_corrupted_data(tmp_path):
    """Test that verify detects corrupted dataset files."""
    downloader = DatasetDownloader(
        source_url="https://example.com/dataset", local_path=str(tmp_path / "test_dataset")
    )

    # Create test file with mismatched checksum
    downloader.local_path.mkdir(parents=True)
    test_file = downloader.local_path / "test.json"
    test_file.write_text('{"test": "data"}')

    checksum_file = downloader.local_path / "checksums.json"
    checksum_file.write_text('{"test.json": "wrong_checksum_value"}')

    # Verify should fail
    result = await downloader.verify()
    assert result is False


async def test_download_creates_version_metadata(tmp_path):
    """Test that download creates version metadata file."""
    downloader = DatasetDownloader(
        source_url="https://example.com/dataset", local_path=str(tmp_path / "test_dataset")
    )

    with patch("agenteval.data.downloader.httpx.AsyncClient") as mock_client:
        mock_response = AsyncMock()
        mock_response.status_code = 200
        mock_response.content = b'{"test": "data"}'
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response

        await downloader.download()

    # Check for version metadata
    version_file = downloader.local_path / "version.json"
    assert version_file.exists()

    import json

    version_data = json.loads(version_file.read_text())
    assert "downloaded_at" in version_data
    assert "source_url" in version_data


async def test_download_handles_network_errors():
    """Test that download handles network errors gracefully."""
    downloader = DatasetDownloader(
        source_url="https://invalid.example.com/dataset", local_path="data/test"
    )

    with patch("agenteval.data.downloader.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.side_effect = Exception(
            "Network error"
        )

        with pytest.raises(Exception):
            await downloader.download()


def test_get_dataset_info_returns_metadata(tmp_path):
    """Test that get_dataset_info returns version and checksum metadata."""
    downloader = DatasetDownloader(
        source_url="https://example.com/dataset", local_path=str(tmp_path / "test_dataset")
    )

    # Create metadata files
    downloader.local_path.mkdir(parents=True)
    version_file = downloader.local_path / "version.json"
    version_file.write_text(
        '{"downloaded_at": "2026-01-21", "source_url": "https://example.com/dataset"}'
    )

    info = downloader.get_dataset_info()

    assert info is not None
    assert "downloaded_at" in info
    assert info["source_url"] == "https://example.com/dataset"
