# python core modules
import os
os.environ['KIVY_GL_BACKEND'] = 'sdl2'
import sys
import random
import string
import threading
import queue
import shutil

# kivy world
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.utils import platform
from kivy.properties import StringProperty, NumericProperty, ObjectProperty

# Other public modules

# IMPORTANT: Set this property for keyboard behavior
Window.softinput_mode = "below_target"

# Import your local screen classes & modules
from screens.tts import TtsBox, UsrMsg, TtsResp
from screens.setting import SettingsBox, DemoPiperLink, DownloadPiperVoice

## OS specific imports
if platform == "android":
    from jnius import autoclass, PythonJavaClass, java_method
    MediaPlayer = autoclass('android.media.MediaPlayer')
    from piperAndroid import PiperTts
else:
    from piperApi import PiperTts

## Global definitions
__version__ = "0.3.0"
# Determine the base path for your application's resources
if getattr(sys, 'frozen', False):
    # Running as a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in a normal Python environment
    base_path = os.path.dirname(os.path.abspath(__file__))
kv_file_path = os.path.join(base_path, 'main_layout.kv')
save_path = os.path.join(base_path, 'generated')
audio_queue = queue.Queue() # audio queue
is_audio_playing = False
current_audio = None


## threaded functions outside the class
def audio_player_thread():
    '''
    This function works on desktop applications only, so it will not be used in android app.
    '''
    import pyglet
    # Initialize Pyglet player
    global is_audio_playing
    global current_audio
    player = pyglet.media.Player()
    player.loop = False
    current_source = None
    audio_duration = 0.0

    #player.on_player_eos = on_eos
    #player.push_handlers(on_eos=on_eos)

    @player.event
    def on_eos():
        print("Audio finished EOS!")

    while True:
        try:
            # Check queue for new audio file paths (non-blocking with timeout)
            message = audio_queue.get(timeout=1) # timeout in seconds
            if message == "exit":
                # Stop and exit on stop signal
                if player.playing:
                    player.pause()
                    player.delete()
                print("Audio thread stopped.")
                is_audio_playing = False
                current_audio = None
                break
            elif message == "stop":
                if player.playing:
                    player.pause()
                    player.delete()
                    player = pyglet.media.Player()
                is_audio_playing = False
                current_audio = None
            else:
                # Assume message is an audio file path
                # Stop and clear current audio if playing
                if player.playing:
                    player.pause()
                    player.delete()
                    player = pyglet.media.Player()
                    is_audio_playing = False
                    current_audio = None
                # Load and play new audio
                try:
                    full_audio_path = os.path.join(save_path, f"{message}.wav")
                    current_source = pyglet.media.load(full_audio_path, streaming=False)
                    player.queue(current_source)
                    player.play()
                    print(f"Playing: {message}.wav, duration: {player.source.duration}")
                    audio_duration = player.source.duration
                    is_audio_playing = True
                    current_audio = message
                except Exception as e:
                    print(f"Error loading audio file {message}.wav: {e}")
        except queue.Empty:
            # No new messages, update event loop
            if player.playing:
                pyglet.clock.tick()
                current_time = player.time
                # if play is over
                if current_time >= audio_duration:
                    player.pause()
                    player.delete()
                    player = pyglet.media.Player()
                    is_audio_playing = False
                    current_audio = None
                    print("Audio finished!")
        except Exception as e:
            #continue
            print(f"No new audio... {e}")

