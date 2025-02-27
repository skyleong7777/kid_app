from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import numpy as np
from datetime import datetime, timedelta

from models.enums import AgeGroup, TraitCategory
from models.data_classes import UserProfile, PersonalityInsight

class InsightsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = None
        self.secure_manager = None
        self.privacy_manager = None
        self.profile = None
        self.show_progress_mode = False
        
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
            text='Insights',
            font_size='18sp',
            bold=True,
            size_hint_x=0.8
        )
        
        header.add_widget(back_btn)
        header.add_widget(self.title_label)
        
        # Create a ScrollView for the main content
        scroll_view = ScrollView()
        self.content_layout = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            padding=dp(10),
            size_hint_y=None
        )
        self.content_layout.bind(minimum_height=self.content_layout.setter('height'))
        
        # Placeholders for dynamic content
        self.graph_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(300)
        )
        
        self.traits_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(10)
        )
        self.traits_container.bind(minimum_height=self.traits_container.setter('height'))
        
        # Add containers to content layout
        self.content_layout.add_widget(Label(
            text='Trait Development Over Time',
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=dp(30)
        ))
        self.content_layout.add_widget(self.graph_container)
        
        self.content_layout.add_widget(Label(
            text='Current Trait Analysis',
            font_size='16sp',
            bold=True,
            size_hint_y=None,
            height=dp(30)
        ))
        self.content_layout.add_widget(self.traits_container)
        
        # Disclaimer at the bottom
        disclaimer = Label(
            text='Insights are based on recent observations and are not clinical assessments.',
            font_size='12sp',
            italic=True,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(30)
        )
        
        # Add the scroll view to the main layout
        scroll_view.add_widget(self.content_layout)
        
        # Assemble the screen
        layout.add_widget(header)
        layout.add_widget(scroll_view)
        layout.add_widget(disclaimer)
        
        self.add_widget(layout)
    
    def initialize(self, db_manager, secure_manager, privacy_manager):
        """Initialize screen with data managers"""
        self.db_manager = db_manager
        self.secure_manager = secure_manager
        self.privacy_manager = privacy_manager
    
    def set_profile(self, profile, show_progress=False):
        """Set the profile for display and update content"""
        self.profile = profile
        self.show_progress_mode = show_progress
        
        if show_progress:
            self.title_label.text = f"Progress: {profile.display_name}"
        else:
            self.title_label.text = f"Insights: {profile.display_name}"
            
        self.update_content()
    
    def update_content(self):
        """Update content based on the current profile"""
        if not self.profile:
            return
        
        # Clear existing content
        self.graph_container.clear_widgets()
        self.traits_container.clear_widgets()
        
        # Generate interactive graph based on age group
        self.generate_graph()
        
        # Generate trait analysis based on age group
        self.generate_trait_analysis()
    
    def generate_graph(self):
        """Generate and display a graph of trait development over time"""
        # Get insights for this profile
        insights = self.db_manager.get_insights(
            user_id=self.profile.id, 
            limit=10
        )
        
        if not insights:
            # No insights available
            self.graph_container.add_widget(Label(
                text="No insight data available yet.\nTrack behaviors to generate insights.",
                halign='center'
            ))
            return
        
        # Sort insights by timestamp
        insights.sort(key=lambda x: x.timestamp)
        
        # Create a matplotlib figure
        fig = Figure(figsize=(6, 4), dpi=80)
        ax = fig.add_subplot(111)
        
        # Extract dates and trait values
        dates = [datetime.fromisoformat(insight.timestamp) for insight in insights]
        
        # Different traits based on age group
        trait_names = list(insights[0].traits.keys())
        
        # Create a dataset for each trait
        traits = {}
        for trait_name in trait_names:
            traits[trait_name] = [insight.traits.get(trait_name, 0) for insight in insights]
        
        # Set title based on age group/category
        if self.profile.age_group == AgeGroup.TODDLER:
            title = "Temperament Trends"
        elif self.profile.age_group == AgeGroup.CHILD:
            title = "MBTI-Inspired Preferences"
        else:  # TEEN
            title = "Big Five Traits"
        
        # Plot each trait
        colors = ['#FF5722', '#2196F3', '#4CAF50', '#9C27B0', '#FFC107']
        for i, (trait_name, values) in enumerate(traits.items()):
            ax.plot(dates, values, marker='o', label=trait_name.replace('_', ' ').title(), 
                   linewidth=2, color=colors[i % len(colors)])
        
        # Customize the plot
        ax.set_title(title)
        ax.set_ylim(0, 1)
        ax.set_ylabel('Trait Score')
        ax.xaxis.set_major_formatter(DateFormatter('%b %Y'))
        ax.legend(loc='lower right')
        fig.autofmt_xdate()
        
        if len(dates) > 1:
            # Add interactivity - highlight current values
            latest_values = [values[-1] for values in traits.values()]
            latest_traits = list(traits.keys())
            
            # Find highest trait
            max_idx = latest_values.index(max(latest_values))
            ax.plot(dates[-1], latest_values[max_idx], 'o', markersize=10, 
                    fillstyle='none', color=colors[max_idx], linewidth=2)
            
            # Add a text annotation
            highlight_trait = latest_traits[max_idx].replace('_', ' ').title()
            text = f"Highest trait: {highlight_trait} - {latest_values[max_idx]:.0%}"
            
            ax.annotate(text, xy=(dates[-1], latest_values[max_idx]), 
                       xytext=(dates[-2], min(latest_values[max_idx]+0.15, 0.95)),
                       arrowprops=dict(facecolor='black', shrink=0.05, width=1.5),
                       bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
        
        # Adjust layout
        fig.tight_layout()
        
        # Convert to Kivy widget
        canvas = FigureCanvasKivyAgg(fig)
        self.graph_container.add_widget(canvas)
    
    def generate_trait_analysis(self):
        """Generate and display trait analysis based on the most recent insight"""
        # Get the most recent insight
        insights = self.db_manager.get_insights(
            user_id=self.profile.id, 
            limit=1
        )
        
        if not insights:
            # No insights available
            self.traits_container.add_widget(Label(
                text="No insight data available yet.\nTrack behaviors to generate insights.",
                halign='center'
            ))
            return
        
        latest_insight = insights[0]
        
        # Generate descriptions based on age group
        if self.profile.age_group == AgeGroup.TODDLER:
            descriptions = {
                "adaptability": "Adapts well to new situations and changes in routine.",
                "sensitivity": "Level of sensitivity to sensory stimuli and emotional input.",
                "social_engagement": "Enjoyment of social interaction and group play."
            }
        elif self.profile.age_group == AgeGroup.CHILD:
            descriptions = {
                "planning_preference": "Preference for structure and planning ahead.",
                "social_energy": "Energy derived from social interaction with peers.",
                "learning_style": "Balance between concrete examples and theoretical concepts.",
                "creativity": "Creative problem-solving and artistic expression."
            }
        else:  # TEEN
            descriptions = {
                "extraversion": "Tendency toward outward expression vs. internal reflection.",
                "openness": "Curiosity about new experiences, ideas, and perspectives.",
                "conscientiousness": "Organization, persistence, and goal-directed behavior.",
                "agreeableness": "Cooperative and considerate approach to others.",
                "emotional_stability": "Ability to manage emotions and handle stress."
            }
        
        # Add MBTI correlation for teens
        if self.profile.age_group == AgeGroup.TEEN:
            # Add MBTI type based on Big Five scores
            mbti_box = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(90),
                padding=dp(10),
                spacing=dp(5)
            )
            
            # Add background color
            with mbti_box.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.9, 0.9, 1, 1)
                self.rect = Rectangle(pos=mbti_box.pos, size=mbti_box.size)
                mbti_box.bind(pos=self._update_rect, size=self._update_rect)
            
            mbti_label = Label(
                text='MBTI-Inspired Type',
                font_size='14sp',
                bold=True,
                size_hint_y=None,
                height=dp(20)
            )
            
            # Calculate MBTI based on Big Five
            traits = latest_insight.traits
            e_i = "I" if traits.get("extraversion", 0) < 0.5 else "E"
            s_n = "N" if traits.get("openness", 0) > 0.5 else "S"
            t_f = "F" if traits.get("agreeableness", 0) > 0.5 else "T"
            j_p = "J" if traits.get("conscientiousness", 0) > 0.5 else "P"
            
            mbti_type = f"{e_i}{s_n}{t_f}{j_p}"
            
            mbti_value = Label(
                text=mbti_type,
                font_size='24sp',
                bold=True,
                color=(0.2, 0.4, 0.6, 1)
            )
            
            mbti_disclaimer = Label(
                text='(Exploratory and subject to change)',
                font_size='12sp',
                italic=True,
                color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None,
                height=dp(20)
            )
            
            mbti_box.add_widget(mbti_label)
            mbti_box.add_widget(mbti_value)
            mbti_box.add_widget(mbti_disclaimer)
            
            self.traits_container.add_widget(mbti_box)
        
        # Add each trait analysis widget
        for trait_name, score in latest_insight.traits.items():
            trait_layout = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(90),
                padding=dp(5)
            )
            
            # Get description
            description = descriptions.get(trait_name, f"Score for {trait_name}.")
            
            # Color based on score
            if score > 0.7:
                color = [0.0, 0.7, 0.3, 1.0]  # Green
            elif score > 0.4:
                color = [0.0, 0.5, 0.8, 1.0]  # Blue
            else:
                color = [0.8, 0.3, 0.3, 1.0]  # Red
            
            # Trait name and score
            header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25))
            name_label = Label(
                text=trait_name.replace('_', ' ').title(),
                font_size='14sp',
                bold=True,
                halign='left',
                size_hint_x=0.7,
                color=(0.2, 0.2, 0.2, 1)
            )
            score_label = Label(
                text=f"{score:.0%}",
                font_size='14sp',
                bold=True,
                halign='right',
                size_hint_x=0.3,
                color=color
            )
            
            header.add_widget(name_label)
            header.add_widget(score_label)
            
            # Progress bar
            bar_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(20), padding=(0, 5))
            
            # Create custom progress bar
            progress = BoxLayout(size_hint_x=score)
            with progress.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(*color)
                Rectangle(pos=progress.pos, size=progress.size)
            progress.bind(pos=self._update_rect, size=self._update_rect)
            
            empty = BoxLayout(size_hint_x=1-score)
            with empty.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.9, 0.9, 0.9, 1)
                Rectangle(pos=empty.pos, size=empty.size)
            empty.bind(pos=self._update_rect, size=self._update_rect)
            
            bar_layout.add_widget(progress)
            bar_layout.add_widget(empty)
            
            # Description
            desc_label = Label(
                text=description,
                font_size='12sp',
                text_size=(self.width - dp(30), None),
                halign='left',
                valign='top',
                size_hint_y=None,
                height=dp(40)
            )
            
            # Add all components to the trait layout
            trait_layout.add_widget(header)
            trait_layout.add_widget(bar_layout)
            trait_layout.add_widget(desc_label)
            
            # Add a separator
            separator = BoxLayout(size_hint_y=None, height=1)
            with separator.canvas.before:
                from kivy.graphics import Color, Rectangle
                Color(0.9, 0.9, 0.9, 1)
                Rectangle(pos=separator.pos, size=separator.size)
            separator.bind(pos=self._update_rect, size=self._update_rect)
            
            # Add to the main container
            self.traits_container.add_widget(trait_layout)
            self.traits_container.add_widget(separator)
    
    def _update_rect(self, instance, value):
        """Update rectangle position and size"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def go_back(self, instance):
        """Return to profile screen"""
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'profile'
