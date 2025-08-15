from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFillRoundFlatButton

from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.metrics import dp, sp

Builder.load_string('''

<SettingsBox@MDScrollView>: # main box
    orientation: 'vertical'
    spacing: dp(10)

    MDBoxLayout: # Settings
        id: setting_box
        orientation: 'vertical'
        adaptive_height: True
        size_hint_y: None
        height: self.minimum_height
        spacing: dp(10)
        padding: dp(10)

        MDLabel:
            text: "The app stores generated audio files in a default location. You can delete them using below button."
            size_hint_y: None
            height: self.texture_size[1] #+ dp(10)

        MDFillRoundFlatButton:
            id: delete_tts_wavs
            text: "Delete TTS Audio Files"
            font_size: sp(18)
            md_bg_color: "orange"
            theme_text_color: "Custom"
            text_color: "black"
            on_release: app.show_delete_alert()

        MDLabel:
            halign: 'left'
            size_hint_y: None
            height: self.texture_size[1] + dp(10)
            markup: True
            text: "How to use the app > [u][color=0000ff][ref=website]Youtube Demo[/ref][/color][/u]"
            on_ref_press: app.open_link(self, "https://youtu.be/AhcjJu2YwUE")

        MDLabel:
            halign: 'left'
            size_hint_y: None
            height: self.texture_size[1] + dp(10)
            markup: True
            text: "Full Documentation > [u][color=0000ff][ref=website]Click Here[/ref][/color][/u]"
            on_ref_press: app.open_link(self, "https://blog.daslearning.in/llm_ai/genai/text-to-speech-app.html")

        MDLabel:
            halign: 'left'
            size_hint_y: None
            height: self.texture_size[1] + dp(10)
            markup: True
            text: "Your app version is: [i]0.2.0[/i] > [u][color=0000ff][ref=website]Check & Download the Latest Release[/ref][/color][/u]"
            on_ref_press: app.open_link(self, "https://github.com/daslearning-org/text-to-speech-offline/releases")

''')


class SettingsBox(MDScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings_scroll"

