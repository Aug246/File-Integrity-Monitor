"""
Simplified command-line interface for File Integrity Monitor.
"""

import os
import sys
import logging
from pathlib import Path
import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from typing import Optional

from .core import BaselineManager
from .database import DatabaseManager

console = Console()


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
def main(verbose: bool):
    """Simple File Integrity Monitor - Baseline creation and verification."""
    setup_logging(verbose)


@main.command()
@click.option('--path', '-p', required=True, help='Path to create baseline for')
@click.option('--exclude', '-e', multiple=True, help='File patterns to exclude (e.g., *.tmp)')
@click.option('--db', default='fim.db', help='Database file path')
def init(path: str, exclude: tuple, db: str):
    """Create initial baseline for specified path."""
    try:
        console.print(f"[bold blue]Creating baseline for: {path}[/bold blue]")
        
        # Initialize database and baseline manager
        database = DatabaseManager(db)
        baseline_manager = BaselineManager(database)
        
        # Convert exclude tuple to list
        exclude_patterns = list(exclude) if exclude else None
        
        # Create baseline with progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Creating baseline...", total=None)
            
            file_records = baseline_manager.create_baseline(path, exclude_patterns)
            
            progress.update(task, description="Baseline created successfully!")
        
        # Display results
        table = Table(title="Baseline Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="magenta")
        
        table.add_row("Path", path)
        table.add_row("Files Processed", str(len(file_records)))
        table.add_row("Database", db)
        table.add_row("Exclusions", str(len(exclude_patterns)) if exclude_patterns else "None")
        
        console.print(table)
        console.print(f"[green]✓ Baseline created successfully with {len(file_records)} files[/green]")
        
    except Exception as e:
        console.print(f"[red]Error creating baseline: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--path', '-p', required=True, help='Path to verify')
@click.option('--db', default='fim.db', help='Database file path')
@click.option('--format', 'output_format', default='table', 
              type=click.Choice(['table', 'json', 'csv']), help='Output format')
def verify(path: str, db: str, output_format: str):
    """Verify current state against baseline."""
    try:
        console.print(f"[bold blue]Verifying baseline for: {path}[/bold blue]")
        
        # Initialize database and baseline manager
        database = DatabaseManager(db)
        baseline_manager = BaselineManager(database)
        
        # Verify baseline
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Verifying files...", total=None)
            
            results = baseline_manager.verify_baseline(path)
            
            progress.update(task, description="Verification complete!")
        
        # Display results
        if output_format == 'json':
            import json
            console.print(json.dumps(results, indent=2))
        elif output_format == 'csv':
            console.print("Path,Status")
            for file_path in results['created']:
                console.print(f"{file_path},created")
            for file_path in results['modified']:
                console.print(f"{file_path},modified")
            for file_path in results['deleted']:
                console.print(f"{file_path},deleted")
        else:
            # Table format (default)
            table = Table(title="Verification Results")
            table.add_column("Status", style="cyan")
            table.add_column("Count", style="magenta")
            table.add_column("Files", style="green")
            
            table.add_row("Created", str(len(results['created'])), 
                         '\n'.join(results['created'][:5]) + ('...' if len(results['created']) > 5 else ''))
            table.add_row("Modified", str(len(results['modified'])), 
                         '\n'.join(results['modified'][:5]) + ('...' if len(results['modified']) > 5 else ''))
            table.add_row("Deleted", str(len(results['deleted'])), 
                         '\n'.join(results['deleted'][:5]) + ('...' if len(results['deleted']) > 5 else ''))
            table.add_row("Unchanged", str(len(results['unchanged'])), "")
            
            console.print(table)
            
            # Show summary
            total_changes = len(results['created']) + len(results['modified']) + len(results['deleted'])
            if total_changes == 0:
                console.print("[green]✓ No changes detected - all files match baseline[/green]")
            else:
                console.print(f"[yellow]⚠ {total_changes} changes detected[/yellow]")
        
    except Exception as e:
        console.print(f"[red]Error during verification: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--format', 'output_format', default='json', 
              type=click.Choice(['json', 'csv']), help='Export format')
@click.option('--output', '-o', help='Output file path (defaults to stdout)')
@click.option('--db', default='fim.db', help='Database file path')
def export(output_format: str, output: Optional[str], db: str):
    """Export database data."""
    try:
        console.print(f"[bold blue]Exporting database: {db}[/bold blue]")
        
        # Initialize database
        database = DatabaseManager(db)
        
        # Export data
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Exporting data...", total=None)
            
            data = database.export_data(output_format)
            
            progress.update(task, description="Export complete!")
        
        # Output data
        if output:
            with open(output, 'w') as f:
                f.write(data)
            console.print(f"[green]✓ Data exported to: {output}[/green]")
        else:
            console.print(data)
        
    except Exception as e:
        console.print(f"[red]Error exporting data: {e}[/red]")
        sys.exit(1)


@main.command()
@click.option('--db', default='fim.db', help='Database file path')
def status(db: str):
    """Show monitoring status and recent events."""
    try:
        console.print(f"[bold blue]File Integrity Monitor Status[/bold blue]")
        
        # Initialize database
        database = DatabaseManager(db)
        
        # Get statistics
        baseline_count = len(database.get_baseline())
        recent_events = database.get_events(limit=10)
        
        # Status table
        status_table = Table(title="System Status")
        status_table.add_column("Metric", style="cyan")
        status_table.add_column("Value", style="magenta")
        
        status_table.add_row("Database", db)
        status_table.add_row("Baseline Files", str(baseline_count))
        status_table.add_row("Recent Events", str(len(recent_events)))
        
        console.print(status_table)
        
        # Recent events table
        if recent_events:
            events_table = Table(title="Recent Events")
            events_table.add_column("Timestamp", style="cyan")
            events_table.add_column("Type", style="yellow")
            events_table.add_column("File", style="green")
            events_table.add_column("Agent", style="blue")
            
            for event in recent_events:
                events_table.add_row(
                    event.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    event.event_type.value,
                    event.file_path,
                    event.agent_id
                )
            
            console.print(events_table)
        
    except Exception as e:
        console.print(f"[red]Error checking status: {e}[/red]")
        sys.exit(1)


@main.command()
def version():
    """Show version information."""
    from . import __version__
    console.print(f"[bold blue]File Integrity Monitor v{__version__}[/bold blue]")
    console.print("Simple file change detection and monitoring")


if __name__ == '__main__':
    main()
