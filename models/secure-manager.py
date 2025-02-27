import os
import json
import base64
import hashlib
import datetime
import uuid
from dataclasses import asdict
from typing import Dict, List, Optional, Tuple

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .data_manager import SQLiteManager
from .data_classes import UserProfile, PersonalityInsight

class SecureDataManager:
    """Handles secure export, import and backup of application data"""
    
    def __init__(self, db_manager: SQLiteManager, backup_dir: str = "backups"):
        """Initialize with database manager and backup directory"""
        self.db_manager = db_manager
        self.backup_dir = backup_dir
        
        # Create backup directory if it doesn't exist
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
    
    def _generate_key_from_password(self, password: str, salt: bytes = None) -> Tuple[Fernet, bytes]:
        """Generate an encryption key from a password"""
        if salt is None:
            salt = os.urandom(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return Fernet(key), salt
    
    def export_data(self, file_path: str, password: str = None, 
                   anonymize: bool = False, selected_profiles: List[str] = None) -> str:
        """Export all data, optionally encrypted with a password"""
        # Fetch profiles from database
        if selected_profiles:
            profiles = [self.db_manager.get_profile(p_id) for p_id in selected_profiles]
            profiles = [p for p in profiles if p]  # Filter out None values
        else:
            profiles = self.db_manager.get_profiles()
        
        # Anonymize profile data if requested
        if anonymize:
            profiles = self._anonymize_profiles(profiles)
        
        # Fetch insights for selected profiles
        all_insights = []
        for profile in profiles:
            insights = self.db_manager.get_insights(user_id=profile.id, limit=1000)
            all_insights.extend(insights)
        
        # Prepare export data
        export_data = {
            'version': '1.0',
            'timestamp': datetime.datetime.now().isoformat(),
            'profiles': [asdict(p) for p in profiles],
            'insights': [asdict(i) for i in all_insights],
        }
        
        # Convert Enum values to strings for serialization
        for profile_dict in export_data['profiles']:
            profile_dict['age_group'] = profile_dict['age_group'].value
        
        for insight_dict in export_data['insights']:
            insight_dict['category'] = insight_dict['category'].value
        
        # Convert to JSON
        json_data = json.dumps(export_data, indent=2)
        
        # Apply encryption if password is provided
        if password:
            cipher, salt = self._generate_key_from_password(password)
            encrypted_data = cipher.encrypt(json_data.encode())
            
            # Final file format: salt + encrypted data
            with open(file_path, 'wb') as f:
                f.write(salt)
                f.write(encrypted_data)
            
            # Log backup
            file_size = os.path.getsize(file_path)
            self.db_manager.log_backup(file_path, file_size, True)
            
            return f"Encrypted data exported to {file_path}"
        else:
            # Save as plaintext JSON
            with open(file_path, 'w') as f:
                f.write(json_data)
            
            # Log backup
            file_size = os.path.getsize(file_path)
            self.db_manager.log_backup(file_path, file_size, False)
            
            return f"Data exported to {file_path}"
    
    def import_data(self, file_path: str, password: str = None, 
                   merge: bool = False) -> str:
        """Import data from a file, optionally decrypting with a password"""
        try:
            # Check if file is encrypted (encrypted files are binary)
            is_encrypted = False
            with open(file_path, 'rb') as f:
                # Try to read as text - this will fail for encrypted files
                try:
                    f.read(10).decode('utf-8')
                    is_encrypted = False
                except UnicodeDecodeError:
                    is_encrypted = True
            
            # Re-open file for proper reading
            if is_encrypted:
                if not password:
                    return "Password required for encrypted file"
                
                with open(file_path, 'rb') as f:
                    # First 16 bytes are salt
                    salt = f.read(16)
                    encrypted_data = f.read()
                
                # Decrypt data
                cipher, _ = self._generate_key_from_password(password, salt)
                try:
                    json_data = cipher.decrypt(encrypted_data).decode()
                except Exception:
                    return "Invalid password or corrupted file"
            else:
                # Read plaintext JSON
                with open(file_path, 'r') as f:
                    json_data = f.read()
            
            # Parse JSON data
            import_data = json.loads(json_data)
            
            # Validate version
            if 'version' not in import_data:
                return "Invalid backup file format"
            
            # If not merging, clear existing data
            if not merge:
                # Get all existing profiles
                profiles = self.db_manager.get_profiles()
                for profile in profiles:
                    self.db_manager.delete_profile(profile.id)
            
            # Import profiles
            for profile_dict in import_data.get('profiles', []):
                profile = UserProfile.from_dict(profile_dict)
                self.db_manager.save_profile(profile)
            
            # Import insights
            for insight_dict in import_data.get('insights', []):
                insight = PersonalityInsight.from_dict(insight_dict)
                self.db_manager.save_insight(insight)
            
            return f"Successfully imported data from {file_path}"
        
        except Exception as e:
            return f"Error importing data: {str(e)}"
    
    def create_scheduled_backup(self) -> str:
        """Create an automatic backup with timestamp filename"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.json"
        file_path = os.path.join(self.backup_dir, filename)
        
        # Get password preference from settings
        encrypt_backups = self.db_manager.get_setting('encrypt_backups', 'false') == 'true'
        backup_password = self.db_manager.get_setting('backup_password', '')
        anonymize = self.db_manager.get_setting('anonymize_backups', 'false') == 'true'
        
        if encrypt_backups and backup_password:
            return self.export_data(file_path, backup_password, anonymize)
        else:
            return self.export_data(file_path, None, anonymize)
    
    def _anonymize_profiles(self, profiles: List[UserProfile]) -> List[UserProfile]:
        """Create anonymized copies of profiles for export"""
        anonymized = []
        
        for profile in profiles:
            # Create a copy
            anon_profile = UserProfile(
                name=f"Child_{hashlib.sha256(profile.name.encode()).hexdigest()[:8]}",
                age=profile.age,
                age_group=profile.age_group,
                profile_pic="default.png",
                id=profile.id,
                created_at=profile.created_at,
                last_updated=profile.last_updated
            )
            anonymized.append(anon_profile)
            
        return anonymized
    
    def delete_all_data(self) -> bool:
        """Delete all data (factory reset)"""
        try:
            # Close the connection
            self.db_manager.close()
            
            # Delete the database file
            if os.path.exists(self.db_manager.db_path):
                os.remove(self.db_manager.db_path)
            
            # Create a new empty database
            self.db_manager = SQLiteManager(self.db_manager.db_path)
            
            return True
        except Exception:
            return False
            
    def get_backup_info(self) -> Dict:
        """Get information about backups"""
        # Count backups
        backup_count = 0
        total_size = 0
        latest_backup = None
        
        if os.path.exists(self.backup_dir):
            backup_files = [f for f in os.listdir(self.backup_dir) 
                           if f.startswith('backup_') and f.endswith('.json')]
            backup_count = len(backup_files)
            
            if backup_files:
                # Get total size
                for f in backup_files:
                    file_path = os.path.join(self.backup_dir, f)
                    total_size += os.path.getsize(file_path)
                
                # Get latest backup
                backup_files.sort(reverse=True)  # Sort by name (which includes timestamp)
                latest_backup = backup_files[0]
        
        return {
            'count': backup_count,
            'total_size': total_size,
            'latest_backup': latest_backup,
            'backup_dir': os.path.abspath(self.backup_dir)
        }
