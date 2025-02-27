from kivy.uix.screenmanager import Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle

from models.enums import AgeGroup, TraitCategory
from models.data_classes import UserProfile, PersonalityInsight, DevelopmentalTip

class TipsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db_manager = None
        self.secure_manager = None
        self.privacy_manager = None
        self.profile = None
        
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
            text='Development Tips',
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
        
        # Child name display
        self.child_name = Label(
            text="",
            font_size='16sp',
            size_hint_y=None,
            height=dp(30)
        )
        self.content_layout.add_widget(self.child_name)
        
        # Tips container
        self.tips_container = BoxLayout(
            orientation='vertical',
            spacing=dp(15),
            size_hint_y=None
        )
        self.tips_container.bind(minimum_height=self.tips_container.setter('height'))
        self.content_layout.add_widget(self.tips_container)
        
        # Disclaimer
        disclaimer = Label(
            text='Tips are based on observed behaviors and are meant to support development.\nThey are not clinical recommendations.',
            font_size='12sp',
            italic=True,
            color=(0.5, 0.5, 0.5, 1),
            size_hint_y=None,
            height=dp(40)
        )
        
        # Add widgets to layout
        scroll_view.add_widget(self.content_layout)
        
        layout.add_widget(header)
        layout.add_widget(scroll_view)
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
        self.title_label.text = f"Tips for {profile.name}"
        self.child_name.text = f"Development Tips for {profile.display_name}"
        self.update_content()
    
    def update_content(self):
        """Update tips based on profile insights"""
        if not self.profile:
            return
        
        # Clear existing tips
        self.tips_container.clear_widgets()
        
        # Get latest insight
        insights = self.db_manager.get_insights(
            user_id=self.profile.id,
            limit=1
        )
        
        if not insights:
            # No insights available
            self.tips_container.add_widget(Label(
                text="No insight data available yet.\nTrack behaviors to generate personalized tips.",
                halign='center'
            ))
            return
        
        latest_insight = insights[0]
        
        # Generate tips based on age group and traits
        tips = self._generate_tips(latest_insight)
        
        # Display tips
        for tip in tips:
            self._add_tip_card(tip)
    
    def _generate_tips(self, insight):
        """Generate development tips based on the insight"""
        tips = []
        
        # Determine which traits to generate tips for based on age group
        if self.profile.age_group == AgeGroup.TODDLER:
            trait_names = ["adaptability", "sensitivity", "social_engagement"]
            # Generate specific tips for toddlers
            for trait_name in trait_names:
                if trait_name in insight.traits:
                    tips.append(self._generate_toddler_tip(trait_name, insight.traits[trait_name]))
        
        elif self.profile.age_group == AgeGroup.CHILD:
            trait_names = ["planning_preference", "social_energy", "learning_style", "creativity"]
            # Generate specific tips for children
            for trait_name in trait_names:
                if trait_name in insight.traits:
                    tips.append(self._generate_child_tip(trait_name, insight.traits[trait_name]))
        
        else:  # TEEN
            trait_names = ["extraversion", "openness", "conscientiousness", 
                          "agreeableness", "emotional_stability"]
            # Generate specific tips for teens
            for trait_name in trait_names:
                if trait_name in insight.traits:
                    tips.append(self._generate_teen_tip(trait_name, insight.traits[trait_name]))
        
        return tips
    
    def _generate_toddler_tip(self, trait_name, score):
        """Generate a tip for toddlers based on trait and score"""
        tip_texts = []
        
        if trait_name == "adaptability":
            if score < 0.4:
                tip_texts = [
                    "Maintain consistent routines to provide security",
                    "Give advance notice before transitions",
                    "Use visual schedules to show what comes next"
                ]
                description = "Your child may benefit from extra support during changes and transitions."
            elif score > 0.7:
                tip_texts = [
                    "Introduce variety in daily activities",
                    "Try new environments and experiences occasionally",
                    "Celebrate flexibility when demonstrated"
                ]
                description = "Your child adapts well to change and may enjoy variety."
            else:
                tip_texts = [
                    "Balance routine with occasional new experiences",
                    "Provide gentle encouragement during transitions",
                    "Acknowledge both comfort in routines and willingness to try new things"
                ]
                description = "Your child shows balanced adaptability to new situations."
        
        elif trait_name == "sensitivity":
            if score < 0.4:
                tip_texts = [
                    "Create rich sensory experiences to explore",
                    "Gradually introduce more varied sensory input",
                    "Notice and support when sensory input becomes overwhelming"
                ]
                description = "Your child may benefit from gradually exploring more sensory experiences."
            elif score > 0.7:
                tip_texts = [
                    "Be mindful of sensory overload in busy environments",
                    "Provide calming spaces when needed",
                    "Teach simple self-regulation techniques"
                ]
                description = "Your child shows high sensitivity to sensory input."
            else:
                tip_texts = [
                    "Provide a mix of stimulating and calming activities",
                    "Observe responses to different sensory experiences",
                    "Follow your child's lead on sensory preferences"
                ]
                description = "Your child shows balanced sensitivity to sensory experiences."
        
        elif trait_name == "social_engagement":
            if score < 0.4:
                tip_texts = [
                    "Arrange short, low-pressure playdates",
                    "Model social interaction with puppets or toys",
                    "Respect need for alone time while gradually building social skills"
                ]
                description = "Your child may prefer solo play or smaller social settings."
            elif score > 0.7:
                tip_texts = [
                    "Provide plenty of social opportunities",
                    "Teach taking turns and reading others' cues",
                    "Balance social time with quiet activities"
                ]
                description = "Your child thrives on social interaction and enjoys group activities."
            else:
                tip_texts = [
                    "Mix individual and group activities",
                    "Notice when your child seeks connection vs. alone time",
                    "Support both independent play and social skills"
                ]
                description = "Your child shows a balanced approach to social engagement."
        
        # Determine color based on score
        if score > 0.7:
            color = [0.0, 0.7, 0.3, 1.0]  # Green
        elif score > 0.4:
            color = [0.0, 0.5, 0.8, 1.0]  # Blue
        else:
            color = [0.8, 0.3, 0.3, 1.0]  # Red
            
        return DevelopmentalTip(
            trait_name=trait_name.replace('_', ' ').title(),
            score=score,
            description=description,
            tips=tip_texts,
            color=color
        )
    
    def _generate_child_tip(self, trait_name, score):
        """Generate a tip for children based on trait and score"""
        tip_texts = []
        
        if trait_name == "planning_preference":
            if score < 0.4:
                tip_texts = [
                    "Provide visual checklists for multi-step tasks",
                    "Break large projects into smaller steps",
                    "Use timers to help with transitions"
                ]
                description = "Your child may benefit from structure and planning support."
            elif score > 0.7:
                tip_texts = [
                    "Encourage flexibility when plans change",
                    "Balance structure with spontaneity",
                    "Teach prioritization of tasks"
                ]
                description = "Your child enjoys planning and organization."
            else:
                tip_texts = [
                    "Provide moderate structure with room for flexibility",
                    "Validate both planning and spontaneity",
                    "Teach both organization and adaptability"
                ]
                description = "Your child shows a balanced approach to planning."
        
        elif trait_name == "social_energy":
            if score < 0.4:
                tip_texts = [
                    "Respect need for alone time to recharge",
                    "Teach conversation starters for social situations",
                    "Build social skills through interests and small groups"
                ]
                description = "Your child may prefer quieter, less socially demanding activities."
            elif score > 0.7:
                tip_texts = [
                    "Provide plenty of social opportunities",
                    "Teach listening skills and turn-taking",
                    "Help recognize when others need space"
                ]
                description = "Your child is energized by social interaction."
            else:
                tip_texts = [
                    "Balance group and individual activities",
                    "Discuss social preferences and boundaries",
                    "Celebrate both social skills and independent interests"
                ]
                description = "Your child shows a balanced approach to social energy."
        
        elif trait_name == "learning_style":
            if score < 0.4:
                tip_texts = [
                    "Provide concrete examples and hands-on activities",
                    "Connect abstract concepts to real-world applications",
                    "Use visual aids and demonstrations"
                ]
                description = "Your child may prefer concrete, practical learning approaches."
            elif score > 0.7:
                tip_texts = [
                    "Encourage exploration of theoretical concepts",
                    "Ask open-ended questions that promote abstract thinking",
                    "Connect ideas across different subjects"
                ]
                description = "Your child enjoys abstract and theoretical thinking."
            else:
                tip_texts = [
                    "Provide both hands-on and theoretical learning",
                    "Connect concrete examples to broader concepts",
                    "Explore different ways of understanding ideas"
                ]
                description = "Your child shows a balanced learning approach."
        
        elif trait_name == "creativity":
            if score < 0.4:
                tip_texts = [
                    "Provide open-ended art materials without specific outcomes",
                    "Ask 'what if' questions to spark imagination",
                    "Celebrate all creative attempts"
                ]
                description = "Your child may benefit from encouragement in creative expression."
            elif score > 0.7:
                tip_texts = [
                    "Provide diverse creative materials and outlets",
                    "Teach skills to bring creative ideas to fruition",
                    "Balance creative freedom with completing projects"
                ]
                description = "Your child shows strong creative tendencies and imagination."
            else:
                tip_texts = [
                    "Offer both structured and open-ended creative activities",
                    "Validate both practical and imaginative approaches",
                    "Connect creativity to problem-solving in daily life"
                ]
                description = "Your child shows a balanced approach to creativity."
        
        # Determine color based on score
        if score > 0.7:
            color = [0.0, 0.7, 0.3, 1.0]  # Green
        elif score > 0.4:
            color = [0.0, 0.5, 0.8, 1.0]  # Blue
        else:
            color = [0.8, 0.3, 0.3, 1.0]  # Red
            
        return DevelopmentalTip(
            trait_name=trait_name.replace('_', ' ').title(),
            score=score,
            description=description,
            tips=tip_texts,
            color=color
        )
    
    def _generate_teen_tip(self, trait_name, score):
        """Generate a tip for teens based on trait and score"""
        tip_texts = []
        
        if trait_name == "extraversion":
            if score < 0.4:
                tip_texts = [
                    "Value quiet reflection and solo interests",
                    "Build social skills in low-pressure settings",
                    "Find balance between social time and recharge time"
                ]
                description = "Your teen may prefer deeper connections and quieter environments."
            elif score > 0.7:
                tip_texts = [
                    "Provide plenty of social opportunities",
                    "Develop active listening skills to balance talking and hearing",
                    "Respect others who may need more personal space"
                ]
                description = "Your teen is energized by social interaction and group activities."
            else:
                tip_texts = [
                    "Support both social engagement and independent activities",
                    "Discuss how to recognize personal energy levels",
                    "Value both outgoing and reflective qualities"
                ]
                description = "Your teen shows a balanced approach to social energy."
        
        elif trait_name == "openness":
            if score < 0.4:
                tip_texts = [
                    "Gradually introduce new experiences in areas of interest",
                    "Connect new ideas to established interests",
                    "Respect preference for the familiar while expanding horizons"
                ]
                description = "Your teen may prefer established routines and familiar ideas."
            elif score > 0.7:
                tip_texts = [
                    "Provide access to diverse books, art, music, and experiences",
                    "Engage in discussions about different perspectives",
                    "Balance exploration with completing projects"
                ]
                description = "Your teen shows strong curiosity and openness to new experiences."
            else:
                tip_texts = [
                    "Encourage thoughtful consideration of both new and established ideas",
                    "Support both creative exploration and practical application",
                    "Value both innovation and tradition"
                ]
                description = "Your teen shows a balanced approach to new experiences."
        
        elif trait_name == "conscientiousness":
            if score < 0.4:
                tip_texts = [
                    "Break large tasks into small, manageable steps",
                    "Use visual planners and checklists",
                    "Celebrate small organizational wins"
                ]
                description = "Your teen may benefit from support with organization and planning."
            elif score > 0.7:
                tip_texts = [
                    "Encourage healthy balance between productivity and relaxation",
                    "Develop flexibility when plans change",
                    "Value the process as much as the outcome"
                ]
                description = "Your teen shows strong organizational and planning skills."
            else:
                tip_texts = [
                    "Support both spontaneity and planning",
                    "Discuss how different situations benefit from different approaches",
                    "Value both creative process and structured completion"
                ]
                description = "Your teen shows a balanced approach to organization."
        
        elif trait_name == "agreeableness":
            if score < 0.4:
                tip_texts = [
                    "Value analytical thinking while building empathy",
                    "Practice perspective-taking exercises",
                    "Find balance between assertiveness and cooperation"
                ]
                description = "Your teen may approach situations with a logical, analytical lens."
            elif score > 0.7:
                tip_texts = [
                    "Develop healthy boundaries while maintaining empathy",
                    "Practice assertiveness in appropriate situations",
                    "Balance others' needs with personal needs"
                ]
                description = "Your teen shows strong empathy and cooperative tendencies."
            else:
                tip_texts = [
                    "Value both logical analysis and emotional understanding",
                    "Discuss when cooperation or assertiveness is most effective",
                    "Appreciate the balance of head and heart in decision-making"
                ]
                description = "Your teen shows a balanced approach to interpersonal dynamics."
        
        elif trait_name == "emotional_stability":
            if score < 0.4:
                tip_texts = [
                    "Develop mindfulness and relaxation techniques",
                    "Identify and name emotions when they arise",
                    "Create stress management strategies for challenging situations"
                ]
                description = "Your teen may benefit from emotional regulation support."
            elif score > 0.7:
                tip_texts = [
                    "Validate all emotions as normal and healthy",
                    "Develop emotional vocabulary beyond 'fine'",
                    "Balance emotional steadiness with appropriate expression"
                ]
                description = "Your teen shows strong emotional regulation and resilience."
            else:
                tip_texts = [
                    "Continue developing emotional awareness and vocabulary",
                    "Practice both expression and regulation of feelings",
                    "Value emotional sensitivity while building resilience"
                ]
                description = "Your teen shows a balanced approach to emotional regulation."
        
        # Determine color based on score
        if score > 0.7:
            color = [0.0, 0.7, 0.3, 1.0]  # Green
        elif score > 0.4:
            color = [0.0, 0.5, 0.8, 1.0]  # Blue
        else:
            color = [0.8, 0.3, 0.3, 1.0]  # Red
            
        return DevelopmentalTip(
            trait_name=trait_name.replace('_', ' ').title(),
            score=score,
            description=description,
            tips=tip_texts,
            color=color
        )
    
    def _add_tip_card(self, tip):
        """Add a tip card to the tips container"""
        # Create a card layout
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=dp(170),
            padding=dp(15),
            spacing=dp(5)
        )
        
        # Add background color with rounded corners
        with card.canvas.before:
            Color(*tip.color, 0.2)  # Light version of the color
            self.rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[10])
            card.bind(pos=self._update_rect, size=self._update_rect)
        
        # Add header (trait name and score)
        header = BoxLayout(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(30)
        )
        
        name_label = Label(
            text=tip.trait_name,
            font_size='16sp',
            bold=True,
            halign='left',
            valign='middle',
            size_hint_x=0.7,
            color=tip.color
        )
        
        score_label = Label(
            text=f"{tip.score:.0%}",
            font_size='16sp',
            bold=True,
            halign='right',
            valign='middle',
            size_hint_x=0.3,
            color=tip.color
        )
        
        header.add_widget(name_label)
        header.add_widget(score_label)
        card.add_widget(header)
        
        # Add description
        desc_label = Label(
            text=tip.description,
            font_size='14sp',
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(40),
            text_size=(self.width - dp(40), None)
        )
        card.add_widget(desc_label)
        
        # Add tips
        tip_layout = GridLayout(
            cols=1,
            spacing=dp(2),
            size_hint_y=None,
            height=dp(80)
        )
        
        for tip_text in tip.tips:
            tip_label = Label(
                text=f"• {tip_text}",
                font_size='12sp',
                halign='left',
                valign='top',
                size_hint_y=None,
                height=dp(25),
                text_size=(self.width - dp(40), None)
            )
            tip_layout.add_widget(tip_label)
        
        card.add_widget(tip_layout)
        
        # Add to container
        self.tips_container.add_widget(card)
    
    def _update_rect(self, instance, value):
        """Update rectangle position and size for background drawing"""
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    
    def go_back(self, instance):
        """Return to profile screen"""
        self.manager.transition = SlideTransition(direction='right')
        self.manager.current = 'profile'
