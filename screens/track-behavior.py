from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.metrics import dp
import datetime

from models.enums import AgeGroup, TraitCategory
from models.data_classes import PersonalityInsight

class TrackBehaviorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = None
        self.secure_manager = None
        self.privacy_manager = None
        self.profile = None
        self.sliders = {}
        
        # Main layout
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # Header with back button and title
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        back_btn = Button(
            text='←',
            size_hint_x=0.2,
            background_color=(0.9, 0.9, 0.9, 1)
        )
        back_btn.bind(on_press=self.go_back)
        
        self.title_label = Label(
            text='Track Behavior',
            font_size='18sp',
            bold=True,
            size_hint_x=0.8
        )
        
        header.add_widget(back_btn)
        header.add_widget(self.title_label)
        
        # Date display
        date_layout = BoxLayout(size_hint_y=None, height=dp(30))
        date_label = Label(
            text='Date:',
            size_hint_x=0.3,
            halign='left'
        )
        date_label.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
        
        self.date_value = Label(
            text=datetime.datetime.now().strftime("%B %d, %Y"),
            size_hint_x=0.7,
            halign='right'
        )
        self.date_value.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
        
        date_layout.add_widget(date_label)
        date_layout.add_widget(self.date_value)
        
        # Child name display
        self.child_name = Label(
            text="",
            font_size='16sp',
            size_hint_y=None,
            height=dp(30)
        )
        
        # Create scrollable content for trait sliders
        from kivy.uix.scrollview import ScrollView
        scroll_view = ScrollView()
        
        self.traits_layout = GridLayout(
            cols=1, 
            spacing=dp(10), 
            size_hint_y=None
        )
        self.traits_layout.bind(minimum_height=self.traits_layout.setter('height'))
        
        scroll_view.add_widget(self.traits_layout)
        
        # Save button
        save_btn = Button(
            text='SAVE OBSERVATIONS',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.7, 0.2, 1)
        )
        save_btn.bind(on_press=self.save_observations)
        
        # Disclaimer
        disclaimer = Label(
            text='These observations help generate insights over time.\nThey are not clinical assessments.',
            font_size='12sp',
            italic=True,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(40)
        )
        
        # Add all components to the main layout
        layout.add_widget(header)
        layout.add_widget(date_layout)
        layout.add_widget(self.child_name)
        layout.add_widget(scroll_view)
        layout.add_widget(save_btn)
        layout.add_widget(disclaimer)
        
        self.add_widget(layout)
    
    def initialize(self, db_manager, secure_manager, privacy_manager):
        """Initialize screen with data managers"""
        self.db_manager = db_manager
        self.secure_manager = secure_manager
        self.privacy_manager = privacy_manager
    
    def set_profile(self, profile):
        """Set the profile and update content"""
        self.profile = profile
        self.title_label.text = f"Track: {profile.name}"
        self.child_name.text = f"Observing behaviors for {profile.display_name}"
        self.update_content()
    
    def update_content(self):
        """Update content based on profile age group"""
        if not self.profile:
            return
        
        # Clear existing sliders
        self.traits_layout.clear_widgets()
        self.sliders = {}
        
        # Get trait categories based on age group
        if self.profile.age_group == AgeGroup.TODDLER:
            self._add_toddler_traits()
        elif self.profile.age_group == AgeGroup.CHILD:
            self._add_child_traits()
        else:  # TEEN
            self._add_teen_traits()
    
    def _add_toddler_traits(self):
        """Add toddler-specific traits (ages 1-5)"""
        self._add_trait_category("Temperament")
        
        self._add_trait_slider(
            "adaptability",
            "Adaptability to Change",
            "Resists Change",
            "Adapts Easily"
        )
        
        self._add_trait_slider(
            "sensitivity",
            "Sensitivity to Stimuli",
            "Less Sensitive",
            "More Sensitive"
        )
        
        self._add_trait_slider(
            "social_engagement",
            "Social Engagement",
            "Prefers Alone",
            "Seeks Interaction"
        )
    
    def _add_child_traits(self):
        """Add child-specific traits (ages 6-12)"""
        self._add_trait_category("Planning & Organization")
        
        self._add_trait_slider(
            "planning_preference",
            "Planning Preference",
            "Spontaneous",
            "Structured"
        )
        
        self._add_trait_category("Social Interaction")
        
        self._add_trait_slider(
            "social_energy",
            "Social Energy",
            "Prefers Quiet",
            "Seeks Groups"
        )
        
        self._add_trait_category("Learning & Creativity")
        
        self._add_trait_slider(
            "learning_style",
            "Learning Approach",
            "Hands-on",
            "Conceptual"
        )
        
        self._add_trait_slider(
            "creativity",
            "Creative Expression",
            "Practical",
            "Imaginative"
        )
    
    def _add_teen_traits(self):
        """Add teen-specific traits (ages 13-18)"""
        self._add_trait_category("Personality Traits")
        
        self._add_trait_slider(
            "extraversion",
            "Social Energy",
            "Inward Focused",
            "Outward Focused"
        )
        
        self._add_trait_slider(
            "openness",
            "Openness to New Experiences",
            "Prefers Familiar",
            "Seeks Novelty"
        )
        
        self._add_trait_slider(
            "conscientiousness",
            "Organization & Planning",
            "Flexible",
            "Structured"
        )
        
        self._add_trait_slider(
            "agreeableness",
            "Approach to Others",
            "Independent",
            "Cooperative"
        )
        
        self._add_trait_slider(
            "emotional_stability",
            "Emotional Management",
            "Variable",
            "Steady"
        )
    
    def _add_trait_category(self, category_name):
        """Add a category header to the traits layout"""
        category = Label(
            text=category_name,
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=dp(40),
            halign='left'
        )
        category.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
        
        self.traits_layout.add_widget(category)
    
    def _add_trait_slider(self, trait_id, trait_name, low_label, high_label):
        """Add a trait slider to the layout"""
        # Container for this trait
        trait_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(80),
            padding=[0, 5]
        )
        
        # Trait name
        name_label = Label(
            text=trait_name,
            font_size='14sp',
            size_hint_y=None,
            height=dp(20),
            halign='left'
        )
        name_label.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
        
        # Slider layout
        slider_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(40)
        )
        
        # Create slider
        slider = Slider(
            min=0,
            max=1,
            value=0.5,
            step=0.05,
            size_hint_x=0.8
        )
        
        # Value display
        value_label = Label(
            text='50%',
            size_hint_x=0.2,
            halign='right'
        )
        value_label.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
        
        # Update value label when slider changes
        def update_value(instance, value):
            value_label.text = f"{int(value * 100)}%"
        
        slider.bind(value=update_value)
        
        # Add to slider layout
        slider_layout.add_widget(slider)
        slider_layout.add_widget(value_label)
        
        # Labels for low/high ends
        ends_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(20)
        )
        
        low_end = Label(
            text=low_label,
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            halign='left',
            size_hint_x=0.5
        )
        low_end.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
        
        high_end = Label(
            text=high_label,
            font_size='12sp',
            color=(0.5, 0.5, 0.5, 1),
            halign='right',
            size_hint_x=0.5
        )
        high_end.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
        
        ends_layout.add_widget(low_end)
        ends_layout.add_widget(high_end)
        
        # Add everything to trait container
        trait_container.add_widget(name_label)
        trait_container.add_widget(slider_layout)
        trait_container.add_widget(ends_layout)
        
        # Add to traits layout
        self.traits_layout.add_widget(trait_container)
        
        # Store slider reference
        self.sliders[trait_id] = slider
    
    def save_observations(self, instance):
        """Save the current observations as an insight"""
        if not self.db_manager or not self.profile:
            self._show_message_popup("Error", "Unable to save observations.")
            return
        
        # Collect trait values
        traits = {}
        for trait_id, slider in self.sliders.items():
            traits[trait_id] = slider.value
        
        # Determine trait category based on age group
        if self.profile.age_group == AgeGroup.TODDLER:
            category = TraitCategory.TEMPERAMENT
        elif self.profile.age_group == AgeGroup.CHILD:
            category = TraitCategory.MBTI_INSPIRED
        else:  # TEEN
            category = TraitCategory.BIG_FIVE
        
        # Create insight
        insight = PersonalityInsight(
            user_id=self.profile.id,
            category=category,
            traits=traits,
            context={"source": "manual_observation"},
            confidence_score=0.9  # High confidence for manual input
        )
        
        # Save to database
        try:
            self.db_manager.save_insight(insight)
            self._show_message_popup(
                "Success",
                "Observations saved successfully!",
                self.go_back
            )
        except Exception as e:
            self._show_message_popup("Error", f"Failed to save observations: {str(e)}")
    
    def go_back(self, instance=None):
        """Return to profile screen"""
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'profile'
    
    def _show_message_popup(self, title, message, callback=None):
        """Show a message popup"""
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message, halign='center'))
        
        btn = Button(text='OK', size_hint_y=None, height=dp(50))
        content.add_widget(btn)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        if callback:
            btn.bind(on_press=lambda x: self._dismiss_and_callback(popup, callback))
        else:
            btn.bind(on_press=popup.dismiss)
            
        popup.open()
    
    def _dismiss_and_callback(self, popup, callback):
        """Dismiss popup and call callback"""
        popup.dismiss()
        callback()
