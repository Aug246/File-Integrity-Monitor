"""
Unit tests for FIM data models.
"""

import os
import tempfile
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock

from fim.models import FileRecord, FileEvent, EventType


class TestFileRecord:
    """Test FileRecord class functionality."""
    
    def test_file_record_creation(self):
        """Test FileRecord creation with all fields."""
        record = FileRecord(
            file_path="/test/file.txt",
            file_hash="a" * 64,
            file_size=1024,
            mtime=1234567890.0,
            ctime=1234567890.0,
            permissions=0o644,
            owner="testuser",
            group="testgroup",
            inode=12345,
            device=67890
        )
        
        assert record.file_path == "/test/file.txt"
        assert record.file_hash == "a" * 64
        assert record.file_size == 1024
        assert record.permissions == 0o644
        assert record.owner == "testuser"
        assert record.group == "testgroup"
    
    def test_file_record_from_path(self):
        """Test FileRecord creation from file path."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"test content")
            tmp_file.flush()
            
            try:
                record = FileRecord.from_path(tmp_file.name)
                
                assert record.file_path == tmp_file.name
                assert len(record.file_hash) == 64  # SHA-256 hash length
                assert record.file_size == 12  # "test content" length
                assert record.permissions > 0
                assert record.inode > 0
                assert record.device > 0
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_file_record_from_path_nonexistent(self):
        """Test FileRecord.from_path with nonexistent file."""
        with pytest.raises(ValueError, match="Could not read file"):
            FileRecord.from_path("/nonexistent/file")
    
    def test_file_record_hash_calculation(self):
        """Test file hash calculation."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"test content")
            tmp_file.flush()
            
            try:
                # Calculate hash manually
                import hashlib
                expected_hash = hashlib.sha256(b"test content").hexdigest()
                
                # Get hash from FileRecord
                record = FileRecord.from_path(tmp_file.name)
                
                assert record.file_hash == expected_hash
                
            finally:
                os.unlink(tmp_file.name)
    
    def test_file_record_to_dict(self):
        """Test FileRecord serialization to dictionary."""
        record = FileRecord(
            file_path="/test/file.txt",
            file_hash="a" * 64,
            file_size=1024,
            mtime=1234567890.0,
            ctime=1234567890.0,
            permissions=0o644,
            owner="testuser",
            group="testgroup",
            inode=12345,
            device=67890
        )
        
        data = record.to_dict()
        
        assert data["file_path"] == "/test/file.txt"
        assert data["file_hash"] == "a" * 64
        assert data["file_size"] == 1024
        assert data["permissions"] == 0o644
        assert data["owner"] == "testuser"
        assert data["group"] == "testgroup"
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_file_record_from_dict(self):
        """Test FileRecord deserialization from dictionary."""
        data = {
            "file_path": "/test/file.txt",
            "file_hash": "a" * 64,
            "file_size": 1024,
            "mtime": 1234567890.0,
            "ctime": 1234567890.0,
            "permissions": 0o644,
            "owner": "testuser",
            "group": "testgroup",
            "inode": 12345,
            "device": 67890,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        record = FileRecord.from_dict(data)
        
        assert record.file_path == "/test/file.txt"
        assert record.file_hash == "a" * 64
        assert record.file_size == 1024
        assert record.permissions == 0o644
        assert record.owner == "testuser"
        assert record.group == "testgroup"
        assert isinstance(record.created_at, datetime)
        assert isinstance(record.updated_at, datetime)


class TestFileEvent:
    """Test FileEvent class functionality."""
    
    def test_file_event_creation(self):
        """Test FileEvent creation with all fields."""
        event = FileEvent(
            event_id="test-event-123",
            event_type=EventType.MODIFIED,
            file_path="/test/file.txt",
            timestamp=datetime.utcnow(),
            agent_id="test-agent",
            previous_hash="old" * 32,
            current_hash="new" * 32,
            file_size=1024,
            permissions=0o644,
            owner="testuser",
            group="testgroup"
        )
        
        assert event.event_id == "test-event-123"
        assert event.event_type == EventType.MODIFIED
        assert event.file_path == "/test/file.txt"
        assert event.agent_id == "test-agent"
        assert event.previous_hash == "old" * 32
        assert event.current_hash == "new" * 32
    
    def test_file_event_auto_id_generation(self):
        """Test automatic event ID generation."""
        event = FileEvent(
            event_id="",  # Empty ID should trigger auto-generation
            event_type=EventType.CREATED,
            file_path="/test/file.txt",
            timestamp=datetime.utcnow(),
            agent_id="test-agent"
        )
        
        assert event.event_id != ""
        assert len(event.event_id) > 0
    
    def test_file_event_to_dict(self):
        """Test FileEvent serialization to dictionary."""
        event = FileEvent(
            event_id="test-event-123",
            event_type=EventType.DELETED,
            file_path="/test/file.txt",
            timestamp=datetime.utcnow(),
            agent_id="test-agent",
            metadata={"test_key": "test_value"}
        )
        
        data = event.to_dict()
        
        assert data["event_id"] == "test-event-123"
        assert data["event_type"] == "deleted"
        assert data["file_path"] == "/test/file.txt"
        assert data["agent_id"] == "test-agent"
        assert data["metadata"] == {"test_key": "test_value"}
    
    def test_file_event_from_dict(self):
        """Test FileEvent deserialization from dictionary."""
        data = {
            "event_id": "test-event-123",
            "event_type": "moved",
            "file_path": "/test/file.txt",
            "timestamp": "2023-01-01T00:00:00",
            "agent_id": "test-agent",
            "previous_hash": "old" * 32,
            "current_hash": "new" * 32,
            "file_size": 1024,
            "permissions": 0o644,
            "owner": "testuser",
            "group": "testgroup",
            "metadata": '{"test_key": "test_value"}'
        }
        
        event = FileEvent.from_dict(data)
        
        assert event.event_id == "test-event-123"
        assert event.event_type == EventType.MOVED
        assert event.file_path == "/test/file.txt"
        assert event.agent_id == "test-agent"
        assert event.previous_hash == "old" * 32
        assert event.current_hash == "new" * 32
        assert event.metadata == {"test_key": "test_value"}


class TestEventType:
    """Test EventType enum functionality."""
    
    def test_event_type_values(self):
        """Test EventType enum values."""
        assert EventType.CREATED.value == "created"
        assert EventType.MODIFIED.value == "modified"
        assert EventType.DELETED.value == "deleted"
        assert EventType.MOVED.value == "moved"
        assert EventType.PERMISSION_CHANGED.value == "permission_changed"
        assert EventType.OWNER_CHANGED.value == "owner_changed"
        assert EventType.BASELINE.value == "baseline"
    
    def test_event_type_from_string(self):
        """Test EventType creation from string."""
        assert EventType("created") == EventType.CREATED
        assert EventType("modified") == EventType.MODIFIED
        assert EventType("deleted") == EventType.DELETED
    
    def test_event_type_invalid_string(self):
        """Test EventType creation with invalid string."""
        with pytest.raises(ValueError):
            EventType("invalid_event_type")


class TestFileRecordCrossPlatform:
    """Test FileRecord functionality across different platforms."""
    
    @patch('fim.models.pwd.getpwuid')
    @patch('fim.models.grp.getgrgid')
    def test_file_record_unix_system(self, mock_grp, mock_pwd):
        """Test FileRecord on Unix-like systems."""
        # Mock Unix user/group functions
        mock_pwd.return_value.pw_name = "testuser"
        mock_grp.return_value.gr_name = "testgroup"
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"test content")
            tmp_file.flush()
            
            try:
                record = FileRecord.from_path(tmp_file.name)
                
                assert record.owner == "testuser"
                assert record.group == "testgroup"
                
            finally:
                os.unlink(tmp_file.name)
    
    @patch('fim.models.pwd.getpwuid')
    @patch('fim.models.grp.getgrgid')
    def test_file_record_fallback_uid_gid(self, mock_grp, mock_pwd):
        """Test FileRecord fallback to UID/GID when user/group lookup fails."""
        # Mock Unix user/group functions to fail
        mock_pwd.side_effect = KeyError("User not found")
        mock_grp.side_effect = KeyError("Group not found")
        
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"test content")
            tmp_file.flush()
            
            try:
                record = FileRecord.from_path(tmp_file.name)
                
                # Should fall back to numeric UID/GID
                assert record.owner.isdigit()
                assert record.group.isdigit()
                
            finally:
                os.unlink(tmp_file.name)
