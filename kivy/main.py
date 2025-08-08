# python core modules
import os
os.environ['KIVY_GL_BACKEND'] = 'sdl2'
import sys
import random
import string
import threading
import queue

# kivy world
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.spinner import MDSpinner
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.utils import platform
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from plyer import filechooser

# Other public modules

# IMPORTANT: Set this property for keyboard behavior
Window.softinput_mode = "below_target"

# Import your local screen classes & modules
from screens.tts import TtsBox, UsrMsg, TtsResp
if platform == "android":
    from jnius import autoclass, PythonJavaClass, java_method
    from plyer.platforms.android import activity
    MediaPlayer = autoclass('android.media.MediaPlayer')
    from piperAndroid import PiperTts
else:
    from piperApi import PiperTts

## Global definitions
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

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Orange"

        characters = string.ascii_lowercase + string.digits
        self.new_session_id = ''.join(random.choice(characters) for _ in range(6))

        return Builder.load_file(kv_file_path)

    def on_start(self):
        #print(self.root.ids)
        global save_path
        # request write permission on Android
        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])
            context = autoclass('org.kivy.android.PythonActivity').mActivity
            android_path = context.getExternalFilesDir(None).getAbsolutePath()
            self.tts_audio_dir = os.path.join(android_path, 'generated')
            self.audio_thread = threading.Thread(target=pyjnuis_audio_player, daemon=True)
        else:
            self.audio_thread = threading.Thread(target=audio_player_thread, daemon=True)
            self.tts_audio_dir = os.path.join(self.user_data_dir, 'generated')
        print(f"Application data directory: {self.user_data_dir}")
        # create the paths
        os.makedirs(self.tts_audio_dir, exist_ok=True)
        save_path = self.tts_audio_dir
        print(f"Generated audio will be saved in: {self.tts_audio_dir}")
        self.audio_thread.start()
        self.tts_queue = queue.Queue()
        self.kv_play_thread = threading.Thread(target=self.kv_player_thread, daemon=True)
        self.kv_play_thread.start()
        model_menu = self.root.ids.tts_screen.ids.model_menu
        self.piper = PiperTts(save_dir=self.tts_audio_dir)
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
            self.selected_tts_model = tts_models[0]
        else:
            self.selected_tts_model = "no-android-voice"
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
        self.selected_tts_model = text_item
        self.piper = PiperTts(save_dir=self.tts_audio_dir, model_name=self.selected_tts_model)
        model_menu.text = self.selected_tts_model

    def show_toast_msg(self, message, is_error=False):
        from kivymd.uix.snackbar import MDSnackbar
        bg_color = (0.2, 0.6, 0.2, 1) if not is_error else (0.8, 0.2, 0.2, 1)
        MDSnackbar(
            MDLabel(
                text = message,
                font_style = "Subtitle1" # change size for android
            ),
            md_bg_color=bg_color,
            y=dp(24),
            pos_hint={"center_x": 0.5},
            duration=3
        ).open()

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

    def start_download(self, instance):
        parent_id = instance.parent.id
        file_to_downlaod = f"{parent_id}.wav"
        wav_file_path = os.path.join(save_path, file_to_downlaod)

        if not os.path.exists(wav_file_path):
            self.show_toast_msg(f"The file {file_to_downlaod} is not found!", is_error=True)
            return

        file_content = ""
        try:
            with open(wav_file_path, 'rb') as f:
                file_content = f.read()
            print(f"Read content from: {wav_file_path}")
        except FileNotFoundError:
            print(f"Error: The file '{file_to_downlaod}' was not found at '{wav_file_path}'")
            self.show_toast_msg(f"Error: Original file '{file_to_downlaod}' not found.", is_error=True)
            return
        except Exception as e:
            print(f"Error reading existing file: {e}")
            self.show_toast_msg(f"Error reading original file: {e}", is_error=True)
            return
        self.default_save_filename = file_to_downlaod
        filechooser.save_file(
            title=f"Save {self.default_save_filename} As",
            path=self.tts_audio_dir,
            filters=[("Audio files", "*.wav"), ("All files", "*.*")],
            # We don't pass 'filename' here. We'll handle it in the callback.
            on_selection=lambda selection: self.save_file_callback(selection, file_content)
        )

    def save_file_callback(self, selection, file_content):
        if selection:
            #print(selection)
            # `selection` will contain the chosen directory path, potentially without the filename
            chosen_path_or_dir = selection[0]

            if os.path.isdir(chosen_path_or_dir):
                chosen_path = os.path.join(chosen_path_or_dir, self.default_save_filename)
            else:
                # If a full path with a filename was already chosen (e.g., user typed one)
                chosen_path = chosen_path_or_dir
                # Ensure the chosen path has an extension if it's missing and we expect one
                if '.' not in os.path.basename(chosen_path) and '.' in self.default_save_filename:
                    chosen_path += os.path.splitext(self.default_save_filename)[1] # Add the original extension

            try:
                with open(chosen_path, 'wb') as f:
                    f.write(file_content)
                print(f"File successfully saved to: {chosen_path}")
                self.show_toast_msg(f"File saved to: {chosen_path}")
            except Exception as e:
                print(f"Error saving file: {e}")
                self.show_toast_msg(f"Error saving file: {e}", is_error=True)
        else:
            print("File save cancelled.")
            self.show_toast_msg("File save cancelled.")

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
            font_style = "Caption" # change size for android
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
        user_message = chat_input_widget.text.strip()
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

if __name__ == '__main__':
    DlTtsSttApp().run()