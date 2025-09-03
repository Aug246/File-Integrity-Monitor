"""
Core file monitoring functionality for File Integrity Monitor.
"""

import os
import time
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from .models import FileRecord, FileEvent, EventType
from .database import DatabaseManager


class FileChangeHandler(FileSystemEventHandler):
    """Handles file system events detected by watchdog."""
    
    def __init__(self, callback: Callable[[FileEvent], None]):
        """Initialize handler with callback function."""
        self.callback = callback
        self.logger = logging.getLogger(__name__)
    
    def on_created(self, event: FileSystemEvent):
        """Handle file creation events."""
        if not event.is_directory:
            self._process_event(event, EventType.CREATED)
    
    def on_modified(self, event: FileSystemEvent):
        """Handle file modification events."""
        if not event.is_directory:
            self._process_event(event, EventType.MODIFIED)
    
    def on_deleted(self, event: FileSystemEvent):
        """Handle file deletion events."""
        if not event.is_directory:
            self._process_event(event, EventType.DELETED)
    
    def on_moved(self, event: FileSystemEvent):
        """Handle file move/rename events."""
        if not event.is_directory:
            self._process_event(event, EventType.MOVED)
    
    def _process_event(self, event: FileSystemEvent, event_type: EventType):
        """Process file system event and create FileEvent."""
        try:
            file_event = FileEvent(
                event_id="",
                event_type=event_type,
                file_path=event.src_path,
                timestamp=datetime.utcnow(),
                agent_id=os.getenv("FIM_AGENT_ID", "default"),
            )
            
            # Add additional metadata based on event type
            if event_type in [EventType.MODIFIED, EventType.CREATED]:
                try:
                    record = FileRecord.from_path(event.src_path)
                    file_event.current_hash = record.file_hash
                    file_event.file_size = record.file_size
                    file_event.permissions = record.permissions
                    file_event.owner = record.owner
                    file_event.group = record.group
                except (OSError, ValueError) as e:
                    self.logger.warning(f"Could not read file {event.src_path}: {e}")
            
            self.callback(file_event)
            
        except Exception as e:
            self.logger.error(f"Error processing event {event_type.value} for {event.src_path}: {e}")


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
            "permission_changed": [],
            "unchanged": [],
        }
        
        for file_path, current_record in current_records.items():
            if file_path not in baseline_records:
                results["created"].append(file_path)
            else:
                baseline_record = baseline_records[file_path]
                
                if current_record.file_hash != baseline_record.file_hash:
                    results["modified"].append(file_path)
                elif current_record.permissions != baseline_record.permissions:
                    results["permission_changed"].append(file_path)
                else:
                    results["unchanged"].append(file_path)
        
        for file_path in baseline_records:
            if file_path not in current_records:
                results["deleted"].append(file_path)
        
        self.logger.info(f"Verification complete: {len(results['modified'])} modified, "
                        f"{len(results['created'])} created, {len(results['deleted'])} deleted")
        
        return results