def pyjnuis_audio_player():
    '''
    This is the android media player using native java classes
    '''

    global is_audio_playing
    global current_audio
    player = MediaPlayer()
    audio_path = None
    audio_duration = 0.0

    class PythonCompletionListener(PythonJavaClass):
        __javainterfaces__ = ['android/media/MediaPlayer$OnCompletionListener']
        __javacontext__ = 'app'

        @java_method('(Landroid/media/MediaPlayer;)V')
        def onCompletion(self, mp):
            global is_audio_playing
            global current_audio
            print("Playback finished automatically")
            is_audio_playing = False
            current_audio = None
            #mp.release() # no release
    listener = PythonCompletionListener()
    player.setOnCompletionListener(listener)

    # main loop for threading
    while True:
        try:
            # Check queue for new audio file paths (non-blocking with timeout)
            message = audio_queue.get(timeout=1) # timeout in seconds
            if message == "exit":
                # Stop and exit on stop signal
                if player.isPlaying():
                    player.stop()
                player.release()
                player = None
                print("Exiting the media player thread")
                is_audio_playing = False
                current_audio = None
                break
            elif message == "stop":
                if player.isPlaying():
                    player.stop()
                    player.release()
                    player = MediaPlayer()
                    player.setOnCompletionListener(listener)
                is_audio_playing = False
                current_audio = None
                audio_duration = 0.0
            else:
                if player.isPlaying():
                    player.stop()
                player.release()
                player = MediaPlayer()
                player.setOnCompletionListener(listener)
                is_audio_playing = False
                current_audio = None
                audio_duration = 0.0
                try:
                    # try to play the audio
                    audio_path = os.path.join(save_path, f"{message}.wav")
                    print(f"Audio path: {audio_path}")
                    player.setDataSource(audio_path)
                    player.prepare()
                    duration_ms = player.getDuration()
                    audio_duration = duration_ms / 1000 # ms to sec
                    player.start()
                    print(f"Playing: {message}.wav, duration: {audio_duration:.2f}")
                    current_audio = message
                    is_audio_playing = True
                except Exception as e:
                    print(f"Error loading audio file {message}.wav: {e}")
        except queue.Empty:
            continue # continue playing or simple loop through
        except Exception as e:
            #continue
            print(f"No new audio... {e}")

# Custom kivy classes
class MainScreenBox(MDBoxLayout):
    top_pad = NumericProperty(0)
    bottom_pad = NumericProperty(0)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if platform == "android":
            try:
                from android.display_cutout import get_height_of_bar
                self.top_pad = int(get_height_of_bar('status'))
                self.bottom_pad = int(get_height_of_bar('navigation'))
            except Exception as e:
                print(f"Failed android 15 padding: {e}")
                self.top_pad = 32
                self.bottom_pad = 48

