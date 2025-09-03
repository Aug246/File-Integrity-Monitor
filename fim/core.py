"""
Simplified core file monitoring functionality.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from .models import FileRecord, FileEvent, EventType
from .database import DatabaseManager


class BaselineManager:
    """Manages file baseline creation and verification."""
    
    def __init__(self, database: DatabaseManager):
        """Initialize baseline manager."""
        self.database = database
        self.logger = logging.getLogger(__name__)
    
    def create_baseline(self, path: str, exclude_patterns: Optional[List[str]] = None) -> List[FileRecord]:
        """Create baseline for specified path."""
        path_obj = Path(path)
        if not path_obj.exists():
            raise ValueError(f"Path does not exist: {path}")
        
        self.logger.info(f"Creating baseline for path: {path}")
        
        file_records = []
        total_files = 0
        processed_files = 0
        
        # Count total files first
        for root, dirs, files in os.walk(path):
            total_files += len(files)
        
        # Process files
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check exclusion patterns
                if self._should_exclude(file_path, exclude_patterns):
                    continue
                
                try:
                    record = FileRecord.from_path(file_path)
                    file_records.append(record)
                    processed_files += 1
                    
                    if processed_files % 100 == 0:
                        self.logger.info(f"Processed {processed_files}/{total_files} files...")
                        
                except (OSError, ValueError) as e:
                    self.logger.warning(f"Skipping file {file_path}: {e}")
        
        # Store baseline in database
        self.database.store_baseline(file_records)
        
        self.logger.info(f"Baseline created successfully: {len(file_records)} files processed")
        return file_records
    
    def _should_exclude(self, file_path: str, exclude_patterns: Optional[List[str]]) -> bool:
        """Check if file should be excluded based on patterns."""
        if not exclude_patterns:
            return False
        
        import fnmatch
        
        for pattern in exclude_patterns:
            if fnmatch.fnmatch(file_path, pattern):
                return True
            if fnmatch.fnmatch(os.path.basename(file_path), pattern):
                return True
        
        return False
    
    def verify_baseline(self, path: str, exclude_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Verify current state against baseline."""
        self.logger.info(f"Verifying baseline for path: {path}")
        
        # Get current state
        current_records = {}
        path_obj = Path(path)
        
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                
                if self._should_exclude(file_path, exclude_patterns):
                    continue
                
                try:
                    record = FileRecord.from_path(file_path)
                    current_records[file_path] = record
                except (OSError, ValueError) as e:
                    self.logger.warning(f"Could not read file {file_path}: {e}")
        
        # Get baseline
        baseline_records = {r.file_path: r for r in self.database.get_baseline()}
        
        # Compare and find differences
        results = {
            "total_files": len(current_records),
            "baseline_files": len(baseline_records),
            "created": [],
            "deleted": [],
            "modified": [],
            "unchanged": [],
        }
        
        for file_path, current_record in current_records.items():
            if file_path not in baseline_records:
                results["created"].append(file_path)
            else:
                baseline_record = baseline_records[file_path]
                
                if current_record.file_hash != baseline_record.file_hash:
                    results["modified"].append(file_path)
                else:
                    results["unchanged"].append(file_path)
        
        for file_path in baseline_records:
            if file_path not in current_records:
                results["deleted"].append(file_path)
        
        self.logger.info(f"Verification complete: {len(results['modified'])} modified, "
                        f"{len(results['created'])} created, {len(results['deleted'])} deleted")
        
        return results
