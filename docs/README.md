# Baesync Documentation

## Overview

Baesync is a command-line tool for efficiently copying files and directories with intelligent comparison and progress tracking.

## Architecture

The application is structured as follows:

- `baesync/`: Main package directory
  - `cli.py`: Command-line interface implementation
  - `file_utils.py`: File comparison and logging utilities
  - `__init__.py`: Package initialization

## Development

### Setup

1. Clone the repository
2. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

### Testing

Run the test suite:
```bash
pytest
```

### Building

Build the package:
```bash
python -m build
```

### Code Style

The project uses:
- Black for code formatting
- isort for import sorting

Run the linters:
```bash
make lint
```

## Usage Examples

### Basic File Copy

```bash
baesync source.txt destination.txt
```

### Directory Copy with Comparison

```bash
baesync --recursive source_dir/ destination_dir/
```

### Overwriting Existing Files

```bash
baesync --recursive --overwrite source_dir/ destination_dir/
```

### Custom Log File

```bash
baesync --recursive source_dir/ destination_dir/ --log-file custom.log
``` 