from dataclasses import dataclass
import datetime
import uuid
from typing import Dict, List, Optional
from .enums import AgeGroup, TraitCategory

@dataclass
class UserProfile:
    """User profile data class"""
    name: str
    age: int
    age_group: AgeGroup
    profile_pic: str = "default.png"
    id: str = ""
    created_at: str = None
    last_updated: str = None
    
    def __post_init__(self):
        """Initialize default values"""
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.created_at:
            self.created_at = datetime.datetime.now().isoformat()
        if not self.last_updated:
            self.last_updated = datetime.datetime.now().isoformat()
    
    @property
    def display_name(self):
        """Get display name with age"""
        return f"{self.name} (Age {self.age})"
        
    @classmethod
    def from_dict(cls, data_dict):
        """Create instance from dictionary"""
        # Handle age_group conversion from string to Enum
        if 'age_group' in data_dict and isinstance(data_dict['age_group'], str):
            data_dict['age_group'] = AgeGroup(data_dict['age_group'])
        return cls(**data_dict)

@dataclass
class PersonalityInsight:
    """Personality insight data class"""
    user_id: str
    category: TraitCategory
    traits: Dict[str, float]  # trait_name: score
    context: Dict  # Additional contextual information
    confidence_score: float
    timestamp: str = None
    id: str = ""
    
    def __post_init__(self):
        """Initialize default values"""
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.datetime.now().isoformat()
            
    @classmethod
    def from_dict(cls, data_dict):
        """Create instance from dictionary"""
        # Handle category conversion from string to Enum
        if 'category' in data_dict and isinstance(data_dict['category'], str):
            data_dict['category'] = TraitCategory(data_dict['category'])
        return cls(**data_dict)

@dataclass
class DevelopmentalTip:
    """Developmental tip data class"""
    trait_name: str
    score: float
    description: str
    tips: List[str]
    color: List[float]  # RGBA
    
    @classmethod
    def from_insight(cls, insight: PersonalityInsight, trait_name: str):
        """Create a tip from an insight for a specific trait"""
        # Color mapping based on trait score
        score = insight.traits.get(trait_name, 0.5)
        
        if score > 0.7:
            color = [0.0, 0.7, 0.3, 1.0]  # Green
        elif score > 0.4:
            color = [0.0, 0.5, 0.8, 1.0]  # Blue
        else:
            color = [0.8, 0.3, 0.3, 1.0]  # Red
            
        # Generate description and tips based on trait and score
        description = f"Score: {score:.0%}"
        tips = [f"Suggested activity for {trait_name}"]
        
        return cls(
            trait_name=trait_name,
            score=score,
            description=description,
            tips=tips,
            color=color
        )
