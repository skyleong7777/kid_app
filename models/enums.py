from enum import Enum

class AgeGroup(Enum):
    """Age groups for the application"""
    TODDLER = "1-5"
    CHILD = "6-12"
    TEEN = "13-18"

class TraitCategory(Enum):
    """Categories for personality traits"""
    TEMPERAMENT = "temperament"
    MBTI_INSPIRED = "mbti_inspired"
    BIG_FIVE = "big_five"
    MULTIPLE_INTELLIGENCE = "multiple_intelligence"
    EQ = "emotional_intelligence"
