# Baesync

Baesync is a simple purpose-built command-line tool for copying files and directories.

## Features
- File comparison based on size and path, ignoring timestamp
- Detailed logging of transfer operations
- Should work on all platforms
- Compares files before 

## Installation

1. Clone this repository or download the files
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

Or install directly from PyPI:
```bash
pip install baesync
```

## Usage

### Basic Usage

Copy a single file:
```bash
baesync source_file.txt destination_file.txt
```

Copy a directory (recursively):
```bash
baesync --recursive source_directory/ destination_directory/
```

### Options

- `--overwrite`, `-o`: Overwrite existing files
- `--recursive`, `-r`: Copy directories recursively
- `--log-file`, `-l`: Specify custom log file path (default: baesync_transfer.log)

### Examples

1. Copy a file with overwrite:
```bash
baesync source.txt dest.txt --overwrite
```

2. Copy a directory recursively:
```bash
baesync --recursive source_dir/ dest_dir/
```

3. Copy a directory recursively with overwrite and custom log:
```bash
baesync --recursive --overwrite source_dir/ dest_dir/ --log_file custom.log
```

## File Comparison

Baesync performs intelligent file comparison before copying:
- Compares file sizes to detect changes
- Identifies new files that need to be copied
- Detects conflicts when files have different sizes
- Skips identical files to save time
- Logs all comparison results

## Error Handling

The tool provides clear error messages and warnings:
- Yellow warnings for existing files
- Red error messages for failed operations
- Green success messages for completed operations
- Detailed logging of all operations
- Progress tracking for large transfers

## Performance Features

- Parallel file copying using ThreadPoolExecutor
- Chunk-based file copying for progress tracking
- Efficient directory scanning
- Smart file comparison to avoid unnecessary copies
- Progress bars for both single files and directories

## Testing

Run the test suite:
```bash
pytest tests/
```

The test suite includes:
- File copying tests
- Directory copying tests
- File comparison tests
- Cross-platform path handling tests
- Progress tracking tests

## Requirements

- Python 3.6+
- click
- rich
- pytest (for testing) 