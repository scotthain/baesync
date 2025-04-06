import os
import shutil
import tempfile
from pathlib import Path

import pytest

from baesync.cli import copy_directory_with_progress, copy_file_with_progress
from baesync.file_utils import FileComparator, FileInfo


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def sample_file(temp_dir):
    """Create a sample file for testing."""
    file_path = temp_dir / "test.txt"
    with open(file_path, "w") as f:
        f.write("Test content")
    return file_path


@pytest.fixture
def sample_directory(temp_dir):
    """Create a sample directory structure for testing."""
    # Create directory structure
    dir_path = temp_dir / "test_dir"
    dir_path.mkdir()

    # Create some files
    (dir_path / "file1.txt").write_text("Content 1")
    (dir_path / "file2.txt").write_text("Content 2")

    # Create subdirectory
    subdir = dir_path / "subdir"
    subdir.mkdir()
    (subdir / "file3.txt").write_text("Content 3")

    return dir_path


@pytest.fixture
def mock_progress():
    """Create a mock progress bar for testing."""

    class MockProgress:
        def __init__(self):
            self.total = None
            self.advance = 0

        def update(self, task_id, total=None, advance=None):
            if total is not None:
                self.total = total
            if advance is not None:
                self.advance += advance

    return MockProgress()


def test_copy_file_with_progress(temp_dir, sample_file, mock_progress):
    """Test copying a single file with progress tracking."""
    dest_file = temp_dir / "copied.txt"

    # Copy file
    success = copy_file_with_progress(sample_file, dest_file, mock_progress, 0)

    # Verify
    assert success
    assert dest_file.exists()
    assert dest_file.read_text() == "Test content"
    assert mock_progress.total == sample_file.stat().st_size
    assert mock_progress.advance == sample_file.stat().st_size


def test_copy_directory_with_progress(temp_dir, sample_directory, mock_progress):
    """Test copying a directory with progress tracking."""
    dest_dir = temp_dir / "copied_dir"

    # Copy directory
    success = copy_directory_with_progress(sample_directory, dest_dir, mock_progress, 0)

    # Verify
    assert success
    assert dest_dir.exists()
    assert (dest_dir / "file1.txt").exists()
    assert (dest_dir / "file2.txt").exists()
    assert (dest_dir / "subdir" / "file3.txt").exists()

    # Verify content
    assert (dest_dir / "file1.txt").read_text() == "Content 1"
    assert (dest_dir / "file2.txt").read_text() == "Content 2"
    assert (dest_dir / "subdir" / "file3.txt").read_text() == "Content 3"


def test_file_comparator(temp_dir, sample_directory):
    """Test the FileComparator class."""
    comparator = FileComparator()

    # Create a slightly different copy
    diff_dir = temp_dir / "diff_dir"
    shutil.copytree(sample_directory, diff_dir)
    (diff_dir / "file1.txt").write_text("Different content")

    # Compare directories
    files_to_copy, files_to_skip, conflicts = comparator.compare_directories(
        sample_directory, diff_dir
    )

    # Verify
    assert len(files_to_copy) == 0  # All files exist
    assert len(files_to_skip) == 2  # file2.txt and subdir/file3.txt are identical
    assert len(conflicts) == 1  # file1.txt has different content


def test_file_comparator_new_files(temp_dir, sample_directory):
    """Test FileComparator with new files."""
    comparator = FileComparator()

    # Create destination with some new files
    dest_dir = temp_dir / "dest_dir"
    dest_dir.mkdir()
    (dest_dir / "new_file.txt").write_text("New content")

    # Compare directories
    files_to_copy, files_to_skip, conflicts = comparator.compare_directories(
        sample_directory, dest_dir
    )

    # Verify
    assert len(files_to_copy) == 3  # All source files need to be copied
    assert len(files_to_skip) == 0  # No identical files
    assert len(conflicts) == 0  # No conflicts


def test_cross_platform_paths(temp_dir):
    """Test handling of different path separators."""
    comparator = FileComparator()

    # Create test files with different path separators
    src_dir = temp_dir / "src"
    src_dir.mkdir()
    (src_dir / "file1.txt").write_text("Content 1")

    # Test with Windows-style path
    win_path = Path(str(src_dir).replace("/", "\\"))
    assert win_path.exists()

    # Test with Unix-style path
    unix_path = Path(str(src_dir).replace("\\", "/"))
    assert unix_path.exists()

    # Both paths should work
    assert comparator.scan_directory(win_path)
    assert comparator.scan_directory(unix_path)
