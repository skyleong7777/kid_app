import os
import json
import sqlite3
import datetime
from dataclasses import asdict
from typing import List, Dict, Optional

from .enums import AgeGroup, TraitCategory
from .data_classes import UserProfile, PersonalityInsight

class SQLiteManager:
    """Manages local SQLite database for the application"""
    
    def __init__(self, db_path="child_insight.db"):
        """Initialize database connection and create tables if they don't exist"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
    
    def _create_tables(self):
        """Create necessary database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Profiles table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            age_group TEXT NOT NULL,
            profile_pic TEXT,
            created_at TEXT NOT NULL,
            last_updated TEXT NOT NULL,
            data TEXT NOT NULL
        )
        ''')
        
        # Insights table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS insights (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            category TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            confidence_score REAL NOT NULL,
            data TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES profiles (id)
        )
        ''')
        
        # Settings table for application settings
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        ''')
        
        # Backup history
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS backups (
            id TEXT PRIMARY KEY,
            timestamp TEXT NOT NULL,
            file_path TEXT NOT NULL,
            size INTEGER NOT NULL,
            encrypted INTEGER NOT NULL
        )
        ''')
        
        # Data retention policy
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS retention_policy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_type TEXT NOT NULL,
            retention_days INTEGER NOT NULL,
            last_cleanup TEXT
        )
        ''')
        
        # Insert default retention policies if not exist
        cursor.execute("SELECT COUNT(*) FROM retention_policy")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Default: keep insights for 365 days
            cursor.execute('''
            INSERT INTO retention_policy (data_type, retention_days, last_cleanup)
            VALUES ('insights', 365, ?)
            ''', (datetime.datetime.now().isoformat(),))
        
        self.conn.commit()
    
    def save_profile(self, profile: UserProfile):
        """Save a user profile to the database"""
        cursor = self.conn.cursor()
        
        # Convert dataclass to dict, preserving the enum as string
        profile_dict = asdict(profile)
        profile_dict['age_group'] = profile_dict['age_group'].value
        
        # Store the complex data as JSON string
        data_json = json.dumps(profile_dict)
        
        cursor.execute('''
        INSERT OR REPLACE INTO profiles 
        (id, name, age, age_group, profile_pic, created_at, last_updated, data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            profile.id,
            profile.name,
            profile.age,
            profile.age_group.value,
            profile.profile_pic,
            profile.created_at,
            datetime.datetime.now().isoformat(),
            data_json
        ))
        
        self.conn.commit()
    
    def get_profiles(self) -> List[UserProfile]:
        """Get all user profiles from the database"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT data FROM profiles ORDER BY name")
        
        profiles = []
        for row in cursor.fetchall():
            profile_dict = json.loads(row['data'])
            profiles.append(UserProfile.from_dict(profile_dict))
        
        return profiles
    
    def get_profile(self, profile_id: str) -> Optional[UserProfile]:
        """Get a specific profile by ID"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT data FROM profiles WHERE id = ?", (profile_id,))
        
        row = cursor.fetchone()
        if row:
            profile_dict = json.loads(row['data'])
            return UserProfile.from_dict(profile_dict)
        
        return None
    
    def delete_profile(self, profile_id: str) -> bool:
        """Delete a profile and all associated insights"""
        cursor = self.conn.cursor()
        
        # First delete associated insights
        cursor.execute("DELETE FROM insights WHERE user_id = ?", (profile_id,))
        
        # Then delete the profile
        cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        
        self.conn.commit()
        return cursor.rowcount > 0
    
    def save_insight(self, insight: PersonalityInsight):
        """Save a personality insight to the database"""
        cursor = self.conn.cursor()
        
        # Convert dataclass to dict
        insight_dict = asdict(insight)
        insight_dict['category'] = insight_dict['category'].value
        
        # Store the complex data as JSON string
        data_json = json.dumps(insight_dict)
        
        cursor.execute('''
        INSERT OR REPLACE INTO insights
        (id, user_id, category, timestamp, confidence_score, data)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            insight.id,
            insight.user_id,
            insight.category.value,
            insight.timestamp,
            insight.confidence_score,
            data_json
        ))
        
        self.conn.commit()
    
    def get_insights(self, user_id: str = None, limit: int = 100, 
                    category: TraitCategory = None) -> List[PersonalityInsight]:
        """Get insights, optionally filtered by user_id and category"""
        cursor = self.conn.cursor()
        
        query = "SELECT data FROM insights"
        params = []
        
        # Add filters
        if user_id or category:
            query += " WHERE"
            
            if user_id:
                query += " user_id = ?"
                params.append(user_id)
                
                if category:
                    query += " AND"
            
            if category:
                query += " category = ?"
                params.append(category.value)
        
        # Add ordering and limit
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, tuple(params))
        
        insights = []
        for row in cursor.fetchall():
            insight_dict = json.loads(row['data'])
            insights.append(PersonalityInsight.from_dict(insight_dict))
        
        return insights
    
    def delete_insight(self, insight_id: str) -> bool:
        """Delete a specific insight by ID"""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM insights WHERE id = ?", (insight_id,))
        self.conn.commit()
        return cursor.rowcount > 0
    
    def apply_retention_policy(self):
        """Apply retention policy to automatically clean up old data"""
        cursor = self.conn.cursor()
        
        # Get retention policies
        cursor.execute("SELECT data_type, retention_days FROM retention_policy")
        
        for row in cursor.fetchall():
            data_type = row['data_type']
            retention_days = row['retention_days']
            
            # Calculate cutoff date
            cutoff_date = (datetime.datetime.now() - 
                           datetime.timedelta(days=retention_days)).isoformat()
            
            if data_type == 'insights':
                cursor.execute(
                    "DELETE FROM insights WHERE timestamp < ?", 
                    (cutoff_date,)
                )
            
            # Update last cleanup timestamp
            cursor.execute(
                "UPDATE retention_policy SET last_cleanup = ? WHERE data_type = ?",
                (datetime.datetime.now().isoformat(), data_type)
            )
        
        self.conn.commit()
    
    def set_setting(self, key: str, value: str):
        """Save an application setting"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
            (key, value)
        )
        self.conn.commit()
    
    def get_setting(self, key: str, default: str = None) -> str:
        """Get an application setting"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        
        row = cursor.fetchone()
        if row:
            return row['value']
        
        return default
    
    def log_backup(self, file_path: str, size: int, encrypted: bool):
        """Log a backup operation"""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO backups (id, timestamp, file_path, size, encrypted) VALUES (?, ?, ?, ?, ?)",
            (str(datetime.uuid.uuid4()), datetime.datetime.now().isoformat(), file_path, size, 1 if encrypted else 0)
        )
        self.conn.commit()
    
    def get_backup_history(self) -> List[Dict]:
        """Get backup history"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id, timestamp, file_path, size, encrypted FROM backups ORDER BY timestamp DESC"
        )
        
        backups = []
        for row in cursor.fetchall():
            backups.append({
                'id': row['id'],
                'timestamp': row['timestamp'],
                'file_path': row['file_path'],
                'size': row['size'],
                'encrypted': bool(row['encrypted'])
            })
        
        return backups
    
    def get_data_summary(self) -> Dict:
        """Get summary statistics about stored data"""
        cursor = self.conn.cursor()
        
        # Count profiles
        cursor.execute("SELECT COUNT(*) FROM profiles")
        profiles_count = cursor.fetchone()[0]
        
        # Count insights
        cursor.execute("SELECT COUNT(*) FROM insights")
        insights_count = cursor.fetchone()[0]
        
        # Get insights by category
        cursor.execute("SELECT category, COUNT(*) as count FROM insights GROUP BY category")
        
        insights_by_category = {}
        for row in cursor.fetchall():
            insights_by_category[row['category']] = row['count']
            
        # Get oldest data
        cursor.execute("SELECT MIN(timestamp) FROM insights")
        oldest_row = cursor.fetchone()
        oldest_data = oldest_row[0] if oldest_row and oldest_row[0] else datetime.datetime.now().isoformat()
        
        # Get database file size
        db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
        
        # Get retention policy
        cursor.execute("SELECT retention_days FROM retention_policy WHERE data_type = 'insights' LIMIT 1")
        retention_row = cursor.fetchone()
        retention_days = retention_row[0] if retention_row else 365
        
        return {
            'profiles_count': profiles_count,
            'insights_count': insights_count,
            'insights_by_category': insights_by_category,
            'oldest_data': oldest_data,
            'storage_size': db_size,
            'retention_days': retention_days
        }
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
