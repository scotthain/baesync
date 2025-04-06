#!/usr/bin/env python3
import os
from pathlib import Path

import click
from rich.console import Console

from .comparator import FileComparator
from .logging import Logger
from .network import RsyncHandler

console = Console()


@click.command()
@click.argument("source", type=click.Path(exists=True))
@click.argument("destination", type=click.Path())
@click.option("--overwrite", "-o", is_flag=True, help="Overwrite existing files")
@click.option("--recursive", "-r", is_flag=True, help="Copy directories recursively")
@click.option("--log-file", "-l", default="baesync_transfer.log", help="Log file path")
@click.option("--preserve-permissions", "-p", is_flag=True, help="Preserve file permissions")
@click.option("--preserve-times", "-t", is_flag=True, help="Preserve modification times")
@click.option("--preserve-owner", "-O", is_flag=True, help="Preserve file owner")
@click.option("--preserve-group", "-g", is_flag=True, help="Preserve file group")
@click.option("--delete", "-d", is_flag=True, help="Delete extraneous files from destination")
def cli(source: str, destination: str, overwrite: bool, recursive: bool, log_file: str,
        preserve_permissions: bool, preserve_times: bool,
        preserve_owner: bool, preserve_group: bool, delete: bool):
    """
    Baesync - A simple and efficient file copying tool using rsync.

    SOURCE: Source file or directory to copy
    DESTINATION: Destination path where to copy the file/directory
    """
    src_path = Path(source)
    dst_path = Path(destination)

    # Initialize logger and file comparator
    logger = Logger(log_file)
    comparator = FileComparator(logger)
    rsync_handler = RsyncHandler(logger)

    console.print("[bold blue]Baesync - File Copy Tool[/bold blue]")

    # Log transfer start
    logger.log_transfer_start(src_path, dst_path)

    try:
        # Use rsync for file transfer
        console.print("[bold green]Using rsync for file transfer[/bold green]")
        
        # Convert paths to strings for rsync
        src_str = str(src_path)
        dst_str = str(dst_path)
        
        # For directories, check for conflicts if not overwriting
        if src_path.is_dir() and not overwrite:
            files_to_copy, files_to_skip, conflicts = comparator.compare_directories(
                src_path, dst_path
            )
            
            if conflicts:
                console.print("[yellow]Conflicts detected. Use --overwrite to proceed.[/yellow]")
                return
        
        # Sync files using rsync
        success, error = rsync_handler.sync_files(
            source=src_str,
            destination=dst_str,
            delete=delete,
            preserve_permissions=preserve_permissions,
            preserve_times=preserve_times,
            preserve_owner=preserve_owner,
            preserve_group=preserve_group,
            recursive=recursive or src_path.is_dir(),
            progress=True
        )
        
        if success:
            console.print("[green]Rsync completed successfully![/green]")
            logger.log_transfer_complete(True)
        else:
            console.print(f"[red]Rsync failed: {error}[/red]")
            logger.log_transfer_complete(False, error)

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        logger.log_transfer_complete(False, str(e))


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
