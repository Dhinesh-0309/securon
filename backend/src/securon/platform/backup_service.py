"""Backup and recovery service for Securon platform"""

import asyncio
import logging
import shutil
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    schedule = None

import time
from threading import Thread

from .data_access import SecuronDataAccess, DataAccessError
from .config import PlatformConfig


logger = logging.getLogger(__name__)


@dataclass
class BackupInfo:
    """Information about a backup"""
    name: str
    path: str
    size_bytes: int
    created_at: datetime
    backup_type: str  # 'manual', 'scheduled', 'emergency'
    description: Optional[str] = None


class BackupService:
    """Comprehensive backup and recovery service"""
    
    def __init__(self, data_access: SecuronDataAccess, config: Optional[PlatformConfig] = None):
        self.data_access = data_access
        self.config = config or PlatformConfig()
        
        # Backup configuration
        self.backup_enabled = self.config.get('rule_engine.backup_enabled', True)
        self.backup_interval_hours = self.config.get('rule_engine.backup_interval_hours', 24)
        self.backup_retention_days = self.config.get('rule_engine.backup_retention_days', 30)
        self.max_backups = self.config.get('rule_engine.max_backups', 50)
        
        # Backup directories
        self.backup_root = Path(self.config.get('rule_engine.backup_path', 'data/backups'))
        self.db_backup_dir = self.backup_root / 'database'
        self.config_backup_dir = self.backup_root / 'config'
        self.logs_backup_dir = self.backup_root / 'logs'
        
        # Create directories
        for directory in [self.db_backup_dir, self.config_backup_dir, self.logs_backup_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Scheduler for automatic backups
        self._scheduler_thread = None
        self._scheduler_running = False
        
        if self.backup_enabled:
            self._setup_scheduler()
        
        logger.info(f"BackupService initialized with {self.backup_interval_hours}h interval")
    
    def _setup_scheduler(self):
        """Setup automatic backup scheduler"""
        if not self.backup_enabled or not SCHEDULE_AVAILABLE:
            if not SCHEDULE_AVAILABLE:
                logger.warning("Schedule module not available, automatic backups disabled")
            return
        
        # Schedule regular backups
        schedule.every(self.backup_interval_hours).hours.do(self._scheduled_backup)
        
        # Schedule cleanup
        schedule.every().day.at("02:00").do(self._scheduled_cleanup)
        
        # Start scheduler thread
        self._scheduler_running = True
        self._scheduler_thread = Thread(target=self._run_scheduler, daemon=True)
        self._scheduler_thread.start()
        
        logger.info("Backup scheduler started")
    
    def _run_scheduler(self):
        """Run the backup scheduler"""
        if not SCHEDULE_AVAILABLE:
            return
            
        while self._scheduler_running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except Exception as e:
                logger.error(f"Scheduler error: {str(e)}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _scheduled_backup(self):
        """Perform scheduled backup"""
        try:
            asyncio.run(self.create_full_backup(
                backup_type='scheduled',
                description=f"Scheduled backup at {datetime.now().isoformat()}"
            ))
        except Exception as e:
            logger.error(f"Scheduled backup failed: {str(e)}")
    
    def _scheduled_cleanup(self):
        """Perform scheduled cleanup"""
        try:
            asyncio.run(self.cleanup_old_backups())
        except Exception as e:
            logger.error(f"Scheduled cleanup failed: {str(e)}")
    
    async def create_database_backup(self, backup_name: Optional[str] = None) -> BackupInfo:
        """Create database backup"""
        if not backup_name:
            backup_name = f"db_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        try:
            backup_path = await self.data_access.create_backup(backup_name)
            backup_file = Path(backup_path)
            
            # Move to organized backup directory
            organized_path = self.db_backup_dir / backup_file.name
            shutil.move(backup_path, organized_path)
            
            backup_info = BackupInfo(
                name=backup_file.name,
                path=str(organized_path),
                size_bytes=organized_path.stat().st_size,
                created_at=datetime.now(),
                backup_type='database'
            )
            
            logger.info(f"Database backup created: {organized_path}")
            return backup_info
            
        except Exception as e:
            logger.error(f"Database backup failed: {str(e)}")
            raise
    
    async def create_config_backup(self) -> BackupInfo:
        """Create configuration backup"""
        backup_name = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = self.config_backup_dir / backup_name
        
        try:
            # Collect configuration data
            config_data = {
                'platform_config': self.config.to_dict() if hasattr(self.config, 'to_dict') else {},
                'system_health': await self.data_access.get_system_health(),
                'backup_info': {
                    'created_at': datetime.now().isoformat(),
                    'backup_type': 'configuration',
                    'version': '1.0'
                }
            }
            
            # Save configuration
            with open(backup_path, 'w') as f:
                json.dump(config_data, f, indent=2, default=str)
            
            backup_info = BackupInfo(
                name=backup_name,
                path=str(backup_path),
                size_bytes=backup_path.stat().st_size,
                created_at=datetime.now(),
                backup_type='configuration'
            )
            
            logger.info(f"Configuration backup created: {backup_path}")
            return backup_info
            
        except Exception as e:
            logger.error(f"Configuration backup failed: {str(e)}")
            raise
    
    async def create_full_backup(self, 
                               backup_type: str = 'manual',
                               description: Optional[str] = None) -> Dict[str, BackupInfo]:
        """Create comprehensive backup of all system data"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            backups = {}
            
            # Database backup
            db_backup = await self.create_database_backup(f"full_db_{timestamp}.db")
            db_backup.backup_type = backup_type
            db_backup.description = description
            backups['database'] = db_backup
            
            # Configuration backup
            config_backup = await self.create_config_backup()
            config_backup.backup_type = backup_type
            config_backup.description = description
            backups['configuration'] = config_backup
            
            # Create backup manifest
            manifest = {
                'backup_id': f"full_{timestamp}",
                'created_at': datetime.now().isoformat(),
                'backup_type': backup_type,
                'description': description,
                'components': {
                    'database': {
                        'name': db_backup.name,
                        'path': db_backup.path,
                        'size_bytes': db_backup.size_bytes
                    },
                    'configuration': {
                        'name': config_backup.name,
                        'path': config_backup.path,
                        'size_bytes': config_backup.size_bytes
                    }
                },
                'total_size_bytes': sum(b.size_bytes for b in backups.values())
            }
            
            manifest_path = self.backup_root / f"manifest_{timestamp}.json"
            with open(manifest_path, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            logger.info(f"Full backup completed: {len(backups)} components, {manifest['total_size_bytes']} bytes")
            return backups
            
        except Exception as e:
            logger.error(f"Full backup failed: {str(e)}")
            raise
    
    async def restore_database_backup(self, backup_path: str) -> None:
        """Restore database from backup"""
        backup_file = Path(backup_path)
        if not backup_file.exists():
            raise ValueError(f"Backup file not found: {backup_path}")
        
        try:
            await self.data_access.restore_backup(str(backup_file))
            logger.info(f"Database restored from: {backup_path}")
            
        except Exception as e:
            logger.error(f"Database restore failed: {str(e)}")
            raise
    
    async def restore_full_backup(self, manifest_path: str) -> None:
        """Restore full backup from manifest"""
        manifest_file = Path(manifest_path)
        if not manifest_file.exists():
            raise ValueError(f"Manifest file not found: {manifest_path}")
        
        try:
            with open(manifest_file, 'r') as f:
                manifest = json.load(f)
            
            # Restore database
            if 'database' in manifest['components']:
                db_path = manifest['components']['database']['path']
                await self.restore_database_backup(db_path)
            
            # Note: Configuration restore would require application restart
            # This is typically handled by the platform orchestrator
            
            logger.info(f"Full backup restored from manifest: {manifest_path}")
            
        except Exception as e:
            logger.error(f"Full backup restore failed: {str(e)}")
            raise
    
    async def list_backups(self, backup_type: Optional[str] = None) -> List[BackupInfo]:
        """List available backups"""
        backups = []
        
        try:
            # Database backups
            for backup_file in self.db_backup_dir.glob("*.db"):
                if backup_type and backup_type != 'database':
                    continue
                
                backup_info = BackupInfo(
                    name=backup_file.name,
                    path=str(backup_file),
                    size_bytes=backup_file.stat().st_size,
                    created_at=datetime.fromtimestamp(backup_file.stat().st_mtime),
                    backup_type='database'
                )
                backups.append(backup_info)
            
            # Configuration backups
            for backup_file in self.config_backup_dir.glob("*.json"):
                if backup_type and backup_type != 'configuration':
                    continue
                
                backup_info = BackupInfo(
                    name=backup_file.name,
                    path=str(backup_file),
                    size_bytes=backup_file.stat().st_size,
                    created_at=datetime.fromtimestamp(backup_file.stat().st_mtime),
                    backup_type='configuration'
                )
                backups.append(backup_info)
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x.created_at, reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Failed to list backups: {str(e)}")
            raise
    
    async def cleanup_old_backups(self) -> Dict[str, int]:
        """Clean up old backup files"""
        if not self.backup_enabled:
            return {'deleted': 0, 'kept': 0}
        
        cutoff_date = datetime.now() - timedelta(days=self.backup_retention_days)
        deleted_count = 0
        kept_count = 0
        
        try:
            # Get all backups
            all_backups = await self.list_backups()
            
            # Sort by type and date
            backups_by_type = {}
            for backup in all_backups:
                if backup.backup_type not in backups_by_type:
                    backups_by_type[backup.backup_type] = []
                backups_by_type[backup.backup_type].append(backup)
            
            # Clean up each type
            for backup_type, backups in backups_by_type.items():
                # Sort by date (newest first)
                backups.sort(key=lambda x: x.created_at, reverse=True)
                
                # Keep recent backups and respect max_backups limit
                for i, backup in enumerate(backups):
                    should_delete = (
                        backup.created_at < cutoff_date and i >= self.max_backups
                    ) or i >= self.max_backups
                    
                    if should_delete:
                        try:
                            Path(backup.path).unlink()
                            deleted_count += 1
                            logger.info(f"Deleted old backup: {backup.name}")
                        except Exception as e:
                            logger.warning(f"Failed to delete backup {backup.name}: {str(e)}")
                    else:
                        kept_count += 1
            
            # Clean up old manifests
            for manifest_file in self.backup_root.glob("manifest_*.json"):
                if datetime.fromtimestamp(manifest_file.stat().st_mtime) < cutoff_date:
                    try:
                        manifest_file.unlink()
                        logger.info(f"Deleted old manifest: {manifest_file.name}")
                    except Exception as e:
                        logger.warning(f"Failed to delete manifest {manifest_file.name}: {str(e)}")
            
            logger.info(f"Backup cleanup completed: {deleted_count} deleted, {kept_count} kept")
            return {'deleted': deleted_count, 'kept': kept_count}
            
        except Exception as e:
            logger.error(f"Backup cleanup failed: {str(e)}")
            raise
    
    async def get_backup_status(self) -> Dict[str, Any]:
        """Get backup system status"""
        try:
            backups = await self.list_backups()
            
            # Calculate statistics
            total_backups = len(backups)
            total_size = sum(b.size_bytes for b in backups)
            
            # Group by type
            by_type = {}
            for backup in backups:
                if backup.backup_type not in by_type:
                    by_type[backup.backup_type] = {'count': 0, 'size_bytes': 0}
                by_type[backup.backup_type]['count'] += 1
                by_type[backup.backup_type]['size_bytes'] += backup.size_bytes
            
            # Find latest backup
            latest_backup = max(backups, key=lambda x: x.created_at) if backups else None
            
            status = {
                'enabled': self.backup_enabled,
                'interval_hours': self.backup_interval_hours,
                'retention_days': self.backup_retention_days,
                'max_backups': self.max_backups,
                'total_backups': total_backups,
                'total_size_bytes': total_size,
                'by_type': by_type,
                'latest_backup': {
                    'name': latest_backup.name,
                    'created_at': latest_backup.created_at.isoformat(),
                    'size_bytes': latest_backup.size_bytes
                } if latest_backup else None,
                'backup_directories': {
                    'root': str(self.backup_root),
                    'database': str(self.db_backup_dir),
                    'configuration': str(self.config_backup_dir)
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get backup status: {str(e)}")
            return {
                'enabled': self.backup_enabled,
                'error': str(e)
            }
    
    def stop_scheduler(self):
        """Stop the backup scheduler"""
        self._scheduler_running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5)
        logger.info("Backup scheduler stopped")
    
    def __del__(self):
        """Cleanup on destruction"""
        self.stop_scheduler()