# The KivyMD app
class DlTtsSttApp(MDApp):
    title = "DasLearning TTS & STT"
    message_counter = NumericProperty(1000)
    selected_tts_model = StringProperty("")
    audio_thread = ObjectProperty(None)
    kv_play_thread = ObjectProperty(None)
    current_tts_box = ObjectProperty(None)
    previous_tts_box = ObjectProperty(None)
    tts_queue = ObjectProperty(None)
    tts_save_filename = StringProperty("")
    external_storage = ObjectProperty(None)
    txt_dialog = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Orange"

        characters = string.ascii_lowercase + string.digits
        self.new_session_id = ''.join(random.choice(characters) for _ in range(6))

        return Builder.load_file(kv_file_path)

    def on_start(self):
        global save_path
        file_m_height = 1
        settings_list = self.root.ids.settings_scroll.ids.settings_list
        support_list = self.root.ids.settings_scroll.ids.support_list
        # request write permission on Android
        if platform == "android":
            from android.permissions import request_permissions, Permission
            sdk_version = 30
            file_m_height = 0.9
            try:
                VERSION = autoclass('android.os.Build$VERSION')
                sdk_version = VERSION.SDK_INT
                print(f"Android SDK: {sdk_version}")
            except Exception as e:
                print(f"Could not check the android SDK version: {e}")
            if sdk_version >= 33:  # Android 13+
                permissions = [Permission.READ_MEDIA_AUDIO]
            elif sdk_version >= 30: # Android 11-12
                permissions = [Permission.READ_EXTERNAL_STORAGE]
            else:
                permissions = [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE]
            request_permissions(permissions)
            context = autoclass('org.kivy.android.PythonActivity').mActivity
            android_path = context.getExternalFilesDir(None).getAbsolutePath()
            self.tts_audio_dir = os.path.join(android_path, 'generated')
            self.model_path = os.path.join(android_path, 'models')
            self.config_path = os.path.join(android_path, 'config')
            self.audio_thread = threading.Thread(target=pyjnuis_audio_player, daemon=True)
        else:
            self.audio_thread = threading.Thread(target=audio_player_thread, daemon=True)
            self.tts_audio_dir = os.path.join(self.user_data_dir, 'generated')
            self.model_path = os.path.join(self.user_data_dir, 'models')
            self.config_path = os.path.join(self.user_data_dir, 'config')
            self.desktop_voice = []
            demo_voices = DemoPiperLink()
            support_list.add_widget(demo_voices)
        print(f"Application data directory: {self.user_data_dir}")
        # create the paths
        os.makedirs(self.tts_audio_dir, exist_ok=True)
        os.makedirs(self.model_path, exist_ok=True)
        os.makedirs(self.config_path, exist_ok=True)
        save_path = self.tts_audio_dir
        print(f"Generated audio will be saved in: {self.tts_audio_dir}")
        # tts file saver using filemanager
        self.manager_open = False
        self.tts_file_saver = MDFileManager(
            exit_manager=self.tts_exit_manager,
            select_path=self.select_tts_path,
            selector="folder",  # Restrict to selecting directories only
            size_hint_y = file_m_height, #0.9 for andoird cut out problem
            #pos_hint = {'center_y': 0.8}
        )
        # audio threads
        self.audio_thread.start()
        self.tts_queue = queue.Queue()
        self.kv_play_thread = threading.Thread(target=self.kv_player_thread, daemon=True)
        self.kv_play_thread.start()
        # voice models menu
        model_menu = self.root.ids.tts_screen.ids.model_menu
        self.piper = PiperTts(save_dir=self.tts_audio_dir, model_path=self.model_path)
        tts_models = self.piper.models_list()
        tts_models.sort() # list all languages in ascending order
        menu_items = [
            {
                "text": f"{model_name}",
                "leading_icon": "robot-happy",
                "on_release": lambda x=f"{model_name}": self.menu_callback(x, model_menu),
                "font_size": sp(24)
            } for model_name in tts_models
        ]
        self.menu = MDDropdownMenu(
            md_bg_color="#bdc6b0",
            caller=model_menu,
            items=menu_items,
        )
        if len(tts_models) >= 1:
            self.selected_tts_model = "select-model"
            if platform == "android":
                text_item = "en-US-language"
                set_stat = self.piper.set_model(model_name=text_item)
                if set_stat:
                    self.selected_tts_model = text_item
                    model_menu.text = self.selected_tts_model
                    self.show_toast_msg(f"Voice is set to: {text_item}, you can now generate speech.")
                else:
                    self.show_toast_msg(f"Error while setting up the voice: {text_item}, you may try with other voice model", is_error=True)
            else:
                text_item = tts_models[0]
                set_stat = self.piper.set_model(model_name=text_item)
                if set_stat:
                    self.selected_tts_model = text_item
                    model_menu.text = self.selected_tts_model
                    self.show_toast_msg(f"Voice is set to: {text_item}, you can now generate speech.")
                else:
                    self.show_toast_msg(f"Error while setting up the voice: {text_item}, you may try with other voice model", is_error=True)
        else:
            if platform == "android":
                self.selected_tts_model = "no-android-voice"
            else:
                self.selected_tts_model = "download-voice"
        model_menu.text = self.selected_tts_model
        print("Init success...")

    def kv_player_thread(self):
        # Updates the spinner
        while True:
            try:
                # Check queue for new audio file paths (non-blocking with timeout)
                message = self.tts_queue.get(timeout=1)
                if self.current_tts_box:
                    if is_audio_playing:
                        for child in self.current_tts_box.children:
                            if isinstance(child, MDSpinner):
                                child.active = True
                    else:
                        for child in self.current_tts_box.children:
                            if isinstance(child, MDSpinner):
                                child.active = False
            except queue.Empty:
                if self.current_tts_box is not None:
                    if is_audio_playing:
                        for child in self.current_tts_box.children:
                            if isinstance(child, MDSpinner):
                                child.active = True
                    else:
                        for child in self.current_tts_box.children:
                            if isinstance(child, MDSpinner):
                                child.active = False
                    if self.previous_tts_box is not None:
                        for child in self.previous_tts_box.children:
                            if isinstance(child, MDSpinner):
                                child.active = False
                elif self.previous_tts_box is not None:
                    for child in self.previous_tts_box.children:
                        if isinstance(child, MDSpinner):
                            child.active = False
            except Exception as e:
                print(f"Error: {e}")

    def menu_callback(self, text_item, model_menu):
        self.menu.dismiss()
        set_stat = self.piper.set_model(model_name=text_item)
        if set_stat:
            self.selected_tts_model = text_item
            model_menu.text = self.selected_tts_model
            self.show_toast_msg(f"Voice is set to: {text_item}, you can now generate speech.")
        else:
            self.show_toast_msg(f"Error while setting up the voice: {text_item}, you may try with other voice model", is_error=True)

    def show_toast_msg(self, message, is_error=False):
        from kivymd.uix.snackbar import MDSnackbar
        bg_color = (0.2, 0.6, 0.2, 1) if not is_error else (0.8, 0.2, 0.2, 1)
        MDSnackbar(
            MDLabel(
                text = message,
                font_style = "Subtitle1" # change size for android
            ),
            md_bg_color=bg_color,
            y=dp(64),
            pos_hint={"center_x": 0.5},
            duration=3
        ).open()

    def show_text_dialog(self, title, text="", buttons=[]):
        self.txt_dialog = MDDialog(
            title=title,
            text=text,
            buttons=buttons
        )
        self.txt_dialog.open()

    def txt_dialog_closer(self, instance):
        if self.txt_dialog:
            self.txt_dialog.dismiss()

    def play_audio(self, instance):
        parent_id = instance.parent.id
        self.previous_tts_box = self.current_tts_box
        self.current_tts_box = instance.parent
        audio_queue.put(parent_id)

    def stop_audio(self, instance):
        parent_id = instance.parent.id
        if is_audio_playing and current_audio == parent_id:
            audio_queue.put("stop")
            self.previous_tts_box = self.current_tts_box
        else:
            self.show_toast_msg(f"Not playing: {parent_id}.wav!!", True)

    def events(self, instance, keyboard, keycode, text, modifiers):
        """Handle mobile device button presses (e.g., Android back button)."""
        if keyboard in (1001, 27):  # Android back button or equivalent
            if self.manager_open:
                # Check if we are at the root of the directory tree
                if self.tts_file_saver.current_path == self.external_storage:
                    self.show_toast_msg("Closing file manager")
                    self.tts_exit_manager()
                else:
                    self.tts_file_saver.back()  # Navigate back within file manager
                return True  # Consume the event to prevent app exit
        return False

    def start_download(self, instance):
        parent_id = instance.parent.id
        file_to_downlaod = f"{parent_id}.wav"
        wav_file_path = os.path.join(save_path, file_to_downlaod)

        if not os.path.exists(wav_file_path):
            self.show_toast_msg(f"The file {file_to_downlaod} is not found!", is_error=True)
            return

        self.tts_save_filename = file_to_downlaod
        if platform == "android":
            try:
                Environment = autoclass("android.os.Environment")
                self.external_storage = Environment.getExternalStorageDirectory().getAbsolutePath()
                tts_save_path = os.path.join(self.external_storage, "Music", "TTS")
                os.makedirs(tts_save_path, exist_ok=True)
                self.tts_file_saver.show(tts_save_path)  # Open /sdcard on Android
            except Exception:
                self.tts_file_saver.show_disks()  # Fallback to showing available disks
        else:
            self.external_storage = os.path.abspath("/")
            self.tts_file_saver.show(os.path.expanduser("~"))  # Use home directory on non-Android platforms
        self.manager_open = True

    def select_tts_path(self, path: str):
        """
        Called when a directory is selected. Save the TTS wav file.
        """
        chosen_path = os.path.join(path, self.tts_save_filename) # destination path
        wav_file_path = os.path.join(save_path, self.tts_save_filename) # source path
        try:
            shutil.copyfile(wav_file_path, chosen_path)
            print(f"File successfully saved to: {chosen_path}")
            self.show_toast_msg(f"File saved to: {chosen_path}")
            self.tts_exit_manager()
        except Exception as e:
            print(f"Error saving file: {e}")
            self.show_toast_msg(f"Error saving file: {e}", is_error=True)

    def tts_exit_manager(self, *args):
        """Called when the user reaches the root of the directory tree."""
        self.manager_open = False
        self.tts_file_saver.close()

    def add_tts_msg(self, chat_history_widget, id_to_set):
        play_pause_btn = MDIconButton(
            id = f"{id_to_set}_pl",
            icon = "play-circle", #pause-circle to be added
            theme_icon_color = "Custom",
            icon_color = "black",
            icon_size = sp(24) # button size
        )
        stop_btn = MDIconButton(
            id = f"{id_to_set}_st",
            icon = "stop-circle",
            theme_icon_color = "Custom",
            icon_color = "black",
            icon_size = sp(24)
        )
        download_button = MDIconButton(
            id = f"{id_to_set}_dw",
            icon = "download",
            theme_icon_color = "Custom",
            icon_color = "black",
            icon_size = sp(24),
            pos_hint = {'right': 1}
        )
        play_pause_btn.bind(on_release=self.play_audio)
        stop_btn.bind(on_release=self.stop_audio)
        download_button.bind(on_release=self.start_download)
        tts_resp = TtsResp(id=id_to_set)
        tts_resp.add_widget(MDLabel(
            text = f"{id_to_set}.wav",
            font_style = "Caption", # change size for android
            allow_selection = True,
            allow_copy = True,
            adaptive_width = True
        ))
        tts_resp.add_widget(MDSpinner(
            size_hint = [None, None],
            size = (dp(10), dp(10)),
            active = False,
            pos_hint={'center_y': .5}
        ))
        tts_resp.add_widget(play_pause_btn)
        tts_resp.add_widget(stop_btn)
        tts_resp.add_widget(download_button)
        chat_history_widget.add_widget(tts_resp)

    def add_usr_message(self, msg_to_add, chat_history_widget):
        chat_history_widget.add_widget(UsrMsg(text=msg_to_add))

    def send_message(self, button_instance, chat_input_widget, chat_history_widget):
        if self.selected_tts_model in ["", "download-voice", "no-android-voice", "select-model"]:
            self.show_toast_msg("You need to choose a working model first!", is_error=True)
            return
        user_message = chat_input_widget.text.strip()
        #print(user_message)
        if user_message:
            # generate a msg id here
            self.message_counter += 1
            msg_id = f"{self.new_session_id}_{self.message_counter}"
            self.add_usr_message(user_message, chat_history_widget)
            chat_input_widget.text = ""
            tts_status = self.piper.transcribe(message=user_message, filename=msg_id)
            self.add_tts_msg(chat_history_widget, msg_id)
            self.show_toast_msg(tts_status)
            self.root.ids.nav_tts.badge_icon = f"numeric-{self.message_counter - 1000}"

    def show_delete_alert(self):
        wav_count = 0
        for filename in os.listdir(self.tts_audio_dir):
            if filename.endswith(".wav"):
                wav_count += 1
        self.show_text_dialog(
            title="Delete all generated Audio files?",
            text=f"There are total: {wav_count} audio files. This action cannot be undone!",
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    theme_text_color="Custom",
                    text_color=self.theme_cls.primary_color,
                    on_release=self.txt_dialog_closer
                ),
                MDFlatButton(
                    text="DELETE",
                    theme_text_color="Custom",
                    text_color="red",
                    on_release=self.delete_tts_action
                ),
            ],
        )

    def delete_tts_action(self, instance):
        # Custom function called when DISCARD is clicked
        for filename in os.listdir(self.tts_audio_dir):
            if filename.endswith(".wav"):
                file_path = os.path.join(self.tts_audio_dir, filename)
                try:
                    os.unlink(file_path)
                    print(f"Deleted {file_path}")
                except Exception as e:
                    print(f"Could not delete the audion files, error: {e}")
        self.show_toast_msg("Executed the audio cleanup!")
        self.txt_dialog_closer(instance)

    def open_link(self, instance, url):
        import webbrowser
        webbrowser.open(url)

    def update_link_open(self, instance):
        self.txt_dialog_closer(instance)
        self.open_link(instance=instance, url="https://github.com/daslearning-org/text-to-speech-offline/releases")

    def update_checker(self, instance):
        buttons = [
            MDFlatButton(
                text="Cancel",
                theme_text_color="Custom",
                text_color=self.theme_cls.primary_color,
                on_release=self.txt_dialog_closer
            ),
            MDFlatButton(
                text="Releases",
                theme_text_color="Custom",
                text_color="green",
                on_release=self.update_link_open
            ),
        ]
        self.show_text_dialog(
            "Check for update",
            f"Your version: {__version__}",
            buttons
        )

if __name__ == '__main__':
    DlTtsSttApp().run()