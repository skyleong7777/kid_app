from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle

class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = None
        self.secure_manager = None
        self.privacy_manager = None
        
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
        
        title_label = Label(
            text='Settings',
            font_size='18sp',
            bold=True,
            size_hint_x=0.8
        )
        
        header.add_widget(back_btn)
        header.add_widget(title_label)
        
        # Create settings sections
        account_section = self._create_section_header("Account Settings")
        privacy_section = self._create_section_header("Privacy & Data")
        appearance_section = self._create_section_header("Appearance")
        about_section = self._create_section_header("About")
        
        # Create settings items
        account_items = GridLayout(cols=1, spacing=dp(2), size_hint_y=None, height=dp(100))
        self._add_setting_item(account_items, "Account Information", self.show_account_info)
        self._add_setting_item(account_items, "Change Password", self.show_change_password)
        
        privacy_items = GridLayout(cols=1, spacing=dp(2), size_hint_y=None, height=dp(150))
        self._add_setting_item(privacy_items, "Privacy Dashboard", self.show_privacy_dashboard)
        self._add_setting_item(privacy_items, "Data Management", self.show_data_management)
        self._add_setting_item(privacy_items, "Export All Data", self.export_all_data)
        
        appearance_items = GridLayout(cols=1, spacing=dp(2), size_hint_y=None, height=dp(100))
        
        # Theme setting with switch
        theme_layout = BoxLayout(size_hint_y=None, height=dp(50))
        theme_label = Label(
            text="Dark Theme",
            halign='left',
            valign='center',
            size_hint_x=0.8
        )
        theme_switch = Switch(active=False, size_hint_x=0.2)
        theme_switch.bind(active=self.toggle_theme)
        
        theme_layout.add_widget(theme_label)
        theme_layout.add_widget(theme_switch)
        appearance_items.add_widget(theme_layout)
        
        # Font size setting
        self._add_setting_item(appearance_items, "Font Size", self.change_font_size)
        
        about_items = GridLayout(cols=1, spacing=dp(2), size_hint_y=None, height=dp(150))
        self._add_setting_item(about_items, "Version: 1.0.0", None)
        self._add_setting_item(about_items, "Help & Support", self.show_help)
        self._add_setting_item(about_items, "Terms of Service", self.show_terms)
        
        # Logout button
        logout_btn = Button(
            text='Logout',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.8, 0.2, 0.2, 1)
        )
        logout_btn.bind(on_press=self.logout)
        
        # Add all sections to layout
        layout.add_widget(header)
        layout.add_widget(account_section)
        layout.add_widget(account_items)
        layout.add_widget(privacy_section)
        layout.add_widget(privacy_items)
        layout.add_widget(appearance_section)
        layout.add_widget(appearance_items)
        layout.add_widget(about_section)
        layout.add_widget(about_items)
        
        # Add spacer
        layout.add_widget(Label())
        
        layout.add_widget(logout_btn)
        
        self.add_widget(layout)
    
    def initialize(self, db_manager, secure_manager, privacy_manager):
        """Initialize screen with data managers"""
        self.db_manager = db_manager
        self.secure_manager = secure_manager
        self.privacy_manager = privacy_manager
    
    def _create_section_header(self, title):
        """Create a section header"""
        section = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(40)
        )
        
        label = Label(
            text=title,
            font_size='16sp',
            bold=True,
            halign='left',
            valign='bottom',
            size_hint_y=None,
            height=dp(30)
        )
        label.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
        
        separator = BoxLayout(size_hint_y=None, height=dp(1))
        with separator.canvas.before:
            Color(0.7, 0.7, 0.7, 1)
            Rectangle(pos=separator.pos, size=separator.size)
        separator.bind(pos=self._update_rect, size=self._update_rect)
        
        section.add_widget(label)
        section.add_widget(separator)
        
        return section
    
    def _add_setting_item(self, container, text, callback):
        """Add a setting item to the container"""
        item = Button(
            text=text,
            size_hint_y=None,
            height=dp(50),
            background_color=(0.95, 0.95, 0.95, 1),
            color=(0.2, 0.2, 0.2, 1),
            halign='left',
            valign='center'
        )
        item.bind(size=lambda s, w: setattr(s, 'text_size', (w[0] - dp(20), None)))
        
        if callback:
            item.bind(on_press=callback)
        else:
            item.disabled = True
        
        container.add_widget(item)
        
        # Add small separator
        separator = BoxLayout(size_hint_y=None, height=dp(1))
        with separator.canvas.before:
            Color(0.9, 0.9, 0.9, 1)
            Rectangle(pos=separator.pos, size=separator.size)
        separator.bind(pos=self._update_rect, size=self._update_rect)
        
        container.add_widget(separator)
    
    def _update_rect(self, instance, value):
        """Update rectangle position and size"""
        instance.canvas.before.clear()
        with instance.canvas.before:
            if hasattr(self, 'rect_color'):
                Color(*self.rect_color)
            else:
                Color(0.9, 0.9, 0.9, 1)
            Rectangle(pos=instance.pos, size=instance.size)
    
    def go_back(self, instance):
        """Return to profile screen"""
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'profile'
    
    def show_account_info(self, instance):
        """Show account information"""
        self._show_message_popup("Account Information", "Demo account\nEmail: demo@example.com")
    
    def show_change_password(self, instance):
        """Show change password dialog"""
        self._show_message_popup("Change Password", "Password change is not available in demo mode.")
    
    def show_privacy_dashboard(self, instance):
        """Show privacy dashboard"""
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'privacy'
    
    def show_data_management(self, instance):
        """Show data management screen"""
        self.manager.transition = SlideTransition(direction='left')
        self.manager.current = 'data_management'
    
    def export_all_data(self, instance):
        """Export all data"""
        if not self.secure_manager:
            self._show_message_popup("Error", "Data manager not initialized.")
            return
            
        try:
            import os
            
            # Create exports directory if it doesn't exist
            if not os.path.exists('exports'):
                os.makedirs('exports')
                
            # Generate export path with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = os.path.join('exports', f'all_data_{timestamp}.json')
            
            # Export data
            result = self.secure_manager.export_data(export_path)
            
            self._show_message_popup("Export Successful", f"Data exported to:\n{export_path}")
        except Exception as e:
            self._show_message_popup("Export Error", f"Failed to export data: {str(e)}")
    
    def toggle_theme(self, instance, value):
        """Toggle dark/light theme"""
        # This would modify app appearance in a real implementation
        theme = "Dark" if value else "Light"
        self._show_message_popup("Theme Changed", f"Theme set to {theme}.\nThis is a demo feature.")
    
    def change_font_size(self, instance):
        """Change font size"""
        self._show_message_popup("Font Size", "Font size adjustment is a demo feature.")
    
    def show_help(self, instance):
        """Show help and support information"""
        self._show_message_popup("Help & Support", 
                                "Child Insight & Growth Tracker\nDemo Version\n\nFor assistance, contact: support@example.com")
    
    def show_terms(self, instance):
        """Show terms of service"""
        self._show_message_popup("Terms of Service", 
                                "This application is for demonstration purposes only.\n\nAll data is stored locally on your device.")
    
    def logout(self, instance):
        """Log out and return to login screen"""
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'login'
    
    def _show_message_popup(self, title, message):
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
        
        btn.bind(on_press=popup.dismiss)
        popup.open()
