from typing import Dict, List, Optional
import datetime

from .data_manager import SQLiteManager

class PrivacyManager:
    """Manages privacy settings and data lifecycle"""
    
    def __init__(self, db_manager: SQLiteManager):
        self.db_manager = db_manager
    
    def set_retention_period(self, data_type: str, days: int) -> bool:
        """Set retention period for a data type"""
        cursor = self.db_manager.conn.cursor()
        try:
            cursor.execute(
                "UPDATE retention_policy SET retention_days = ? WHERE data_type = ?",
                (days, data_type)
            )
            self.db_manager.conn.commit()
            return True
        except Exception:
            return False
    
    def get_retention_period(self, data_type: str) -> int:
        """Get retention period for a data type"""
        cursor = self.db_manager.conn.cursor()
        cursor.execute(
            "SELECT retention_days FROM retention_policy WHERE data_type = ?",
            (data_type,)
        )
        
        row = cursor.fetchone()
        if row:
            return row[0]
        
        return 365  # Default
    
    def set_privacy_setting(self, key: str, value: str) -> bool:
        """Set a privacy-related setting"""
        try:
            self.db_manager.set_setting(f"privacy_{key}", value)
            return True
        except Exception:
            return False
    
    def get_privacy_setting(self, key: str, default: str = None) -> str:
        """Get a privacy-related setting"""
        return self.db_manager.get_setting(f"privacy_{key}", default)
    
    def anonymize_profile(self, profile_id: str) -> bool:
        """Anonymize a profile by removing identifiable information"""
        profile = self.db_manager.get_profile(profile_id)
        if not profile:
            return False
        
        # Create a hash of the name for pseudonymization
        import hashlib
        name_hash = hashlib.sha256(profile.name.encode()).hexdigest()[:8]
        
        # Update profile with anonymized data
        profile.name = f"Child_{name_hash}"
        profile.profile_pic = "default.png"
        
        # Save anonymized profile
        self.db_manager.save_profile(profile)
        return True
    
    def delete_old_data(self) -> int:
        """Apply retention policy and return number of deleted records"""
        cursor = self.db_manager.conn.cursor()
        
        # Get retention days
        retention_days = self.get_retention_period("insights")
        
        # Calculate cutoff date
        cutoff_date = (datetime.datetime.now() - 
                      datetime.timedelta(days=retention_days)).isoformat()
        
        # Count records to be deleted
        cursor.execute(
            "SELECT COUNT(*) FROM insights WHERE timestamp < ?",
            (cutoff_date,)
        )
        count = cursor.fetchone()[0]
        
        # Apply retention policy
        self.db_manager.apply_retention_policy()
        
        return count
    
    def get_privacy_status(self) -> Dict:
        """Get status of all privacy settings"""
        return {
            'encrypt_backups': self.get_privacy_setting('encrypt_backups', 'false') == 'true',
            'anonymize_exports': self.get_privacy_setting('anonymize_exports', 'false') == 'true',
            'auto_backup': self.get_privacy_setting('auto_backup', 'false') == 'true',
            'backup_frequency': self.get_privacy_setting('backup_frequency', 'weekly'),
            'retention_days': self.get_retention_period('insights')
        }
