from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.switch import Switch
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.metrics import dp
import datetime

class PrivacyDashboardScreen(Screen):
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
            text='Privacy Dashboard',
            font_size='18sp',
            bold=True,
            size_hint_x=0.8
        )
        
        header.add_widget(back_btn)
        header.add_widget(title_label)
        
        # Create content sections
        data_summary_section = self._create_section_header("Data Summary")
        self.summary_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(150))
        
        retention_section = self._create_section_header("Data Retention")
        self.retention_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(130))
        
        # Insight retention slider
        slider_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(70))
        
        slider_header = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(25))
        slider_title = Label(text='Keep insights for:', halign='left', size_hint_x=0.7)
        self.slider_value = Label(text='365 days', halign='right', size_hint_x=0.3)
        slider_header.add_widget(slider_title)
        slider_header.add_widget(self.slider_value)
        
        # Slider for retention period
        self.retention_slider = Slider(min=30, max=730, step=30, value=365)
        self.retention_slider.bind(value=self.on_slider_value)
        
        slider_layout.add_widget(slider_header)
        slider_layout.add_widget(self.retention_slider)
        
        # Apply retention now button
        apply_btn = Button(
            text='Apply Retention Policy Now',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.3, 0.5, 0.8, 1)
        )
        apply_btn.bind(on_press=self.apply_retention_policy)
        
        self.retention_layout.add_widget(slider_layout)
        self.retention_layout.add_widget(apply_btn)
        
        privacy_controls_section = self._create_section_header("Privacy Controls")
        self.controls_layout = GridLayout(cols=2, spacing=dp(10), size_hint_y=None, height=dp(150))
        
        # Encrypt backups switch
        encrypt_label = Label(text='Encrypt Backups:', halign='left')
        self.encrypt_switch = Switch(active=False)
        self.encrypt_switch.bind(active=self.on_encrypt_changed)
        
        # Backup password
        password_label = Label(text='Backup Password:', halign='left')
        self.password_input = TextInput(
            password=True,
            multiline=False,
            hint_text='Enter password',
            disabled=True,
            size_hint_y=None,
            height=dp(40)
        )
        
        # Anonymize data switch
        anonymize_label = Label(text='Anonymize Exports:', halign='left')
        self.anonymize_switch = Switch(active=False)
        self.anonymize_switch.bind(active=self.on_anonymize_changed)
        
        self.controls_layout.add_widget(encrypt_label)
        self.controls_layout.add_widget(self.encrypt_switch)
        self.controls_layout.add_widget(password_label)
        self.controls_layout.add_widget(self.password_input)
        self.controls_layout.add_widget(anonymize_label)
        self.controls_layout.add_widget(self.anonymize_switch)
        
        data_management_section = self._create_section_header("Data Management")
        self.actions_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(100))
        
        # Delete old data button
        delete_old_btn = Button(
            text='Delete Old Data',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.8, 0.6, 0.2, 1)
        )
        delete_old_btn.bind(on_press=self.delete_old_data)
        
        # Delete all data button
        delete_all_btn = Button(
            text='Delete All Data (Factory Reset)',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.8, 0.2, 0.2, 1)
        )
        delete_all_btn.bind(on_press=self.delete_all_data)
        
        self.actions_layout.add_widget(delete_old_btn)
        self.actions_layout.add_widget(delete_all_btn)
        
        # Add all sections to layout
        layout.add_widget(header)
        layout.add_widget(data_summary_section)
        layout.add_widget(self.summary_layout)
        layout.add_widget(retention_section)
        layout.add_widget(self.retention_layout)
        layout.add_widget(privacy_controls_section)
        layout.add_widget(self.controls_layout)
        layout.add_widget(data_management_section)
        layout.add_widget(self.actions_layout)
        
        # Add spacer
        layout.add_widget(Label())
        
        self.add_widget(layout)
    
    def initialize(self, db_manager, secure_manager, privacy_manager):
        """Initialize screen with data managers"""
        self.db_manager = db_manager
        self.secure_manager = secure_manager
        self.privacy_manager = privacy_manager
    
    def on_pre_enter(self):
        """Called before the screen is displayed"""
        self.update_data_summary()
        self.load_settings()
    
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
        
        from kivy.graphics import Color, Rectangle
        separator = BoxLayout(size_hint_y=None, height=dp(1))
        with separator.canvas.before:
            Color(0.7, 0.7, 0.7, 1)
            Rectangle(pos=separator.pos, size=separator.size)
        
        section.add_widget(label)
        section.add_widget(separator)
        
        return section
    
    def update_data_summary(self):
        """Update data summary information"""
        if not self.db_manager:
            return
            
        # Clear existing widgets
        self.summary_layout.clear_widgets()
        
        # Get data summary
        summary = self.db_manager.get_data_summary()
        
        # Add summary items
        self._add_summary_item("Profiles:", f"{summary['profiles_count']}")
        self._add_summary_item("Insights:", f"{summary['insights_count']}")
        
        # Format data size
        storage_size = summary['storage_size']
        if storage_size < 1024:
            size_str = f"{storage_size} bytes"
        elif storage_size < 1024 * 1024:
            size_str = f"{storage_size / 1024:.1f} KB"
        else:
            size_str = f"{storage_size / (1024 * 1024):.1f} MB"
        
        self._add_summary_item("Storage Used:", size_str)
        
        # Format oldest data
        try:
            oldest_date = datetime.datetime.fromisoformat(summary['oldest_data'])
            date_str = oldest_date.strftime("%b %d, %Y")
        except:
            date_str = "No data"
            
        self._add_summary_item("Oldest Data:", date_str)
        
        # Set retention slider value
        self.retention_slider.value = summary['retention_days']
        self.slider_value.text = f"{int(self.retention_slider.value)} days"
    
    def load_settings(self):
        """Load current privacy settings"""
        if not self.privacy_manager:
            return
            
        # Get privacy settings
        privacy_status = self.privacy_manager.get_privacy_status()
        
        # Update UI elements
        self.encrypt_switch.active = privacy_status['encrypt_backups']
        self.anonymize_switch.active = privacy_status['anonymize_exports']
        self.password_input.disabled = not privacy_status['encrypt_backups']
        
        # Load backup password
        if privacy_status['encrypt_backups']:
            password = self.db_manager.get_setting('backup_password', '')
            self.password_input.text = password
    
    def _add_summary_item(self, label_text, value_text):
        """Add a summary item to the layout"""
        label = Label(
            text=label_text,
            halign='left',
            valign='middle'
        )
        label.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
        
        value = Label(
            text=value_text,
            halign='right',
            valign='middle',
            bold=True
        )
        value.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
        
        self.summary_layout.add_widget(label)
        self.summary_layout.add_widget(value)
    
    def on_slider_value(self, instance, value):
        """Update slider value display"""
        self.slider_value.text = f"{int(value)} days"
    
    def apply_retention_policy(self, instance):
        """Apply data retention policy"""
        if not self.privacy_manager:
            self._show_message_popup("Error", "Privacy manager not initialized.")
            return
            
        # Update retention period
        retention_days = int(self.retention_slider.value)
        self.privacy_manager.set_retention_period('insights', retention_days)
        
        # Apply retention policy
        deleted_count = self.privacy_manager.delete_old_data()
        
        if deleted_count > 0:
            self._show_message_popup("Retention Policy Applied", 
                                   f"{deleted_count} insights older than {retention_days} days have been deleted.")
        else:
            self._show_message_popup("Retention Policy Applied", 
                                   f"No insights older than {retention_days} days were found.")
    
    def on_encrypt_changed(self, instance, value):
        """Handle encrypt backups toggle"""
        self.password_input.disabled = not value
        
        if not self.privacy_manager:
            return
            
        # Save setting
        self.privacy_manager.set_privacy_setting('encrypt_backups', 'true' if value else 'false')
    
    def on_anonymize_changed(self, instance, value):
        """Handle anonymize exports toggle"""
        if not self.privacy_manager:
            return
            
        # Save setting
        self.privacy_manager.set_privacy_setting('anonymize_exports', 'true' if value else 'false')
    
    def on_password_text(self, instance, value):
        """Save password when changed"""
        if not self.db_manager or not value:
            return
            
        # Save backup password
        self.db_manager.set_setting('backup_password', value)
    
    def delete_old_data(self, instance):
        """Delete old data according to retention policy"""
        if not self.privacy_manager:
            self._show_message_popup("Error", "Privacy manager not initialized.")
            return
            
        # Confirm before deleting
        self._show_confirm_popup(
            "Delete Old Data",
            f"This will permanently delete data older than {int(self.retention_slider.value)} days. Continue?",
            self._confirm_delete_old_data
        )
    
    def _confirm_delete_old_data(self):
        """Confirm deleting old data"""
        deleted_count = self.privacy_manager.delete_old_data()
        
        if deleted_count > 0:
            self._show_message_popup("Data Deleted", f"{deleted_count} insights have been permanently deleted.")
        else:
            self._show_message_popup("No Data Deleted", "No old data was found to delete.")
        
        # Update data summary
        self.update_data_summary()
    
    def delete_all_data(self, instance):
        """Delete all data (factory reset)"""
        if not self.secure_manager:
            self._show_message_popup("Error", "Secure manager not initialized.")
            return
            
        # Confirm before deleting
        self._show_confirm_popup(
            "Delete All Data",
            "This will permanently delete ALL data and reset the app to factory settings. This action cannot be undone. Continue?",
            self._confirm_delete_all_data
        )
    
    def _confirm_delete_all_data(self):
        """Confirm deleting all data"""
        success = self.secure_manager.delete_all_data()
        
        if success:
            self._show_message_popup("Factory Reset Complete", 
                                   "All data has been deleted. The app will now return to the login screen.",
                                   self._go_to_login)
        else:
            self._show_message_popup("Error", "Failed to delete all data.")
    
    def _go_to_login(self):
        """Go to login screen after factory reset"""
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'login'
    
    def go_back(self, instance):
        """Return to settings screen"""
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'settings'
    
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
    
    def _show_confirm_popup(self, title, message, confirm_callback):
        """Show a confirmation popup"""
        content = BoxLayout(orientation='vertical', padding=dp(10))
        content.add_widget(Label(text=message, halign='center'))
        
        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        cancel_btn = Button(text='Cancel')
        confirm_btn = Button(text='Confirm', background_color=(0.8, 0.2, 0.2, 1))
        
        buttons.add_widget(cancel_btn)
        buttons.add_widget(confirm_btn)
        content.add_widget(buttons)
        
        popup = Popup(
            title=title,
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        confirm_btn.bind(on_press=lambda x: self._dismiss_and_callback(popup, confirm_callback))
        
        popup.open()
    
    def _dismiss_and_callback(self, popup, callback):
        """Dismiss popup and call callback"""
        popup.dismiss()
        callback()
