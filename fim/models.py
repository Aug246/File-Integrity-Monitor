"""
Data models for File Integrity Monitor.
"""

import hashlib
import os
import stat
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass, field


class EventType(Enum):
    """Types of file system events that can be detected."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"
    PERMISSION_CHANGED = "permission_changed"
    OWNER_CHANGED = "owner_changed"
    BASELINE = "baseline"


@dataclass
class FileRecord:
    """Represents a file record in the baseline or current state."""
    file_path: str
    file_hash: str
    file_size: int
    mtime: float
    ctime: float
    permissions: int
    owner: str
    group: str
    inode: int
    device: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
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
                ctime=stat_info.st_ctime,
                permissions=stat_info.st_mode,
                owner=owner,
                group=group,
                inode=stat_info.st_ino,
                device=stat_info.st_dev,
            )
        except (OSError, IOError) as e:
            raise ValueError(f"Could not read file {file_path}: {e}")
    
    @staticmethod
    def _calculate_hash(file_path: str, algorithm: str = "sha256") -> str:
        """Calculate hash of a file using the specified algorithm."""
        hash_obj = hashlib.new(algorithm)
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
        except (OSError, IOError):
            # Return empty hash for inaccessible files
            return ""
        
        return hash_obj.hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "file_path": self.file_path,
            "file_hash": self.file_hash,
            "file_size": self.file_size,
            "mtime": self.mtime,
            "ctime": self.ctime,
            "permissions": self.permissions,
            "owner": self.owner,
            "group": self.group,
            "inode": self.inode,
            "device": self.device,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileRecord":
        """Create FileRecord from dictionary."""
        return cls(
            file_path=data["file_path"],
            file_hash=data["file_hash"],
            file_size=data["file_size"],
            mtime=data["mtime"],
            ctime=data["ctime"],
            permissions=data["permissions"],
            owner=data["owner"],
            group=data["group"],
            inode=data["inode"],
            device=data["device"],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


@dataclass
class FileEvent:
    """Represents a file system event that was detected."""
    event_id: str
    event_type: EventType
    file_path: str
    timestamp: datetime
    agent_id: str
    previous_hash: Optional[str] = None
    current_hash: Optional[str] = None
    file_size: Optional[int] = None
    permissions: Optional[int] = None
    owner: Optional[str] = None
    group: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Generate event ID if not provided."""
        if not self.event_id:
            import uuid
            self.event_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "file_path": self.file_path,
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "previous_hash": self.previous_hash,
            "current_hash": self.current_hash,
            "file_size": self.file_size,
            "permissions": self.permissions,
            "owner": self.owner,
            "group": self.group,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FileEvent":
        """Create FileEvent from dictionary."""
        return cls(
            event_id=data["event_id"],
            event_type=EventType(data["event_type"]),
            file_path=data["file_path"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            agent_id=data["agent_id"],
            previous_hash=data.get("previous_hash"),
            current_hash=data.get("current_hash"),
            file_size=data.get("file_size"),
            permissions=data.get("permissions"),
            owner=data.get("owner"),
            group=data.get("group"),
            metadata=data.get("metadata", {}),
        )