class FileMonitor:
    """Main file monitoring class with continuous monitoring capabilities."""
    
    def __init__(self, database: DatabaseManager, config: Optional[Dict[str, Any]] = None):
        """Initialize file monitor."""
        self.database = database
        self.config = config or {}
        self.observer = None
        self.handler = None
        self.is_monitoring = False
        self.logger = logging.getLogger(__name__)
        
        # Default configuration
        self.monitor_paths = self.config.get("monitor_paths", [])
        self.exclude_patterns = self.config.get("exclude_patterns", [
            "*.tmp", "*.log", "*.cache", ".DS_Store", "Thumbs.db"
        ])
        self.polling_interval = self.config.get("polling_interval", 60)  # seconds
        self.agent_id = self.config.get("agent_id", os.getenv("FIM_AGENT_ID", "default"))
    
    def start_monitoring(self, paths: Optional[List[str]] = None) -> None:
        """Start continuous file monitoring."""
        if self.is_monitoring:
            self.logger.warning("Monitoring is already active")
            return
        
        monitor_paths = paths or self.monitor_paths
        if not monitor_paths:
            raise ValueError("No paths specified for monitoring")
        
        self.logger.info(f"Starting file monitoring for paths: {monitor_paths}")
        
        # Create event handler
        self.handler = FileChangeHandler(self._handle_file_event)
        
        # Create observer
        self.observer = Observer()
        
        # Schedule monitoring for each path
        for path in monitor_paths:
            if os.path.exists(path):
                self.observer.schedule(self.handler, path, recursive=True)
                self.logger.info(f"Monitoring path: {path}")
            else:
                self.logger.warning(f"Path does not exist, skipping: {path}")
        
        # Start monitoring
        self.observer.start()
        self.is_monitoring = True
        
        self.logger.info("File monitoring started successfully")
    
    def stop_monitoring(self) -> None:
        """Stop continuous file monitoring."""
        if not self.is_monitoring:
            self.logger.warning("Monitoring is not active")
            return
        
        self.logger.info("Stopping file monitoring...")
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
        
        self.is_monitoring = False
        self.logger.info("File monitoring stopped")
    
    def _handle_file_event(self, file_event: FileEvent) -> None:
        """Handle file events and store in database."""
        try:
            # Get previous hash from baseline if available
            baseline_records = self.database.get_baseline(file_event.file_path)
            if baseline_records:
                file_event.previous_hash = baseline_records[0].file_hash
            
            # Store event in database
            self.database.store_event(file_event)
            
            # Log event
            self.logger.info(f"File event detected: {file_event.event_type.value} - {file_event.file_path}")
            
            # Check if this is a critical change
            if self._is_critical_change(file_event):
                self.logger.warning(f"Critical file change detected: {file_event.file_path}")
                self._send_alert(file_event)
                
        except Exception as e:
            self.logger.error(f"Error handling file event: {e}")
    
    def _is_critical_change(self, file_event: FileEvent) -> bool:
        """Determine if a file change is critical."""
        critical_extensions = {".exe", ".dll", ".so", ".dylib", ".conf", ".config", ".ini"}
        critical_paths = {"etc", "bin", "sbin", "usr/bin", "usr/sbin", "Windows/System32"}
        
        file_ext = Path(file_event.file_path).suffix.lower()
        file_path_lower = file_event.file_path.lower()
        
        return (file_ext in critical_extensions or 
                any(critical in file_path_lower for critical in critical_paths))
    
    def _send_alert(self, file_event: FileEvent) -> None:
        """Send alert for critical file changes."""
        # This could be extended to send emails, webhooks, etc.
        alert_msg = f"CRITICAL: {file_event.event_type.value} detected on {file_event.file_path}"
        self.logger.warning(alert_msg)
        
        # Store alert in metadata
        file_event.metadata["alert_sent"] = True
        file_event.metadata["alert_timestamp"] = datetime.utcnow().isoformat()
    
    def run_polling_monitor(self, paths: Optional[List[str]] = None) -> None:
        """Run monitoring in polling mode (fallback for systems without watchdog support)."""
        monitor_paths = paths or self.monitor_paths
        if not monitor_paths:
            raise ValueError("No paths specified for monitoring")
        
        self.logger.info(f"Starting polling monitor for paths: {monitor_paths}")
        
        try:
            while True:
                for path in monitor_paths:
                    if os.path.exists(path):
                        self._poll_directory(path)
                
                time.sleep(self.polling_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Polling monitor stopped by user")
    
    def _poll_directory(self, path: str) -> None:
        """Poll directory for changes."""
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    if self._should_exclude(file_path):
                        continue
                    
                    # Check if file has changed since last check
                    if self._file_has_changed(file_path):
                        self._handle_file_change(file_path)
                        
        except Exception as e:
            self.logger.error(f"Error polling directory {path}: {e}")
    
    def _should_exclude(self, file_path: str) -> bool:
        """Check if file should be excluded."""
        return self._should_exclude(file_path, self.exclude_patterns)
    
    def _file_has_changed(self, file_path: str) -> bool:
        """Check if file has changed since last check."""
        # This is a simplified check - in practice, you'd want to track last check time
        # and compare with file modification time
        return True
    
    def _handle_file_change(self, file_path: str) -> None:
        """Handle file change detected during polling."""
        try:
            # Determine event type based on current state vs baseline
            baseline_records = self.database.get_baseline(file_path)
            
            if not baseline_records:
                event_type = EventType.CREATED
            else:
                current_record = FileRecord.from_path(file_path)
                if current_record.file_hash != baseline_records[0].file_hash:
                    event_type = EventType.MODIFIED
                else:
                    return  # No change detected
            
            file_event = FileEvent(
                event_id="",
                event_type=event_type,
                file_path=file_path,
                timestamp=datetime.utcnow(),
                agent_id=self.agent_id,
            )
            
            self._handle_file_event(file_event)
            
        except Exception as e:
            self.logger.error(f"Error handling file change for {file_path}: {e}")
