"""
Simplified database management for File Integrity Monitor.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from contextlib import contextmanager

from .models import FileRecord, FileEvent, EventType


class DatabaseManager:
    """Simple SQLite database manager."""
    
    def __init__(self, db_path: str = "fim.db"):
        """Initialize database manager."""
        self.db_path = Path(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create baseline table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS baseline (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    file_hash TEXT NOT NULL,
                    file_size INTEGER NOT NULL,
                    mtime REAL NOT NULL,
                    permissions INTEGER NOT NULL,
                    owner TEXT NOT NULL,
                    group_name TEXT NOT NULL
                )
            """)
            
            # Create events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT NOT NULL
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_baseline_path ON baseline(file_path)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_path ON events(file_path)")
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def store_baseline(self, file_records: List[FileRecord]):
        """Store baseline file records."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            for record in file_records:
                cursor.execute("""
                    INSERT OR REPLACE INTO baseline 
                    (file_path, file_hash, file_size, mtime, permissions, owner, group_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.file_path, record.file_hash, record.file_size, record.mtime,
                    record.permissions, record.owner, record.group
                ))
            
            conn.commit()
    
    def get_baseline(self, file_path: Optional[str] = None) -> List[FileRecord]:
        """Retrieve baseline records."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if file_path:
                cursor.execute("SELECT * FROM baseline WHERE file_path = ?", (file_path,))
            else:
                cursor.execute("SELECT * FROM baseline")
            
            records = []
            for row in cursor.fetchall():
                record = FileRecord(
                    file_path=row[1],
                    file_hash=row[2],
                    file_size=row[3],
                    mtime=row[4],
                    permissions=row[5],
                    owner=row[6],
                    group=row[7],
                )
                records.append(record)
            
            return records
    
    def store_event(self, event: FileEvent):
        """Store a file system event."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO events (event_type, file_path, timestamp, agent_id)
                VALUES (?, ?, ?, ?)
            """, (
                event.event_type.value, event.file_path,
                event.timestamp.isoformat(), event.agent_id
            ))
            
            conn.commit()
    
    def get_events(self, limit: Optional[int] = None) -> List[FileEvent]:
        """Retrieve events."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM events ORDER BY timestamp DESC"
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            
            events = []
            for row in cursor.fetchall():
                event = FileEvent(
                    event_type=EventType(row[1]),
                    file_path=row[2],
                    timestamp=datetime.fromisoformat(row[3]),
                    agent_id=row[4]
                )
                events.append(event)
            
            return events
    
    def export_data(self, format_type: str = "json") -> str:
        """Export database data."""
        baseline = self.get_baseline()
        events = self.get_events()
        
        data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "baseline_count": len(baseline),
            "events_count": len(events),
            "baseline": [
                {
                    "file_path": record.file_path,
                    "file_hash": record.file_hash,
                    "file_size": record.file_size,
                    "mtime": record.mtime,
                    "permissions": record.permissions,
                    "owner": record.owner,
                    "group": record.group,
                }
                for record in baseline
            ],
            "events": [
                {
                    "event_type": event.event_type.value,
                    "file_path": event.file_path,
                    "timestamp": event.timestamp.isoformat(),
                    "agent_id": event.agent_id,
                }
                for event in events
            ],
        }
        
        if format_type.lower() == "csv":
            return self._export_csv(data)
        else:
            return json.dumps(data, indent=2)
    
    def _export_csv(self, data: dict) -> str:
        """Export data as CSV."""
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write baseline
        if data["baseline"]:
            writer.writerow(["BASELINE"])
            writer.writerow(data["baseline"][0].keys())
            for record in data["baseline"]:
                writer.writerow(record.values())
            writer.writerow([])
        
        # Write events
        if data["events"]:
            writer.writerow(["EVENTS"])
            writer.writerow(data["events"][0].keys())
            for event in data["events"]:
                writer.writerow(event.values())
        
        return output.getvalue()
