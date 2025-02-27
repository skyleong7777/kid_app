from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.metrics import dp

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = None
        self.secure_manager = None
        self.privacy_manager = None
        
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        # Title and logo
        title = Label(
            text='Child Insight & Growth Tracker',
            font_size='22sp',
            bold=True,
            size_hint_y=None,
            height=dp(50)
        )
        
        # Username and password fields
        self.username = TextInput(
            multiline=False,
            hint_text='Email',
            size_hint_y=None,
            height=dp(50),
            padding=[10, 15, 10, 15]
        )
        self.password = TextInput(
            multiline=False,
            password=True,
            hint_text='Password',
            size_hint_y=None,
            height=dp(50),
            padding=[10, 15, 10, 15]
        )
        
        # Login button
        login_btn = Button(
            text='LOGIN',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.6, 1, 1)
        )
        login_btn.bind(on_press=self.login)
        
        # Demo mode button
        demo_btn = Button(
            text='DEMO MODE',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.8, 0.8, 0.8, 1)
        )
        demo_btn.bind(on_press=self.demo_login)
        
        # Disclaimer
        disclaimer = Label(
            text='For entertainment and developmental insight purposes only.\nNot a clinical diagnostic tool.',
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            halign='center',
            valign='top',
            size_hint_y=None,
            height=dp(40)
        )
        
        # Add widgets to layout
        layout.add_widget(title)
        
        # Add a spacer
        layout.add_widget(Label(size_hint_y=None, height=dp(40)))
        
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(login_btn)
        layout.add_widget(demo_btn)
        
        # Add another spacer before disclaimer
        layout.add_widget(Label(size_hint_y=None, height=dp(40)))
        
        layout.add_widget(disclaimer)
        
        # Add layout to screen
        self.add_widget(layout)
    
    def initialize(self, db_manager, secure_manager, privacy_manager):
        """Initialize screen with data managers"""
        self.db_manager = db_manager
        self.secure_manager = secure_manager
        self.privacy_manager = privacy_manager

    def login(self, instance):
        """Handle login button press"""
        # In a real app, we would verify credentials here
        # For demo purposes, just navigate to the profile screen
        self.manager.current = 'profile'

    def demo_login(self, instance):
        """Handle demo mode button press"""
        # Create demo data if needed
        self._create_demo_data()
        
        # Navigate to profile screen
        self.manager.current = 'profile'
    
    def _create_demo_data(self):
        """Create demo profiles and insights for testing"""
        from datetime import datetime, timedelta
        import random
        from models.enums import AgeGroup, TraitCategory
        from models.data_classes import UserProfile, PersonalityInsight
        
        # Check if demo data already exists
        profiles = self.db_manager.get_profiles()
        if profiles:
            return  # Demo data already exists
        
        # Create demo profiles
        demo_profiles = [
            UserProfile(
                name="Emma",
                age=4,
                age_group=AgeGroup.TODDLER
            ),
            UserProfile(
                name="Noah",
                age=9,
                age_group=AgeGroup.CHILD
            ),
            UserProfile(
                name="Olivia",
                age=15,
                age_group=AgeGroup.TEEN
            )
        ]
        
        # Save profiles to database
        for profile in demo_profiles:
            self.db_manager.save_profile(profile)
        
        # Create demo insights - 5 for each profile over the last 5 months
        for profile in demo_profiles:
            # Determine trait category based on age group
            if profile.age_group == AgeGroup.TODDLER:
                category = TraitCategory.TEMPERAMENT
                traits = {
                    "adaptability": [0.65, 0.68, 0.7, 0.72, 0.75],
                    "sensitivity": [0.5, 0.48, 0.45, 0.43, 0.42],
                    "social_engagement": [0.55, 0.6, 0.65, 0.68, 0.72]
                }
            elif profile.age_group == AgeGroup.CHILD:
                category = TraitCategory.MBTI_INSPIRED
                traits = {
                    "planning_preference": [0.5, 0.52, 0.55, 0.58, 0.6],
                    "social_energy": [0.7, 0.72, 0.73, 0.74, 0.75],
                    "learning_style": [0.6, 0.63, 0.65, 0.68, 0.7],
                    "creativity": [0.8, 0.81, 0.82, 0.84, 0.85]
                }
            else:  # TEEN
                category = TraitCategory.BIG_FIVE
                traits = {
                    "extraversion": [0.35, 0.38, 0.4, 0.42, 0.45],
                    "openness": [0.8, 0.82, 0.85, 0.87, 0.9],
                    "conscientiousness": [0.65, 0.67, 0.7, 0.72, 0.75],
                    "agreeableness": [0.7, 0.72, 0.73, 0.75, 0.76],
                    "emotional_stability": [0.55, 0.58, 0.61, 0.64, 0.67]
                }
            
            # Create an insight for each of the last 5 months
            for i in range(5):
                # Calculate date - most recent to oldest
                date = datetime.now() - timedelta(days=30 * (4 - i))
                
                # Create trait dictionary for this insight
                trait_values = {}
                for trait_name, values in traits.items():
                    trait_values[trait_name] = values[i]
                
                # Create insight
                insight = PersonalityInsight(
                    user_id=profile.id,
                    category=category,
                    traits=trait_values,
                    context={"source": "demo_data"},
                    confidence_score=0.85,
                    timestamp=date.isoformat()
                )
                
                # Save insight to database
                self.db_manager.save_insight(insight)
