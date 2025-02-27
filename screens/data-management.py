from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch
from kivy.metrics import dp
import os
import datetime

class DataManagementScreen(Screen):
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
            text='Data Management',
            font_size='18sp',
            bold=True,
            size_hint_x=0.8
        )
        
        header.add_widget(back_btn)
        header.add_widget(title_label)
        
        # Create sections
        export_section = self._create_section_header("Export Options")
        export_layout = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, height=dp(150))
        
        # Export all data button
        export_all_btn = Button(
            text='Export All Data',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.6, 1, 1)
        )
        export_all_btn.bind(on_press=self.export_all_data)
        
        # Export selected profile button
        self.export_profile_btn = Button(
            text='Export Selected Profile',
            size_hint_y=None,
            height=dp(50),
            background_color=(0.2, 0.7, 0.3, 1)
        )
        self.export_profile_btn.bind(on_press=self.show_profile_select)
        
        export_layout.add_widget(export_all_btn)
        export_layout.add_widget(self.export_profile_btn)
        
        import_section = self._create_section_header("Import Data")
        import_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(100))
        
        # Import button
        import_btn = Button(
            text='Import From Backup',
            size_hint_y=None,
            height=dp(50),
            background_color=(1, 0.6, 0.2, 1)
        )
        import_btn.bind(on_press=self.show_import)
        
        import_layout.add_widget(import_btn)
        
        # Option to merge or replace data
        merge_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        merge_label = Label(
            text='Merge with existing data:',
            halign='left',
            valign='center',
            size_hint_x=0.7
        )
        self.merge_switch = Switch(active=False, size_hint_x=0.3)
        
        merge_layout.add_widget(merge_label)
        merge_layout.add_widget(self.merge_switch)
        import_layout.add_widget(merge_layout)
        
        backup_section = self._create_section_header("Automatic Backups")
        backup_layout = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=None, height=dp(130))
        
        # Auto backup toggle
        auto_backup_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        auto_backup_label = Label(
            text='Auto Backup:',
            halign='left',
            valign='center',
            size_hint_x=0.7
        )
        self.auto_backup_switch = Switch(active=False, size_hint_x=0.3)
        self.auto_backup_switch.bind(active=self.on_auto_backup_changed)
        
        auto_backup_layout.add_widget(auto_backup_label)
        auto_backup_layout.add_widget(self.auto_backup_switch)
        
        # Backup frequency selection
        freq_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10))
        freq_label = Label(
            text='Backup Frequency:',
            halign='left',
            valign='center',
            size_hint_x=0.5
        )
        self.freq_btns = BoxLayout(spacing=dp(5), size_hint_x=0.5)
        
        daily_btn = Button(text='Daily')
        weekly_btn = Button(text='Weekly')
        monthly_btn = Button(text='Monthly')
        
        daily_btn.bind(on_press=lambda x: self.set_backup_frequency('daily'))
        weekly_btn.bind(on_press=lambda x: self.set_backup_frequency('weekly'))
        monthly_btn.bind(on_press=lambda x: self.set_backup_frequency('monthly'))
        
        self.freq_btns.add_widget(daily_btn)
        self.freq_btns.add_widget(weekly_btn)
        self.freq_btns.add_widget(monthly_btn)
        
        freq_layout.add_widget(freq_label)
        freq_layout.add_widget(self.freq_btns)
        
        # Create backup now button
        create_backup_btn = Button(
            text='Create Backup Now',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.3, 0.7, 0.3, 1)
        )
        create_backup_btn.bind(on_press=self.create_backup_now)
        
        backup_layout.add_widget(auto_backup_layout)
        backup_layout.add_widget(freq_layout)
        backup_layout.add_widget(create_backup_btn)
        
        # Backup history section
        history_section = self._create_section_header("Backup History")
        
        self.history_layout = GridLayout(
            cols=1, 
            spacing=dp(2), 
            size_hint_y=None,
            height=dp(150)
        )
        self.history_layout.bind(minimum_height=self.history_layout.setter('height'))
        
        # Add all sections to layout
        layout.add_widget(header)
        layout.add_widget(export_section)
        layout.add_widget(export_layout)
        layout.add_widget(import_section)
        layout.add_widget(import_layout)
        layout.add_widget(backup_section)
        layout.add_widget(backup_layout)
        layout.add_widget(history_section)
        layout.add_widget(self.history_layout)
        
        self.add_widget(layout)
    
    def initialize(self, db_manager, secure_manager, privacy_manager):
        """Initialize screen with data managers"""
        self.db_manager = db_manager
        self.secure_manager = secure_manager
        self.privacy_manager = privacy_manager
    
    def on_pre_enter(self):
        """Called before the screen is displayed"""
        self.load_settings()
        self.update_backup_history()
    
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
    
    def load_settings(self):
        """Load current settings"""
        if not self.privacy_manager:
            return
            
        # Get settings
        auto_backup = self.privacy_manager.get_privacy_setting('auto_backup', 'false') == 'true'
        backup_frequency = self.privacy_manager.get_privacy_setting('backup_frequency', 'weekly')
        
        # Update UI
        self.auto_backup_switch.active = auto_backup
        
        # Update frequency buttons
        for child in self.freq_btns.children:
            if child.text.lower() == backup_frequency:
                child.background_color = (0.2, 0.6, 1, 1)  # Highlight selected
            else:
                child.background_color = (0.9, 0.9, 0.9, 1)  # Default color
    
    def update_backup_history(self):
        """Update backup history display"""
        if not self.secure_manager:
            return
            
        # Clear existing history
        self.history_layout.clear_widgets()
        
        # Get backup info
        backup_info = self.secure_manager.get_backup_info()
        
        if backup_info['count'] == 0:
            # No backups
            self.history_layout.add_widget(Label(
                text="No backups found.",
                halign='center',
                size_hint_y=None,
                height=dp(40)
            ))
            return
        
        # Add summary
        size_str = self._format_size(backup_info['total_size'])
        summary = Label(
            text=f"Total backups: {backup_info['count']} ({size_str})",
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        summary.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
        
        self.history_layout.add_widget(summary)
        
        # Add latest backup info
        if backup_info['latest_backup']:
            latest = Label(
                text=f"Latest backup: {backup_info['latest_backup']}",
                halign='left',
                size_hint_y=None,
                height=dp(30)
            )
            latest.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
            
            self.history_layout.add_widget(latest)
        
        # Add backup directory
        directory = Label(
            text=f"Backup directory: {backup_info['backup_dir']}",
            halign='left',
            size_hint_y=None,
            height=dp(30)
        )
        directory.bind(size=lambda s, w: setattr(s, 'text_size', (w[0], None)))
        
        self.history_layout.add_widget(directory)
    
    def _format_size(self, size_bytes):
        """Format bytes to human-readable size"""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def export_all_data(self, instance):
        """Export all data"""
        if not self.secure_manager:
            self._show_message_popup("Error", "Secure manager not initialized.")
            return
            
        self._show_export_dialog(export_all=True)
    
    def show_profile_select(self, instance):
        """Show profile selection dialog for export"""
        if not self.db_manager:
            self._show_message_popup("Error", "Database manager not initialized.")
            return
            
        # Get profiles
        profiles = self.db_manager.get_profiles()
        
        if not profiles:
            self._show_message_popup("No Profiles", "No profiles found to export.")
            return
            
        # Create selection dialog
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        content.add_widget(Label(
            text="Select Profile to Export:",
            size_hint_y=None,
            height=dp(30)
        ))
        
        # Create buttons for each profile
        profiles_layout = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        profiles_layout.bind(minimum_height=profiles_layout.setter('height'))
        
        for profile in profiles:
            btn = Button(
                text=f"{profile.name} (Age {profile.age})",
                size_hint_y=None,
                height=dp(50)
            )
            btn.profile_id = profile.id
            btn.bind(on_press=lambda x: self._select_profile_for_export(x.profile_id, popup))
            profiles_layout.add_widget(btn)
        
        content.add_widget(profiles_layout)
        
        # Cancel button
        cancel_btn = Button(
            text='Cancel',
            size_hint_y=None,
            height=dp(50)
        )
        
        content.add_widget(cancel_btn)
        
        # Create popup
        popup = Popup(
            title='Select Profile',
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        
        cancel_btn.bind(on_press=popup.dismiss)
        popup.open()
    
    def _select_profile_for_export(self, profile_id, popup):
        """Handle profile selection for export"""
        popup.dismiss()
        self._show_export_dialog(export_all=False, profile_id=profile_id)
    
    def _show_export_dialog(self, export_all=True, profile_id=None):
        """Show export dialog"""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # Export file name
        name_layout = BoxLayout(size_hint_y=None, height=dp(40))
        name_label = Label(
            text="File Name:",
            size_hint_x=0.3
        )
        
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        name_input = TextInput(
            text=f"export_{timestamp}.json",
            multiline=False,
            size_hint_x=0.7
        )
        
        name_layout.add_widget(name_label)
        name_layout.add_widget(name_input)
        
        # Get encryption and anonymization settings
        encrypt = self.privacy_manager.get_privacy_setting('encrypt_backups', 'false') == 'true'
        anonymize = self.privacy_manager.get_privacy_setting('anonymize_exports', 'false') == 'true'
        
        # Encryption password
        password_layout = BoxLayout(size_hint_y=None, height=dp(40))
        password_label = Label(
            text="Password:",
            size_hint_x=0.3
        )
        
        password_input = TextInput(
            password=True,
            multiline=False,
            hint_text="Leave empty for no encryption",
            text="" if not encrypt else self.db_manager.get_setting('backup_password', ''),
            size_hint_x=0.7,
            disabled=not encrypt
        )
        
        password_layout.add_widget(password_label)
        password_layout.add_widget(password_input)
        
        # Anonymize switch
        anonymize_layout = BoxLayout(size_hint_y=None, height=dp(40))
        anonymize_label = Label(
            text="Anonymize Data:",
            size_hint_x=0.7
        )
        
        anonymize_switch = Switch(active=anonymize, size_hint_x=0.3)
        
        anonymize_layout.add_widget(anonymize_label)
        anonymize_layout.add_widget(anonymize_switch)
        
        # Buttons
        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        cancel_btn = Button(text='Cancel')
        export_btn = Button(text='Export', background_color=(0.2, 0.6, 1, 1))
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(export_btn)
        
        # Add widgets to content
        content.add_widget(name_layout)
        content.add_widget(password_layout)
        content.add_widget(anonymize_layout)
        content.add_widget(button_layout)
        
        # Create popup
        popup = Popup(
            title='Export Data',
            content=content,
            size_hint=(0.8, 0.5),
            auto_dismiss=False
        )
        
        # Bind buttons
        cancel_btn.bind(on_press=popup.dismiss)
        export_btn.bind(on_press=lambda x: self._perform_export(
            name_input.text,
            password_input.text if encrypt and password_input.text else None,
            anonymize_switch.active,
            [profile_id] if profile_id else None,
            popup
        ))
        
        popup.open()
    
    def _perform_export(self, filename, password, anonymize, profile_ids, popup):
        """Perform the actual export"""
        if not self.secure_manager:
            self._show_message_popup("Error", "Secure manager not initialized.")
            popup.dismiss()
            return
            
        try:
            # Create exports directory if it doesn't exist
            if not os.path.exists('exports'):
                os.makedirs('exports')
                
            # Full export path
            export_path = os.path.join('exports', filename)
            
            # Export data
            result = self.secure_manager.export_data(
                export_path,
                password,
                anonymize,
                profile_ids
            )
            
            popup.dismiss()
            self._show_message_popup("Export Successful", f"Data exported to:\n{export_path}")
        except Exception as e:
            popup.dismiss()
            self._show_message_popup("Export Error", f"Failed to export data: {str(e)}")
    
    def show_import(self, instance):
        """Show import dialog"""
        content = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        
        # File chooser
        content.add_widget(Label(
            text="Select Backup File:",
            size_hint_y=None,
            height=dp(30)
        ))
        
        file_chooser = FileChooserListView(
            path='exports' if os.path.exists('exports') else os.getcwd(),
            filters=['*.json']
        )
        content.add_widget(file_chooser)
        
        # Password input
        password_layout = BoxLayout(size_hint_y=None, height=dp(40))
        password_label = Label(
            text="Password:",
            size_hint_x=0.3
        )
        
        password_input = TextInput(
            password=True,
            multiline=False,
            hint_text="Leave empty if not encrypted",
            size_hint_x=0.7
        )
        
        password_layout.add_widget(password_label)
        password_layout.add_widget(password_input)
        
        # Buttons
        button_layout = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        cancel_btn = Button(text='Cancel')
        import_btn = Button(text='Import', background_color=(1, 0.6, 0.2, 1))
        
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(import_btn)
        
        # Add widgets to content
        content.add_widget(password_layout)
        content.add_widget(button_layout)
        
        # Create popup
        popup = Popup(
            title='Import Data',
            content=content,
            size_hint=(0.8, 0.8),
            auto_dismiss=False
        )
        
        # Bind buttons
        cancel_btn.bind(on_press=popup.dismiss)
        import_btn.bind(on_press=lambda x: self._perform_import(
            file_chooser.selection[0] if file_chooser.selection else None,
            password_input.text,
            popup
        ))
        
        popup.open()
    
    def _perform_import(self, filepath, password, popup):
        """Perform the actual import"""
        if not filepath:
            self._show_message_popup("No File Selected", "Please select a file to import.")
            return
            
        if not self.secure_manager:
            self._show_message_popup("Error", "Secure manager not initialized.")
            popup.dismiss()
            return
            
        try:
            # Import data
            result = self.secure_manager.import_data(
                filepath,
                password if password else None,
                self.merge_switch.active
            )
            
            popup.dismiss()
            self._show_message_popup("Import Complete", result, self._refresh_app)
        except Exception as e:
            popup.dismiss()
            self._show_message_popup("Import Error", f"Failed to import data: {str(e)}")
    
    def _refresh_app(self):
        """Refresh app after import"""
        # Go back to profile screen to reflect changes
        self.manager.current = 'profile'
    
    def on_auto_backup_changed(self, instance, value):
        """Handle auto backup toggle"""
        if not self.privacy_manager:
            return
            
        # Save setting
        self.privacy_manager.set_privacy_setting('auto_backup', 'true' if value else 'false')
    
    def set_backup_frequency(self, frequency):
        """Set backup frequency"""
        if not self.privacy_manager:
            return
            
        # Save setting
        self.privacy_manager.set_privacy_setting('backup_frequency', frequency)
        
        # Update UI
        for child in self.freq_btns.children:
            if child.text.lower() == frequency:
                child.background_color = (0.2, 0.6, 1, 1)  # Highlight selected
            else:
                child.background_color = (0.9, 0.9, 0.9, 1)  # Default color
    
    def create_backup_now(self, instance):
        """Create a backup immediately"""
        if not self.secure_manager:
            self._show_message_popup("Error", "Secure manager not initialized.")
            return
            
        try:
            result = self.secure_manager.create_scheduled_backup()
            self._show_message_popup("Backup Created", result)
            self.update_backup_history()
        except Exception as e:
            self._show_message_popup("Backup Error", f"Failed to create backup: {str(e)}")
    
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
    
    def _dismiss_and_callback(self, popup, callback):
        """Dismiss popup and call callback"""
        popup.dismiss()
        callback()
