#!/usr/bin/env python3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform

# Import local modules
from screens.login_screen import LoginScreen
from screens.profile_screen import ProfileScreen
from screens.insights_screen import InsightsScreen
from screens.tips_screen import TipsScreen
from screens.settings_screen import SettingsScreen
from screens.privacy_dashboard import PrivacyDashboardScreen
from screens.data_management import DataManagementScreen
from screens.track_behavior import TrackBehaviorScreen

from models.data_manager import SQLiteManager
from models.secure_manager import SecureDataManager
from models.privacy_manager import PrivacyManager

# Set window size to mobile phone dimensions for desktop testing
if platform != 'android' and platform != 'ios':
    Window.size = (400, 700)
    Window.clearcolor = (0.95, 0.95, 0.95, 1)

class ChildInsightApp(App):
    """Main application class for Child Insight & Growth Tracker"""
    
    def build(self):
        """Build the application"""
        # Initialize data managers
        self.db_manager = SQLiteManager()
        self.secure_manager = SecureDataManager(self.db_manager)
        self.privacy_manager = PrivacyManager(self.db_manager)
        
        # Apply data retention policy on startup
        self.db_manager.apply_retention_policy()
        
        # Create screen manager
        sm = ScreenManager(transition=SlideTransition())
        
        # Add screens
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(InsightsScreen(name='insights'))
        sm.add_widget(TipsScreen(name='tips'))
        sm.add_widget(SettingsScreen(name='settings'))
        sm.add_widget(PrivacyDashboardScreen(name='privacy'))
        sm.add_widget(DataManagementScreen(name='data_management'))
        sm.add_widget(TrackBehaviorScreen(name='track_behavior'))
        
        # Initialize screens with data managers
        for screen in sm.screens:
            if hasattr(screen, 'initialize'):
                screen.initialize(self.db_manager, self.secure_manager, self.privacy_manager)
        
        return sm
    
    def on_pause(self):
        """Handle app pause event"""
        return True
    
    def on_resume(self):
        """Handle app resume event"""
        pass
    
    def on_stop(self):
        """Handle app stop event - clean up resources"""
        self.db_manager.close()

if __name__ == '__main__':
    ChildInsightApp().run()
