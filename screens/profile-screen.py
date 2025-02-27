from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

from models.enums import AgeGroup
from models.data_classes import UserProfile

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = None
        self.secure_manager = None
        self.privacy_manager = None
        self.current_profile = None
        
        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        # We'll populate the rest in initialize() when data managers are available
        self.add_widget(self.layout)
    
    def initialize(self, db_manager, secure_manager, privacy_manager):
        """Initialize screen with data managers"""
        self.db_manager = db_manager
        self.secure_manager = secure_manager
        self.privacy_manager = privacy_manager
        
        # Now build the UI
        self._build_ui()
    
    def _build_ui(self):
        """Build the UI elements"""
        # Clear existing widgets
        self.layout.clear_widgets()
        
        # Header with title
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(50))
        title = Label(
            text='My Children',
            font_size='22sp',
            bold=True,
            halign='left',
            size_hint_x=0.7
        )
        settings_btn = Button(
            text='⚙️',
            size_hint_x=0.15,
            background_color=(0.9, 0.9, 0.9, 1)
        )
        settings_btn.bind(on_press=self.show_settings)
        
        logout_btn = Button(
            text='↩️',
            size_hint_x=0.15,
            background_color=(0.9, 0.9, 0.9, 1)
        )
        logout_btn.bind(on_press=self.logout)
        
        header.add_widget(title)
        header.add_widget(settings_btn)
        header.add_widget(logout_btn)
        
        # Add profile button
        add_profile_btn = Button(
            text='+ Add Child',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.3, 0.7, 0.3, 1)
        )
        add_profile_btn.bind(on_press=self.show_add_profile)
        
        # Profile grid
        self.profile_grid = GridLayout(
            cols=3, 
            spacing=dp(10), 
            size_hint_y=None,
            height=dp(120)
        )
        
        # Selected profile display
        self.profile_display = Label(
            text="Select a child profile",
            size_hint_y=None,
            height=dp(30)
        )
        
        # Action buttons
        action_layout = GridLayout(
            cols=2, 
            spacing=dp(10), 
            size_hint_y=None,
            height=dp(220)
        )
        
        insights_btn = Button(
            text='View Insights',
            background_color=(0.2, 0.6, 1, 1)
        )
        insights_btn.bind(on_press=self.show_insights)
        
        tips_btn = Button(
            text='Development Tips',
            background_color=(0.2, 0.8, 0.4, 1)
        )
        tips_btn.bind(on_press=self.show_tips)
        
        track_btn = Button(
            text='Track New Behavior',
            background_color=(1, 0.6, 0.2, 1)
        )
        track_btn.bind(on_press=self.show_track_behavior)
        
        progress_btn = Button(
            text='Progress Over Time',
            background_color=(0.8, 0.4, 0.8, 1)
        )
        progress_btn.bind(on_press=self.show_progress)
        
        action_layout.add_widget(insights_btn)
        action_layout.add_widget(tips_btn)
        action_layout.add_widget(track_btn)
        action_layout.add_widget(progress_btn)
        
        # Add a disclaimer
        disclaimer = Label(
            text='Child personality traits are fluid and constantly evolving.\nThis app provides insights for entertainment and discussion,\nnot clinical assessment.',
            font_size='12sp',
            italic=True,
            color=(0.5, 0.5, 0.5, 1),
            halign='center',
            size_hint_y=None,
            height=dp(60)
        )
        
        # Add all components to the main layout
        self.layout.add_widget(header)
        self.layout.add_widget(add_profile_btn)
        self.layout.add_widget(self.profile_grid)
        self.layout.add_widget(self.profile_display)
        self.layout.add_widget(action_layout)
        
        # Add spacer
        self.layout.add_widget(Label())
        
        self.layout.add_widget(disclaimer)
        
        # Load profiles
        self.load_profiles()
    
    def load_profiles(self):
        """Load profiles from database and display them"""
        # Clear existing profile buttons
        self.profile_grid.clear_widgets()
        
        # Get profiles from database
        profiles = self.db_manager.get_profiles()
        
        if not profiles:
            # No profiles - add a message
            no_profiles = Label(
                text="No profiles found.\nAdd a child to get started.",
                halign='center'
            )
            self.profile_grid.add_widget(no_profiles)
            return
        
        # Add a button for each profile
        for profile in profiles:
            btn = Button(
                text=f"{profile.name}\nAge {profile.age}",
                halign='center',
                background_color=self._get_age_color(profile.age_group)
            )
            btn.profile = profile  # Store profile in button for later reference
            btn.bind(on_press=self.select_profile)
            self.profile_grid.add_widget(btn)
            
        # Select the first profile by default
        self.current_profile = profiles[0]
        self.profile_display.text = f"Selected: {self.current_profile.display_name}"
    
    def _get_age_color(self, age_group):
        """Get a color based on age group"""
        if age_group == AgeGroup.TODDLER:
            return (0.2, 0.8, 0.8, 1)  # Teal
        elif age_group == AgeGroup.CHILD:
            return (0.2, 0.6, 1, 1)    # Blue
        else:
            return (0.6, 0.4, 0.8, 1)  # Purple
    
    def select_profile(self, button):
        """Handle profile selection"""
        self.current_profile = button.profile
        self.profile_display.text = f"Selected: {self.current_profile.display_name}"
    
    def show_insights(self, instance):
        """Show insights for the selected profile"""
        if not self.current_profile:
            self._show_error_popup("Please select a child profile first")
            return
        
        # Pass the current profile to the insights screen
        insights_screen = self.manager.get_screen('insights')
        insights_screen.set_profile(self.current_profile)
        
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'insights'
    
    def show_tips(self, instance):
        """Show development tips for the selected profile"""
        if not self.current_profile:
            self._show_error_popup("Please select a child profile first")
            return
        
        # Pass the current profile to the tips screen
        tips_screen = self.manager.get_screen('tips')
        tips_screen.set_profile(self.current_profile)
        
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'tips'
    
    def show_track_behavior(self, instance):
        """Show track behavior screen for the selected profile"""
        if not self.current_profile:
            self._show_error_popup("Please select a child profile first")
            return
        
        # Pass the current profile to the track behavior screen
        track_screen = self.manager.get_screen('track_behavior')
        track_screen.set_profile(self.current_profile)
        
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'track_behavior'
    
    def show_progress(self, instance):
        """Show progress screen"""
        if not self.current_profile:
            self._show_error_popup("Please select a child profile first")
            return
            
        # We'll use insights screen for this as well
        insights_screen = self.manager.get_screen('insights')
        insights_screen.set_profile(self.current_profile, show_progress=True)
        
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'insights'
    
    def show_settings(self, instance):
        """Show settings screen"""
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'settings'
    
    def logout(self, instance):
        """Handle logout button press"""
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'login'
    
    def show_add_profile(self, instance):
        """Show popup to add a new profile"""
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))
        
        # Form fields
        name_input = TextInput(
            hint_text='Child Name',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        
        age_input = TextInput(
            hint_text='Age',
            multiline=False,
            input_filter='int',
            size_hint_y=None,
            height=dp(40)
        )
        
        # Buttons
        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        cancel_btn = Button(text='Cancel')
        save_btn = Button(text='Save', background_color=(0.2, 0.7, 0.2, 1))
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(save_btn)
        
        # Add widgets to content
        content.add_widget(Label(text='Add New Child', size_hint_y=None, height=dp(40), font_size='18sp'))
        content.add_widget(name_input)
        content.add_widget(age_input)
        content.add_widget(buttons)
        
        # Create popup
        popup = Popup(
            title='Add New Child',
            content=content,
            size_hint=(0.8, 0.5),
            auto_dismiss=False
        )
        
        # Bind buttons
        cancel_btn.bind(on_press=popup.dismiss)
        save_btn.bind(on_press=lambda x: self._save_new_profile(name_input.text, age_input.text, popup))
        
        popup.open()
    
    def _save_new_profile(self, name, age_str, popup):
        """Save a new profile"""
        if not name:
            self._show_error_popup("Please enter a name")
            return
            
        if not age_str:
            self._show_error_popup("Please enter an age")
            return
            
        try:
            age = int(age_str)
            if age < 1 or age > 18:
                self._show_error_popup("Age must be between 1 and 18")
                return
        except ValueError:
            self._show_error_popup("Please enter a valid age")
            return
        
        # Determine age group
        if age <= 5:
            age_group = AgeGroup.TODDLER
        elif age <= 12:
            age_group = AgeGroup.CHILD
        else:
            age_group = AgeGroup.TEEN
        
        # Create and save the profile
        profile = UserProfile(
            name=name,
            age=age,
            age_group=age_group
        )
        
        self.db_manager.save_profile(profile)
        
        # Close popup
        popup.dismiss()
        
        # Reload profiles
        self.load_profiles()
    
    def _show_error_popup(self, message):
        """Show an error popup with the given message"""
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message))
        
        btn = Button(text='OK', size_hint_y=None, height=dp(50))
        content.add_widget(btn)
        
        popup = Popup(
            title='Error',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        btn.bind(on_press=popup.dismiss)
        popup.open()
