import hashlib
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Set, Tuple, Optional

from .logging import Logger
from .network import RsyncHandler, RemoteFileInfo


@dataclass
class FileInfo:
    """Information about a file for comparison purposes."""
    path: Path
    size: int
    name: str
    relative_path: str
    modified_date: datetime
    checksum: Optional[str] = None
    is_remote: bool = False

    def __post_init__(self):
        """Convert modified_date to date only for comparison."""
        if isinstance(self.modified_date, datetime):
            self.modified_date = self.modified_date.date()


class FileComparator:
    """Handles file comparison operations."""

    def __init__(self, logger: Logger):
        self.logger = logger
        self.rsync_handler = RsyncHandler(logger)

    def _calculate_checksum(self, file_path: Path, chunk_size: int = 8192) -> Optional[str]:
        """Calculate SHA-256 checksum of a file."""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest()
        except Exception as e:
            self.logger.error(f"Error calculating checksum for {file_path}: {str(e)}")
            return None

    def _get_file_info(self, file_path: Path, base_path: Path) -> Optional[FileInfo]:
        """Get file information for comparison."""
        try:
            # Check if the path is a URL or remote path
            if str(file_path).startswith(('rsync://', 'ssh://', 'sftp://')):
                remote_info = self.rsync_handler.get_remote_file_info(str(file_path))
                if remote_info:
                    return FileInfo(
                        path=remote_info.path,
                        size=remote_info.size,
                        name=remote_info.name,
                        relative_path=remote_info.relative_path,
                        modified_date=remote_info.modified_date,
                        checksum=remote_info.checksum,
                        is_remote=True
                    )
                return None

            # Local file
            stat = file_path.stat()
            relative_path = str(file_path.relative_to(base_path))
            return FileInfo(
                path=file_path,
                size=stat.st_size,
                name=file_path.name,
                relative_path=relative_path,
                modified_date=datetime.fromtimestamp(stat.st_mtime),
                checksum=self._calculate_checksum(file_path)
            )
        except Exception as e:
            self.logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return None

    def compare_files(self, source_info: FileInfo, dest_info: FileInfo) -> bool:
        """
        Compare two files based on size, date, and checksum.
        Returns True if files are identical, False otherwise.
        """
        # Size comparison
        if source_info.size != dest_info.size:
            self.logger.debug(f"Size mismatch for {source_info.relative_path}")
            return False

        # Date comparison (ignoring time)
        if source_info.modified_date != dest_info.modified_date:
            self.logger.debug(f"Date mismatch for {source_info.relative_path}")
            return False

        # Checksum comparison (only if both files have checksums)
        if source_info.checksum and dest_info.checksum:
            if source_info.checksum != dest_info.checksum:
                self.logger.debug(f"Checksum mismatch for {source_info.relative_path}")
                return False

        return True

    def scan_directory(self, directory: Path) -> Dict[str, FileInfo]:
        """Scan directory and return file information dictionary."""
        file_dict = {}
        try:
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = Path(root) / file
                    try:
                        file_info = self._get_file_info(file_path, directory)
                        if file_info:
                            file_dict[file_info.relative_path] = file_info
                    except Exception as e:
                        self.logger.warning(f"Skipping file {file_path}: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error scanning directory {directory}: {str(e)}")
            raise
        return file_dict

    def compare_directories(
        self, source: Path, destination: Path
    ) -> Tuple[Set[str], Set[str], Set[str]]:
        """
        Compare source and destination directories.
        Returns: (files_to_copy, files_to_skip, conflicts)
        """
        self.logger.info(f"Starting directory comparison: {source} -> {destination}")

        source_files = self.scan_directory(source)
        dest_files = self.scan_directory(destination) if destination.exists() else {}

        files_to_copy = set()
        files_to_skip = set()
        conflicts = set()

        # Find files to copy and conflicts
        for rel_path, src_info in source_files.items():
            if rel_path not in dest_files:
                files_to_copy.add(rel_path)
            else:
                dest_info = dest_files[rel_path]
                if not self.compare_files(src_info, dest_info):
                    conflicts.add(rel_path)
                    self.logger.warning(
                        f"File mismatch for {rel_path}: "
                        f"source_size={src_info.size}, dest_size={dest_info.size}, "
                        f"source_date={src_info.modified_date}, dest_date={dest_info.modified_date}"
                    )
                else:
                    files_to_skip.add(rel_path)

        # Log summary
        self.logger.info(f"Comparison complete:")
        self.logger.info(f"Files to copy: {len(files_to_copy)}")
        self.logger.info(f"Files to skip: {len(files_to_skip)}")
        self.logger.info(f"Conflicts: {len(conflicts)}")

        return files_to_copy, files_to_skip, conflicts 