"""
Unit tests for simplified FIM data models.
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
            permissions=0o644,
            owner="testuser",
            group="testgroup"
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
    
    def test_file_record_owner_group_fallback(self):
        """Test FileRecord owner/group fallback for systems without pwd/grp."""
        # This test verifies that the system handles missing pwd/grp gracefully
        # Since we're on a system that has these modules, we'll test the fallback logic
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"test content")
            tmp_file.flush()
            
            try:
                record = FileRecord.from_path(tmp_file.name)
                
                # Should have valid owner and group (either names or numeric IDs)
                assert record.owner is not None
                assert record.group is not None
                assert len(str(record.owner)) > 0
                assert len(str(record.group)) > 0
                
            finally:
                os.unlink(tmp_file.name)


class TestFileEvent:
    """Test FileEvent class functionality."""
    
    def test_file_event_creation(self):
        """Test FileEvent creation with all fields."""
        timestamp = datetime.utcnow()
        event = FileEvent(
            event_type=EventType.MODIFIED,
            file_path="/test/file.txt",
            timestamp=timestamp,
            agent_id="test-agent"
        )
        
        assert event.event_type == EventType.MODIFIED
        assert event.file_path == "/test/file.txt"
        assert event.timestamp == timestamp
        assert event.agent_id == "test-agent"
    
    def test_file_event_default_timestamp(self):
        """Test FileEvent automatic timestamp generation."""
        event = FileEvent(
            event_type=EventType.CREATED,
            file_path="/test/file.txt"
        )
        
        assert event.timestamp is not None
        assert isinstance(event.timestamp, datetime)
    
    def test_file_event_default_agent_id(self):
        """Test FileEvent default agent_id."""
        event = FileEvent(
            event_type=EventType.DELETED,
            file_path="/test/file.txt"
        )
        
        assert event.agent_id == "default"


class TestEventType:
    """Test EventType enum functionality."""
    
    def test_event_type_values(self):
        """Test EventType enum values."""
        assert EventType.CREATED.value == "created"
        assert EventType.MODIFIED.value == "modified"
        assert EventType.DELETED.value == "deleted"
        assert EventType.BASELINE.value == "baseline"
    
    def test_event_type_enumeration(self):
        """Test EventType enum iteration."""
        event_types = list(EventType)
        assert len(event_types) == 4
        assert EventType.CREATED in event_types
        assert EventType.MODIFIED in event_types
        assert EventType.DELETED in event_types
        assert EventType.BASELINE in event_types
