"""
Database management for File Integrity Monitor.
"""

import sqlite3
import json
import hmac
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from contextlib import contextmanager

from .models import FileRecord, FileEvent, EventType


class DatabaseManager:
    """Manages SQLite database operations with tamper-evident features."""
    
    def __init__(self, db_path: str = "fim.db"):
        """Initialize database manager."""
        self.db_path = Path(db_path)
        self.secret_key = self._generate_secret_key()
        self._init_database()
    
    def _generate_secret_key(self) -> bytes:
        """Generate a secret key for HMAC verification."""
        import secrets
        return secrets.token_bytes(32)
    
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
                    ctime REAL NOT NULL,
                    permissions INTEGER NOT NULL,
                    owner TEXT NOT NULL,
                    group_name TEXT NOT NULL,
                    inode INTEGER NOT NULL,
                    device INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    signature TEXT NOT NULL
                )
            """)
            
            # Create events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    event_type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    previous_hash TEXT,
                    current_hash TEXT,
                    file_size INTEGER,
                    permissions INTEGER,
                    owner TEXT,
                    group_name TEXT,
                    metadata TEXT,
                    signature TEXT NOT NULL
                )
            """)
            
            # Create audit log table for tamper evidence
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    user TEXT NOT NULL,
                    details TEXT,
                    signature TEXT NOT NULL
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_baseline_path ON baseline(file_path)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_path ON events(file_path)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type)")
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _sign_data(self, data: str) -> str:
        """Sign data with HMAC for tamper evidence."""
        return hmac.new(self.secret_key, data.encode(), hashlib.sha256).hexdigest()
    
    def _verify_signature(self, data: str, signature: str) -> bool:
        """Verify HMAC signature."""
        expected = self._sign_data(data)
        return hmac.compare_digest(expected, signature)
    
    def _log_audit(self, operation: str, table_name: str, record_id: str, 
                   user: str, details: Optional[Dict] = None):
        """Log audit trail for tamper evidence."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            details_json = json.dumps(details) if details else None
            timestamp = datetime.utcnow().isoformat()
            
            # Create signature for audit log entry
            audit_data = f"{operation}:{table_name}:{record_id}:{timestamp}:{user}:{details_json or ''}"
            signature = self._sign_data(audit_data)
            
            cursor.execute("""
                INSERT INTO audit_log (operation, table_name, record_id, timestamp, user, details, signature)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (operation, table_name, record_id, user, timestamp, details_json, signature))
            
            conn.commit()
    
    def store_baseline(self, file_records: List[FileRecord], user: str = "system"):
        """Store baseline file records."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            for record in file_records:
                # Create signature for baseline record
                record_data = f"{record.file_path}:{record.file_hash}:{record.file_size}:{record.mtime}"
                signature = self._sign_data(record_data)
                
                cursor.execute("""
                    INSERT OR REPLACE INTO baseline 
                    (file_path, file_hash, file_size, mtime, ctime, permissions, 
                     owner, group_name, inode, device, created_at, updated_at, signature)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    record.file_path, record.file_hash, record.file_size, record.mtime,
                    record.ctime, record.permissions, record.owner, record.group,
                    record.inode, record.device, record.created_at.isoformat(),
                    record.updated_at.isoformat(), signature
                ))
                
                # Log audit trail
                self._log_audit(
                    "INSERT_BASELINE", "baseline", record.file_path, user,
                    {"hash": record.file_hash, "size": record.file_size}
                )
            
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
                # Verify signature before returning
                record_data = f"{row['file_path']}:{row['file_hash']}:{row['file_size']}:{row['mtime']}"
                if not self._verify_signature(record_data, row['signature']):
                    raise ValueError(f"Tampering detected in baseline record for {row['file_path']}")
                
                record = FileRecord(
                    file_path=row['file_path'],
                    file_hash=row['file_hash'],
                    file_size=row['file_size'],
                    mtime=row['mtime'],
                    ctime=row['ctime'],
                    permissions=row['permissions'],
                    owner=row['owner'],
                    group=row['group_name'],
                    inode=row['inode'],
                    device=row['device'],
                    created_at=datetime.fromisoformat(row['created_at']),
                    updated_at=datetime.fromisoformat(row['updated_at']),
                )
                records.append(record)
            
            return records
    
    def store_event(self, event: FileEvent, user: str = "system"):
        """Store a file system event."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create signature for event
            event_data = f"{event.event_id}:{event.event_type.value}:{event.file_path}:{event.timestamp.isoformat()}"
            signature = self._sign_data(event_data)
            
            cursor.execute("""
                INSERT INTO events 
                (event_id, event_type, file_path, timestamp, agent_id, previous_hash,
                 current_hash, file_size, permissions, owner, group_name, metadata, signature)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event.event_id, event.event_type.value, event.file_path,
                event.timestamp.isoformat(), event.agent_id, event.previous_hash,
                event.current_hash, event.file_size, event.permissions,
                event.owner, event.group, json.dumps(event.metadata), signature
            ))
            
            # Log audit trail
            self._log_audit(
                "INSERT_EVENT", "events", event.event_id, user,
                {"type": event.event_type.value, "file_path": event.file_path}
            )
            
            conn.commit()
    
    def get_events(self, file_path: Optional[str] = None, 
                   event_type: Optional[EventType] = None,
                   limit: Optional[int] = None) -> List[FileEvent]:
        """Retrieve events with optional filtering."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM events WHERE 1=1"
            params = []
            
            if file_path:
                query += " AND file_path = ?"
                params.append(file_path)
            
            if event_type:
                query += " AND event_type = ?"
                params.append(event_type.value)
            
            query += " ORDER BY timestamp DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(query, params)
            
            events = []
            for row in cursor.fetchall():
                # Verify signature before returning
                event_data = f"{row['event_id']}:{row['event_type']}:{row['file_path']}:{row['timestamp']}"
                if not self._verify_signature(event_data, row['signature']):
                    raise ValueError(f"Tampering detected in event record {row['event_id']}")
                
                event = FileEvent(
                    event_id=row['event_id'],
                    event_type=EventType(row['event_type']),
                    file_path=row['file_path'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    agent_id=row['agent_id'],
                    previous_hash=row['previous_hash'],
                    current_hash=row['current_hash'],
                    file_size=row['file_size'],
                    permissions=row['permissions'],
                    owner=row['owner'],
                    group=row['group_name'],
                    metadata=json.loads(row['metadata']) if row['metadata'] else {},
                )
                events.append(event)
            
            return events
    
    def export_data(self, format_type: str = "json") -> str:
        """Export database data in specified format."""
        baseline = self.get_baseline()
        events = self.get_events()
        
        data = {
            "export_timestamp": datetime.utcnow().isoformat(),
            "baseline_count": len(baseline),
            "events_count": len(events),
            "baseline": [record.to_dict() for record in baseline],
            "events": [event.to_dict() for event in events],
        }
        
        if format_type.lower() == "csv":
            return self._export_csv(data)
        else:
            return json.dumps(data, indent=2)
    
    def _export_csv(self, data: Dict[str, Any]) -> str:
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
    
    def verify_integrity(self) -> Dict[str, Any]:
        """Verify database integrity and detect tampering."""
        results = {
            "baseline_integrity": True,
            "events_integrity": True,
            "audit_log_integrity": True,
            "errors": []
        }
        
        try:
            # Verify baseline records
            self.get_baseline()
        except Exception as e:
            results["baseline_integrity"] = False
            results["errors"].append(f"Baseline integrity check failed: {e}")
        
        try:
            # Verify events
            self.get_events(limit=100)  # Check recent events
        except Exception as e:
            results["events_integrity"] = False
            results["errors"].append(f"Events integrity check failed: {e}")
        
        return results
