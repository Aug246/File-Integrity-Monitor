"""
File Integrity Monitor (FIM)

A cross-platform file integrity monitoring system that detects and logs file changes
with tamper-evident records and continuous monitoring capabilities.
"""

__version__ = "1.0.0"
__author__ = "File Integrity Monitor Team"
__email__ = "team@example.com"

from .core import FileMonitor, BaselineManager
from .database import DatabaseManager
from .models import FileEvent, FileRecord

__all__ = [
    "FileMonitor",
    "BaselineManager", 
    "DatabaseManager",
    "FileEvent",
    "FileRecord",
    "__version__",
]
