from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDList, OneLineIconListItem, IconLeftWidget, IconRightWidget

from kivy.uix.accordion import Accordion, AccordionItem
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.metrics import dp, sp
from kivy.parser import parse_color

# local imports

Builder.load_string('''

<DownloadPiperVoice>:
    text: "Download voices"
    on_release: app.open_link(self, "https://youtu.be/AhcjJu2YwUE")
    IconLeftWidget:
        icon: "download"

<DemoPiperLink>:
    text: "Check the demo voices"
    on_release: app.open_link(self, "https://rhasspy.github.io/piper-samples/")
    IconLeftWidget:
        icon: "music"

<SettingsBox@MDBoxLayout>:

    Accordion:
        orientation: 'vertical'

        AccordionItem:
            title: "Settings"
            spacing: dp(8)
            canvas.before:
                Color:
                    rgba: parse_color('#a8b7bf')
                RoundedRectangle:
                    size: self.width, self.height
                    pos: self.pos

            MDScrollView:
                MDList:
                    id: settings_list
                    OneLineIconListItem:
                        text: "Delete old audio files(s)"
                        on_release: app.show_delete_alert()
                        IconLeftWidget:
                            icon: "broom"

        AccordionItem:
            title: "Help & Support"
            spacing: dp(8)
            canvas.before:
                Color:
                    rgba: parse_color('#aabfb8')
                RoundedRectangle:
                    size: self.width, self.height
                    pos: self.pos

            MDScrollView:
                MDList:
                    id: support_list
                    OneLineIconListItem:
                        text: "Demo (How to use)"
                        on_release: app.open_link(self, "https://youtu.be/AhcjJu2YwUE")
                        IconLeftWidget:
                            icon: "youtube"
                    OneLineIconListItem:
                        text: "Documentation (Blog)"
                        on_release: app.open_link(self, "https://blog.daslearning.in/llm_ai/genai/text-to-speech-app.html")
                        IconLeftWidget:
                            icon: "file-document-check"
                    OneLineIconListItem:
                        text: "Contact Developer"
                        on_release: app.open_link(self, "https://daslearning.in/contact/")
                        IconLeftWidget:
                            icon: "card-account-phone"
                    OneLineIconListItem:
                        text: "Check for update"
                        on_release: app.update_checker(self)
                        IconLeftWidget:
                            icon: "github"

''')

class SettingsBox(MDBoxLayout):
    """ The main settings box which contains the setting, help & other required sections """

class DownloadPiperVoice(OneLineIconListItem):
    """ Download the Piper-TTS voices for Desktop only """

class DemoPiperLink(OneLineIconListItem):
    """ Check demo Piper-TTS voices for Desktop only """
