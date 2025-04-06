import logging
from pathlib import Path


class Logger:
    """Handles all logging operations for the application."""

    def __init__(self, log_file: str = "baesync_transfer.log"):
        self.logger = self._setup_logger(log_file)

    def _setup_logger(self, log_file: str) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger("Baesync")
        logger.setLevel(logging.INFO)

        # File handler
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    def info(self, message: str):
        """Log an info message."""
        self.logger.info(message)

    def warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(message)

    def error(self, message: str):
        """Log an error message."""
        self.logger.error(message)

    def debug(self, message: str):
        """Log a debug message."""
        self.logger.debug(message)

    def log_transfer_start(self, source: Path, destination: Path):
        """Log the start of a transfer operation."""
        self.info(f"Starting transfer from {source} to {destination}")
        self.info(f"Source exists: {source.exists()}")
        self.info(f"Destination exists: {destination.exists()}")

    def log_transfer_complete(self, success: bool, error: str = None):
        """Log the completion of a transfer operation."""
        if success:
            self.info("Transfer completed successfully")
        else:
            self.error(f"Transfer failed: {error}")

    def log_file_transfer(self, file_path: str, success: bool, error: str = None):
        """Log individual file transfer status."""
        if success:
            self.info(f"Successfully transferred: {file_path}")
        else:
            self.error(f"Failed to transfer {file_path}: {error}") 