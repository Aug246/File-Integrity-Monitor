"""
Simplified data models for File Integrity Monitor.
"""

import hashlib
import os
from datetime import datetime
from enum import Enum
from dataclasses import dataclass


class EventType(Enum):
    """Types of file system events."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    BASELINE = "baseline"


@dataclass
class FileRecord:
    """Represents a file record in the baseline."""
    file_path: str
    file_hash: str
    file_size: int
    mtime: float
    permissions: int
    owner: str
    group: str
    
    @classmethod
    def from_path(cls, file_path: str) -> "FileRecord":
        """Create a FileRecord from a file path."""
        try:
            stat_info = os.stat(file_path)
            
            # Calculate SHA-256 hash
            file_hash = cls._calculate_hash(file_path)
            
            # Get owner and group info
            try:
                import pwd
                import grp
                owner = pwd.getpwuid(stat_info.st_uid).pw_name
                group = grp.getgrgid(stat_info.st_gid).gr_name
            except (ImportError, KeyError):
                # Fallback for Windows or missing user/group info
                owner = str(stat_info.st_uid)
                group = str(stat_info.st_gid)
            
            return cls(
                file_path=file_path,
                file_hash=file_hash,
                file_size=stat_info.st_size,
                mtime=stat_info.st_mtime,
                permissions=stat_info.st_mode,
                owner=owner,
                group=group,
            )
        except (OSError, IOError) as e:
            raise ValueError(f"Could not read file {file_path}: {e}")
    
    @staticmethod
    def _calculate_hash(file_path: str) -> str:
        """Calculate SHA-256 hash of a file."""
        hash_obj = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
        except (OSError, IOError):
            return ""
        
        return hash_obj.hexdigest()


@dataclass
class FileEvent:
    """Represents a file system event."""
    event_type: EventType
    file_path: str
    timestamp: datetime = None
    agent_id: str = "default"
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
