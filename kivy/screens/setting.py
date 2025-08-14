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
    padding: dp(4)
    spacing: dp(10)

    MDBoxLayout: # Settings
        id: setting_box
        orientation: 'vertical'
        #adaptive_height: True
        size_hint_y: None
        height: self.minimum_height
        padding: 10, 10
        spacing: dp(4)
        padding: dp(10)

        MDLabel:
            text: "The app stores generated audio files in a default location. You can delete them using below button."
            size_hint_y: None
            height: self.texture_size[1] + dp(10)

        MDFillRoundFlatButton:
            id: delete_tts_wavs
            text: "Delete TTS Audio Files"
            font_size: sp(18)
            md_bg_color: "orange"
            theme_text_color: "Custom"
            text_color: "white"
            on_release: app.show_delete_alert()


''')


class SettingsBox(MDScrollView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "settings_scroll"

