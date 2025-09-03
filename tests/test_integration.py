"""
Integration tests for simplified File Integrity Monitor.
"""

import os
import tempfile
import shutil
import pytest
from pathlib import Path

from fim.core import BaselineManager
from fim.database import DatabaseManager
from fim.models import FileEvent, EventType


class TestFIMIntegration:
    """Integration tests for the simplified FIM workflow."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        # Create temporary test directory
        self.test_dir = tempfile.mkdtemp(prefix="fim_test_")
        self.test_files_dir = os.path.join(self.test_dir, "test_files")
        os.makedirs(self.test_files_dir)
        
        # Create temporary database
        self.db_path = os.path.join(self.test_dir, "test_fim.db")
        
        # Initialize components
        self.database = DatabaseManager(self.db_path)
        self.baseline_manager = BaselineManager(self.database)
        
        # Create some test files
        self._create_test_files()
    
    def teardown_method(self):
        """Clean up test environment after each test."""
        # Remove test directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def _create_test_files(self):
        """Create test files for monitoring."""
        test_files = [
            ("file1.txt", "This is test file 1"),
            ("file2.txt", "This is test file 2"),
            ("config.ini", "setting1=value1\nsetting2=value2"),
            ("script.sh", "#!/bin/bash\necho 'Hello World'"),
        ]
        
        for filename, content in test_files:
            file_path = os.path.join(self.test_files_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
    
    def test_baseline_creation_and_verification(self):
        """Test complete baseline creation and verification workflow."""
        # Create baseline
        baseline_records = self.baseline_manager.create_baseline(self.test_files_dir)
        
        assert len(baseline_records) == 4  # 4 test files
        assert any("file1.txt" in record.file_path for record in baseline_records)
        assert any("config.ini" in record.file_path for record in baseline_records)
        
        # Verify baseline
        verification_results = self.baseline_manager.verify_baseline(self.test_files_dir)
        
        assert verification_results["total_files"] == 4
        assert verification_results["baseline_files"] == 4
        assert len(verification_results["unchanged"]) == 4
        assert len(verification_results["created"]) == 0
        assert len(verification_results["modified"]) == 0
        assert len(verification_results["deleted"]) == 0
    
    def test_file_modification_detection(self):
        """Test detection of file modifications."""
        # Create baseline
        self.baseline_manager.create_baseline(self.test_files_dir)
        
        # Modify a file
        file1_path = os.path.join(self.test_files_dir, "file1.txt")
        with open(file1_path, 'w') as f:
            f.write("Modified content for file 1")
        
        # Verify changes
        verification_results = self.baseline_manager.verify_baseline(self.test_files_dir)
        
        assert len(verification_results["modified"]) == 1
        assert file1_path in verification_results["modified"]
        assert len(verification_results["unchanged"]) == 3
    
    def test_file_creation_detection(self):
        """Test detection of new file creation."""
        # Create baseline
        self.baseline_manager.create_baseline(self.test_files_dir)
        
        # Create a new file
        new_file_path = os.path.join(self.test_files_dir, "newfile.txt")
        with open(new_file_path, 'w') as f:
            f.write("This is a new file")
        
        # Verify changes
        verification_results = self.baseline_manager.verify_baseline(self.test_files_dir)
        
        assert len(verification_results["created"]) == 1
        assert new_file_path in verification_results["created"]
        assert len(verification_results["unchanged"]) == 4
    
    def test_file_deletion_detection(self):
        """Test detection of file deletion."""
        # Create baseline
        self.baseline_manager.create_baseline(self.test_files_dir)
        
        # Delete a file
        file_to_delete = os.path.join(self.test_files_dir, "file2.txt")
        os.unlink(file_to_delete)
        
        # Verify changes
        verification_results = self.baseline_manager.verify_baseline(self.test_files_dir)
        
        assert len(verification_results["deleted"]) == 1
        assert file_to_delete in verification_results["deleted"]
        assert len(verification_results["unchanged"]) == 3
    
    def test_exclude_patterns(self):
        """Test file exclusion patterns."""
        # Create some temporary files
        temp_files = [
            ("temp1.tmp", "temporary content 1"),
            ("temp2.tmp", "temporary content 2"),
            ("cache.log", "log content"),
        ]
        
        for filename, content in temp_files:
            file_path = os.path.join(self.test_files_dir, filename)
            with open(file_path, 'w') as f:
                f.write(content)
        
        # Create baseline with exclusions
        exclude_patterns = ["*.tmp", "*.log"]
        baseline_records = self.baseline_manager.create_baseline(
            self.test_files_dir, exclude_patterns
        )
        
        # Should exclude temp and log files
        assert len(baseline_records) == 4  # Only the original 4 files
        assert not any("temp" in record.file_path for record in baseline_records)
        assert not any("cache.log" in record.file_path for record in baseline_records)
    
    def test_database_persistence(self):
        """Test that baseline data persists in database."""
        # Create baseline
        baseline_records = self.baseline_manager.create_baseline(self.test_files_dir)
        
        # Create new database manager instance (simulating restart)
        new_database = DatabaseManager(self.db_path)
        new_baseline_manager = BaselineManager(new_database)
        
        # Verify baseline still exists
        stored_records = new_database.get_baseline()
        assert len(stored_records) == 4
        
        # Verify against stored baseline
        verification_results = new_baseline_manager.verify_baseline(self.test_files_dir)
        assert len(verification_results["unchanged"]) == 4
    
    def test_large_file_handling(self):
        """Test handling of large files."""
        # Create a larger file
        large_file_path = os.path.join(self.test_files_dir, "large.txt")
        large_content = "x" * 1000000  # 1MB file
        
        with open(large_file_path, 'w') as f:
            f.write(large_content)
        
        # Create baseline
        baseline_records = self.baseline_manager.create_baseline(self.test_files_dir)
        
        # Should handle large file
        large_file_record = next(
            (r for r in baseline_records if "large.txt" in r.file_path), None
        )
        assert large_file_record is not None
        assert large_file_record.file_size == 1000000
        
        # Verify hash calculation
        assert len(large_file_record.file_hash) == 64  # SHA-256 hash length
    
    def test_special_characters_in_paths(self):
        """Test handling of special characters in file paths."""
        # Create file with special characters
        special_file_path = os.path.join(self.test_files_dir, "file with spaces.txt")
        special_content = "content with special chars: !@#$%^&*()"
        
        with open(special_file_path, 'w') as f:
            f.write(special_content)
        
        # Create baseline
        baseline_records = self.baseline_manager.create_baseline(self.test_files_dir)
        
        # Should handle special characters
        special_file_record = next(
            (r for r in baseline_records if "file with spaces.txt" in r.file_path), None
        )
        assert special_file_record is not None
        assert special_file_record.file_size == len(special_content)
    
    def test_empty_directory(self):
        """Test handling of empty directories."""
        # Create empty directory
        empty_dir = os.path.join(self.test_dir, "empty_dir")
        os.makedirs(empty_dir)
        
        # Create baseline for empty directory
        baseline_records = self.baseline_manager.create_baseline(empty_dir)
        
        # Should handle empty directory gracefully
        assert len(baseline_records) == 0
        
        # Verify empty directory
        verification_results = self.baseline_manager.verify_baseline(empty_dir)
        assert verification_results["total_files"] == 0
        assert verification_results["baseline_files"] == 0
