"""
Simple File Integrity Monitor (FIM)

A straightforward file integrity monitoring system that creates baselines
and verifies file changes with basic reporting.
"""

__version__ = "1.0.0"
__author__ = "File Integrity Monitor Team"
__email__ = "team@example.com"

from .core import BaselineManager
from .database import DatabaseManager
from .models import FileEvent, FileRecord

__all__ = [
    "BaselineManager", 
    "DatabaseManager",
    "FileEvent",
    "FileRecord",
    "__version__",
]
