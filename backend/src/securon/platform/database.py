"""Database management and schema for Securon platform"""

import sqlite3
import json
import os
import shutil
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from contextlib import asynccontextmanager
import logging
from threading import Lock

from ..interfaces.core_types import Severity, RuleSource, RuleStatus, LogSource, AnomalyType
from ..interfaces.iac_scanner import SecurityRule, ScanResult
from ..rule_engine.models import RuleVersion, RuleConflict, RuleMetrics


logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Exception raised for database operations"""
    pass


class DatabaseSchema:
    """Database schema definitions"""
    
    # Security Rules table
    RULES_TABLE = """
    CREATE TABLE IF NOT EXISTS security_rules (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        severity TEXT NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
        pattern TEXT NOT NULL,
        remediation TEXT NOT NULL,
        source TEXT NOT NULL CHECK (source IN ('STATIC', 'ML_GENERATED')),
        status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'CANDIDATE', 'REJECTED')),
        created_at TIMESTAMP NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        checksum TEXT NOT NULL,
        UNIQUE(id)
    );
    """
    
    # Rule versions for audit trail
    RULE_VERSIONS_TABLE = """
    CREATE TABLE IF NOT EXISTS rule_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_id TEXT NOT NULL,
        version INTEGER NOT NULL,
        rule_data TEXT NOT NULL,  -- JSON serialized rule
        modified_at TIMESTAMP NOT NULL,
        modified_by TEXT,
        change_reason TEXT,
        checksum TEXT NOT NULL,
        FOREIGN KEY (rule_id) REFERENCES security_rules (id) ON DELETE CASCADE,
        UNIQUE(rule_id, version)
    );
    """
    
    # Rule metrics for performance tracking
    RULE_METRICS_TABLE = """
    CREATE TABLE IF NOT EXISTS rule_metrics (
        rule_id TEXT PRIMARY KEY,
        times_triggered INTEGER DEFAULT 0,
        false_positives INTEGER DEFAULT 0,
        true_positives INTEGER DEFAULT 0,
        last_triggered TIMESTAMP,
        effectiveness_score REAL DEFAULT 0.0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (rule_id) REFERENCES security_rules (id) ON DELETE CASCADE
    );
    """
    
    # Rule conflicts tracking
    RULE_CONFLICTS_TABLE = """
    CREATE TABLE IF NOT EXISTS rule_conflicts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_id TEXT NOT NULL,
        conflicting_rule_id TEXT NOT NULL,
        conflict_type TEXT NOT NULL,
        description TEXT NOT NULL,
        severity TEXT NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        resolved_at TIMESTAMP,
        FOREIGN KEY (rule_id) REFERENCES security_rules (id) ON DELETE CASCADE,
        FOREIGN KEY (conflicting_rule_id) REFERENCES security_rules (id) ON DELETE CASCADE,
        UNIQUE(rule_id, conflicting_rule_id, conflict_type)
    );
    """
    
    # Cloud logs storage
    CLOUD_LOGS_TABLE = """
    CREATE TABLE IF NOT EXISTS cloud_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP NOT NULL,
        source TEXT NOT NULL CHECK (source IN ('VPC_FLOW', 'CLOUDTRAIL', 'IAM')),
        raw_data TEXT NOT NULL,  -- JSON serialized raw data
        normalized_data TEXT NOT NULL,  -- JSON serialized normalized data
        processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        checksum TEXT NOT NULL,
        batch_id TEXT
    );
    """
    
    # ML findings/anomalies storage
    ML_FINDINGS_TABLE = """
    CREATE TABLE IF NOT EXISTS ml_findings (
        id TEXT PRIMARY KEY,
        anomaly_type TEXT NOT NULL CHECK (anomaly_type IN ('PORT_SCAN', 'BRUTE_FORCE', 'SUSPICIOUS_IP', 'UNUSUAL_API')),
        severity REAL NOT NULL,
        confidence REAL NOT NULL,
        affected_resources TEXT NOT NULL,  -- JSON array
        time_window_start TIMESTAMP NOT NULL,
        time_window_end TIMESTAMP NOT NULL,
        patterns TEXT NOT NULL,  -- JSON serialized patterns
        explanation TEXT NOT NULL,  -- JSON serialized explanation
        candidate_rule_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        processed BOOLEAN DEFAULT FALSE,
        checksum TEXT NOT NULL
    );
    """
    
    # IaC scan results storage
    SCAN_RESULTS_TABLE = """
    CREATE TABLE IF NOT EXISTS scan_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id TEXT NOT NULL,
        file_path TEXT NOT NULL,
        rule_id TEXT NOT NULL,
        severity TEXT NOT NULL CHECK (severity IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
        description TEXT NOT NULL,
        line_number INTEGER,
        remediation TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        checksum TEXT NOT NULL,
        FOREIGN KEY (rule_id) REFERENCES security_rules (id)
    );
    """
    
    # System metadata and configuration
    SYSTEM_METADATA_TABLE = """
    CREATE TABLE IF NOT EXISTS system_metadata (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        description TEXT
    );
    """
    
    # Index creation statements
    INDEXES = [
        "CREATE INDEX IF NOT EXISTS idx_cloud_logs_timestamp ON cloud_logs(timestamp)",
        "CREATE INDEX IF NOT EXISTS idx_cloud_logs_source ON cloud_logs(source)",
        "CREATE INDEX IF NOT EXISTS idx_cloud_logs_batch_id ON cloud_logs(batch_id)",
        "CREATE INDEX IF NOT EXISTS idx_ml_findings_type ON ml_findings(anomaly_type)",
        "CREATE INDEX IF NOT EXISTS idx_ml_findings_created ON ml_findings(created_at)",
        "CREATE INDEX IF NOT EXISTS idx_ml_findings_processed ON ml_findings(processed)",
        "CREATE INDEX IF NOT EXISTS idx_scan_results_scan_id ON scan_results(scan_id)",
        "CREATE INDEX IF NOT EXISTS idx_scan_results_file_path ON scan_results(file_path)",
        "CREATE INDEX IF NOT EXISTS idx_scan_results_rule_id ON scan_results(rule_id)",
        "CREATE INDEX IF NOT EXISTS idx_scan_results_created ON scan_results(created_at)"
    ]
    
    @classmethod
    def get_all_tables(cls) -> List[str]:
        """Get all table creation statements"""
        return [
            cls.RULES_TABLE,
            cls.RULE_VERSIONS_TABLE,
            cls.RULE_METRICS_TABLE,
            cls.RULE_CONFLICTS_TABLE,
            cls.CLOUD_LOGS_TABLE,
            cls.ML_FINDINGS_TABLE,
            cls.SCAN_RESULTS_TABLE,
            cls.SYSTEM_METADATA_TABLE
        ]
    
    @classmethod
    def get_all_indexes(cls) -> List[str]:
        """Get all index creation statements"""
        return cls.INDEXES


class DatabaseManager:
    """Enhanced database manager with comprehensive data persistence"""
    
    def __init__(self, db_path: str = "data/securon.db", backup_enabled: bool = True):
        self.db_path = Path(db_path)
        self.backup_enabled = backup_enabled
        self.backup_dir = self.db_path.parent / "backups"
        self._lock = Lock()
        
        # Ensure directories exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        if self.backup_enabled:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize database
        self._initialize_database()
        
        logger.info(f"Database initialized at {self.db_path}")
    
    def _initialize_database(self):
        """Initialize database schema"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("PRAGMA foreign_keys = ON")
                conn.execute("PRAGMA journal_mode = WAL")
                conn.execute("PRAGMA synchronous = NORMAL")
                
                # Create all tables
                for table_sql in DatabaseSchema.get_all_tables():
                    conn.execute(table_sql)
                
                # Create all indexes
                for index_sql in DatabaseSchema.get_all_indexes():
                    conn.execute(index_sql)
                
                # Insert initial metadata
                conn.execute("""
                    INSERT OR IGNORE INTO system_metadata (key, value, description)
                    VALUES (?, ?, ?)
                """, ("schema_version", "1.0", "Database schema version"))
                
                conn.execute("""
                    INSERT OR IGNORE INTO system_metadata (key, value, description)
                    VALUES (?, ?, ?)
                """, ("created_at", datetime.now().isoformat(), "Database creation timestamp"))
                
                conn.commit()
                
        except Exception as e:
            raise DatabaseError(f"Failed to initialize database: {str(e)}")
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection with proper error handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA foreign_keys = ON")
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            raise DatabaseError(f"Database connection error: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def _calculate_checksum(self, data: Any) -> str:
        """Calculate checksum for data integrity"""
        import hashlib
        if isinstance(data, dict):
            data_str = json.dumps(data, sort_keys=True, default=str)
        else:
            data_str = str(data)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]
    
    def _validate_data_integrity(self, stored_checksum: str, data: Any) -> bool:
        """Validate data integrity using checksum"""
        calculated_checksum = self._calculate_checksum(data)
        return stored_checksum == calculated_checksum
    
    async def store_security_rule(self, rule: SecurityRule) -> None:
        """Store security rule with integrity checks"""
        with self._lock:
            checksum = self._calculate_checksum(rule.model_dump())
            
            async with self.get_connection() as conn:
                try:
                    # Check if rule exists
                    existing = conn.execute(
                        "SELECT id, checksum FROM security_rules WHERE id = ?",
                        (rule.id,)
                    ).fetchone()
                    
                    if existing:
                        # Update existing rule and create version
                        await self._create_rule_version(conn, rule.id, rule)
                        
                        conn.execute("""
                            UPDATE security_rules 
                            SET name=?, description=?, severity=?, pattern=?, remediation=?, 
                                source=?, status=?, updated_at=?, checksum=?
                            WHERE id=?
                        """, (
                            rule.name, rule.description, rule.severity.value, rule.pattern,
                            rule.remediation, rule.source.value, rule.status.value,
                            datetime.now(), checksum, rule.id
                        ))
                    else:
                        # Insert new rule
                        conn.execute("""
                            INSERT INTO security_rules 
                            (id, name, description, severity, pattern, remediation, source, status, created_at, checksum)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            rule.id, rule.name, rule.description, rule.severity.value,
                            rule.pattern, rule.remediation, rule.source.value, rule.status.value,
                            rule.created_at, checksum
                        ))
                        
                        # Initialize metrics
                        conn.execute("""
                            INSERT INTO rule_metrics (rule_id) VALUES (?)
                        """, (rule.id,))
                    
                    conn.commit()
                    logger.info(f"Stored security rule: {rule.id}")
                    
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(f"Failed to store security rule {rule.id}: {str(e)}")
    
    async def _create_rule_version(self, conn: sqlite3.Connection, rule_id: str, rule: SecurityRule) -> None:
        """Create a new version entry for rule changes"""
        # Get next version number
        result = conn.execute(
            "SELECT MAX(version) FROM rule_versions WHERE rule_id = ?",
            (rule_id,)
        ).fetchone()
        
        next_version = (result[0] or 0) + 1
        
        rule_data = json.dumps(rule.model_dump(), default=str)
        checksum = self._calculate_checksum(rule_data)
        
        conn.execute("""
            INSERT INTO rule_versions 
            (rule_id, version, rule_data, modified_at, change_reason, checksum)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            rule_id, next_version, rule_data, datetime.now(),
            "Rule updated", checksum
        ))
    
    async def get_security_rule(self, rule_id: str) -> Optional[SecurityRule]:
        """Get security rule by ID with integrity validation"""
        async with self.get_connection() as conn:
            try:
                row = conn.execute("""
                    SELECT id, name, description, severity, pattern, remediation, 
                           source, status, created_at, checksum
                    FROM security_rules WHERE id = ?
                """, (rule_id,)).fetchone()
                
                if not row:
                    return None
                
                rule_dict = {
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'severity': Severity(row['severity']),
                    'pattern': row['pattern'],
                    'remediation': row['remediation'],
                    'source': RuleSource(row['source']),
                    'status': RuleStatus(row['status']),
                    'created_at': datetime.fromisoformat(row['created_at'])
                }
                
                # Validate integrity
                if not self._validate_data_integrity(row['checksum'], rule_dict):
                    logger.warning(f"Data integrity check failed for rule {rule_id}")
                    raise DatabaseError(f"Data integrity check failed for rule {rule_id}")
                
                return SecurityRule(**rule_dict)
                
            except Exception as e:
                raise DatabaseError(f"Failed to get security rule {rule_id}: {str(e)}")
    
    async def get_rules_by_status(self, status: RuleStatus) -> List[SecurityRule]:
        """Get all rules with specific status"""
        async with self.get_connection() as conn:
            try:
                rows = conn.execute("""
                    SELECT id, name, description, severity, pattern, remediation, 
                           source, status, created_at, checksum
                    FROM security_rules WHERE status = ?
                    ORDER BY created_at DESC
                """, (status.value,)).fetchall()
                
                rules = []
                for row in rows:
                    rule_dict = {
                        'id': row['id'],
                        'name': row['name'],
                        'description': row['description'],
                        'severity': Severity(row['severity']),
                        'pattern': row['pattern'],
                        'remediation': row['remediation'],
                        'source': RuleSource(row['source']),
                        'status': RuleStatus(row['status']),
                        'created_at': datetime.fromisoformat(row['created_at'])
                    }
                    
                    # Validate integrity
                    if self._validate_data_integrity(row['checksum'], rule_dict):
                        rules.append(SecurityRule(**rule_dict))
                    else:
                        logger.warning(f"Skipping rule {row['id']} due to integrity check failure")
                
                return rules
                
            except Exception as e:
                raise DatabaseError(f"Failed to get rules by status {status}: {str(e)}")
    
    async def delete_security_rule(self, rule_id: str) -> bool:
        """Delete security rule and all related data"""
        with self._lock:
            async with self.get_connection() as conn:
                try:
                    # Check if rule exists
                    exists = conn.execute(
                        "SELECT 1 FROM security_rules WHERE id = ?",
                        (rule_id,)
                    ).fetchone()
                    
                    if not exists:
                        return False
                    
                    # Delete rule (cascades to related tables)
                    conn.execute("DELETE FROM security_rules WHERE id = ?", (rule_id,))
                    conn.commit()
                    
                    logger.info(f"Deleted security rule: {rule_id}")
                    return True
                    
                except Exception as e:
                    conn.rollback()
                    raise DatabaseError(f"Failed to delete security rule {rule_id}: {str(e)}")
    
    async def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create database backup"""
        if not self.backup_enabled:
            raise DatabaseError("Backup is disabled")
        
        if not backup_name:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        backup_path = self.backup_dir / backup_name
        
        try:
            # Create backup using SQLite backup API
            with sqlite3.connect(self.db_path) as source:
                with sqlite3.connect(backup_path) as backup:
                    source.backup(backup)
            
            logger.info(f"Database backup created: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            raise DatabaseError(f"Failed to create backup: {str(e)}")
    
    async def restore_backup(self, backup_path: str) -> None:
        """Restore database from backup"""
        backup_file = Path(backup_path)
        if not backup_file.exists():
            raise DatabaseError(f"Backup file not found: {backup_path}")
        
        try:
            # Create temporary backup of current database
            temp_backup = await self.create_backup("temp_before_restore")
            
            # Replace current database with backup
            shutil.copy2(backup_file, self.db_path)
            
            # Verify restored database
            self._initialize_database()  # This will validate schema
            
            logger.info(f"Database restored from backup: {backup_path}")
            
        except Exception as e:
            # Try to restore from temp backup if restoration failed
            try:
                shutil.copy2(temp_backup, self.db_path)
                logger.info("Restored from temporary backup after failed restoration")
            except:
                pass
            raise DatabaseError(f"Failed to restore backup: {str(e)}")
    
    async def cleanup_old_backups(self, keep_days: int = 30) -> None:
        """Clean up old backup files"""
        if not self.backup_enabled:
            return
        
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        
        try:
            for backup_file in self.backup_dir.glob("backup_*.db"):
                if backup_file.stat().st_mtime < cutoff_date.timestamp():
                    backup_file.unlink()
                    logger.info(f"Deleted old backup: {backup_file}")
                    
        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {str(e)}")
    
    async def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics and health information"""
        async with self.get_connection() as conn:
            try:
                stats = {}
                
                # Table row counts
                tables = ['security_rules', 'rule_versions', 'rule_metrics', 'rule_conflicts',
                         'cloud_logs', 'ml_findings', 'scan_results']
                
                for table in tables:
                    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                    stats[f"{table}_count"] = count
                
                # Database size
                stats['database_size_bytes'] = self.db_path.stat().st_size
                
                # Last backup info
                if self.backup_enabled and self.backup_dir.exists():
                    backups = list(self.backup_dir.glob("backup_*.db"))
                    if backups:
                        latest_backup = max(backups, key=lambda x: x.stat().st_mtime)
                        stats['last_backup'] = datetime.fromtimestamp(latest_backup.stat().st_mtime).isoformat()
                        stats['backup_count'] = len(backups)
                
                return stats
                
            except Exception as e:
                raise DatabaseError(f"Failed to get database stats: {str(e)}")