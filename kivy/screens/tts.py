# screens/tts.py
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dropdownitem import MDDropDownItem
from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.metrics import dp, sp

Builder.load_string('''
#:import parse_color kivy.parser.parse_color
#<UsrMsg>:
#    size_hint_y: None
#    size_hint_x: 0.7
#    height: self.texture_size[1] + dp(20)
#    padding: 10, 10
#    font_size: sp(14)
#    font_name: 'data/fonts/NotoSans-Merge-BM.ttf'
#    text_size: self.width - 20, None
#    color: (0, 0, 0, 1)
#    allow_selection: True
#    allow_copy: True
#    halign: "left"
#    pos_hint: {'right': 1}
#    canvas.before:
#        Color:
#            rgb: parse_color('#fad2ed')
#        RoundedRectangle:
#            size: self.width, self.height
#            pos: self.pos
#            radius: [20, 20, 0, 20] # [top_left, top_right, bottom_right, bottom_left]

<UsrMsg>:
    mode: "fill"
    readonly: True
    font_name: 'data/fonts/NotoSans-Merged.ttf'
    multiline: True
    max_height: "200dp"
    size_hint_x: 0.7
    font_size: sp(18)
    pos_hint: {'right': 1}
    text_color_normal: (0, 0, 0, 1)
    text_color_focus: (0, 0, 0, 1)
    fill_color_normal: '#fad2ed'
    fill_color_focus: '#fad2ed'
    radius: [20, 20, 0, 20]

<TtsResp>
    orientation: 'horizontal'
    size_hint_y: None
    size_hint_x: 0.9
    pos_hint: {"x": 0}
    height: self.minimum_height + dp(10)
    padding: 4, 2
    spacing: dp(2)
    canvas.before:
        Color:
            rgb: parse_color('#affae5')
        RoundedRectangle:
            size: self.width, self.height
            pos: self.pos
            radius: [20, 20, 20, 0]

<MultiLingualTextField>:
    hint_text: "Type your text..."
    mode: "rectangle"
    font_name: 'data/fonts/NotoSans-Merged.ttf'
    multiline: True
    max_height: "200dp"
    size_hint_x: 0.8
    font_size: sp(18)

<TtsBox@MDBoxLayout>: # main box
    orientation: 'vertical'
    padding: dp(4)
    spacing: dp(10)

    MDBoxLayout: # top button group
        id: top_menu
        orientation: 'horizontal'
        adaptive_height: True
        #size_hint_y: 0.1
        spacing: dp(10)

        MDDropDownItem:
            md_bg_color: "#bdc6b0"
            #pos_hint: {"center_x": .5, "center_y": .7}
            on_release: app.menu.open()
            text: "Choose Model"
            id: model_menu
            font_size: sp(14)

    MDScrollView: # chat history section with scroll enabled
        size_hint_y: 0.7 # Takes the 70%
        adaptive_height: True
        id: chat_box

        MDBoxLayout:
            id: chat_history_id
            orientation: 'vertical'
            padding: dp(10)
            spacing: dp(10)
            size_hint_y: None
            height: self.minimum_height

            #ChildElement:
            # add the child elements

    MDBoxLayout: # Input box
        size_hint_y: 0.2
        orientation: 'horizontal'
        spacing: dp(5)
        adaptive_height: True
        id: input_box

        MultiLingualTextField:
            id: chat_input
            #hint_text: "Type your text..."
            #mode: "rectangle"
            #multiline: True
            #max_height: "200dp"
            #size_hint_x: 0.8
            #font_size: sp(18)
        MDFillRoundFlatButton:
            id: send_msg_button
            text: "Send"
            size_hint_x: 0.2
            size_hint_y: 1
            font_size: sp(18)
            on_release: app.send_message(self, chat_input, chat_history_id)
''')

class TtsResp(MDBoxLayout):
    id = StringProperty("")

class MultiLingualTextField(MDTextField):
    pass

class UsrMsg(MDTextField): # originally MDLabel
    id = StringProperty("")
    text = StringProperty("")
    #font_style = "Subtitle1"

class TtsBox(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "tts_main_box"
