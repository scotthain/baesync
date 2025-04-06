from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlparse

import os
import json
import logging
import tempfile

from .logging import Logger


@dataclass
class RemoteFileInfo:
    """Information about a remote file."""
    path: Path
    size: int
    name: str
    relative_path: str
    modified_date: datetime
    is_remote: bool = True
    checksum: Optional[str] = None


class RsyncHandler:
    """Handles rsync operations for file transfers using a Python rsync library."""

    def __init__(self, logger: Logger):
        self.logger = logger
        self._setup_rsync()

    def _setup_rsync(self):
        """Setup the rsync library."""
        try:
            # Import the rsync library
            from rsync_backup import Rsync
            self.rsync = Rsync
            self.logger.debug("Successfully imported rsync library")
        except ImportError:
            self.logger.error("rsync-backup Python library not found. Please install rsync-backup.")
            raise RuntimeError("rsync-backup Python library is required but not installed")

    def _parse_rsync_output(self, output: str) -> Dict[str, Any]:
        """Parse rsync output to extract file information."""
        try:
            # Try to parse as JSON if it's in that format
            return json.loads(output)
        except json.JSONDecodeError:
            # Fall back to text parsing
            result = {}
            for line in output.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    result[key.strip()] = value.strip()
            return result

    def get_remote_file_info(self, url: str) -> Optional[RemoteFileInfo]:
        """Get file information for a remote file using rsync."""
        try:
            # Parse the URL to get host and path
            parsed_url = urlparse(url)
            if not parsed_url.scheme or parsed_url.scheme not in ['rsync', 'ssh']:
                self.logger.error(f"Unsupported URL scheme: {parsed_url.scheme}")
                return None
                
            # Use the rsync library to get file information
            self.logger.debug(f"Getting file info for {url}")
            
            # Create a temporary file to store the output
            with tempfile.NamedTemporaryFile(mode='w+', delete=False) as temp_file:
                temp_path = temp_file.name
                
            # Use the rsync library to list files without transferring
            rsync_client = self.rsync()
            rsync_client.list_files(
                source=url,
                destination=temp_path,
                list_only=True,
                verbose=True
            )
            
            # Read the output
            with open(temp_path, 'r') as f:
                output = f.read()
                
            # Clean up the temporary file
            os.unlink(temp_path)
            
            # Parse the output
            file_info = self._parse_rsync_output(output)
            
            if not file_info:
                self.logger.error(f"Could not get file info for {url}")
                return None
                
            # Extract file information
            path = Path(file_info.get('path', ''))
            size = int(file_info.get('size', 0))
            modified = file_info.get('mtime', '')
            
            # Parse the modification time
            try:
                modified_date = datetime.fromtimestamp(float(modified))
            except (ValueError, TypeError):
                modified_date = datetime.now()
                
            # Get checksum if available
            checksum = file_info.get('checksum')
            
            return RemoteFileInfo(
                path=path,
                size=size,
                name=path.name,
                relative_path=str(path),
                modified_date=modified_date,
                checksum=checksum
            )
            
        except Exception as e:
            self.logger.error(f"Error getting remote file info for {url}: {str(e)}")
            return None

    def sync_files(self, source: str, destination: str, 
                  delete: bool = False, 
                  preserve_permissions: bool = True,
                  preserve_times: bool = True,
                  preserve_owner: bool = False,
                  preserve_group: bool = False,
                  recursive: bool = True,
                  progress: bool = True) -> Tuple[bool, str]:
        """
        Synchronize files using rsync.
        
        Args:
            source: Source path (local or remote)
            destination: Destination path (local or remote)
            delete: Delete extraneous files from destination
            preserve_permissions: Preserve permissions
            preserve_times: Preserve modification times
            preserve_owner: Preserve owner
            preserve_group: Preserve group
            recursive: Copy directories recursively
            progress: Show progress
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            self.logger.debug(f"Syncing files from {source} to {destination}")
            
            # Create rsync client
            rsync_client = self.rsync()
            
            # Configure rsync options
            options = {
                'delete': delete,
                'perms': preserve_permissions,
                'times': preserve_times,
                'owner': preserve_owner,
                'group': preserve_group,
                'recursive': recursive,
                'progress': progress,
                'verbose': True
            }
            
            # Use the rsync library to sync files
            result = rsync_client.sync(
                source=source,
                destination=destination,
                **options
            )
            
            if result.success:
                return True, ""
            else:
                return False, f"Rsync failed: {result.error}"
                
        except Exception as e:
            error_msg = f"Error during rsync operation: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg 