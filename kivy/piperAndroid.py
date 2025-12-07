from jnius import PythonJavaClass, java_method, autoclass, cast
from plyer.platforms.android import activity
import os
import sys
from threading import Event

## Global definitions
# Determine the base path for your application's resources
if getattr(sys, 'frozen', False):
    # Running as a PyInstaller bundle
    base_path = sys._MEIPASS
else:
    # Running in a normal Python environment
    base_path = os.path.dirname(os.path.abspath(__file__))
save_path = os.path.join(base_path, 'generated')
model_path = os.path.join(base_path, 'models')

Locale = autoclass('java.util.Locale')
TextToSpeech = autoclass('android.speech.tts.TextToSpeech')
TextToSpeechEngine = autoclass('android.speech.tts.TextToSpeech$Engine')
Bundle = autoclass('android.os.Bundle')
#HashMap = autoclass('java.util.HashMap')
Environment = autoclass('android.os.Environment')
File = autoclass('java.io.File')
JavaString = autoclass('java.lang.String')

class MyOnInitListener(PythonJavaClass):
    __javainterfaces__ = ['android/speech/tts/TextToSpeech$OnInitListener']
    __javacontext__ = 'app'

    def __init__(self, event_obj):
        super().__init__()
        self._event = event_obj

    @java_method('(I)V')
    def onInit(self, status):
        if status == TextToSpeech.SUCCESS:
            print("TTS engine initialized successfully.")
        else:
            print(f"TTS engine failed to initialize with status: {status}")
        self._event.set()

PyTTSListener = autoclass('in.daslearning.ttssts.PyTTSListener')
class MyTTSCallback(PythonJavaClass):
    __javainterfaces__ = ['in/daslearning/ttssts/PyTTSListener$PyTTSCallback']
    __javacontext__ = 'app'

    def __init__(self, event):
        super().__init__()
        self.event = event

    @java_method('(Ljava/lang/String;)V')
    def onStart(self, utteranceId):
        print(f"[TTS] Started: {utteranceId}")

    @java_method('(Ljava/lang/String;)V')
    def onDone(self, utteranceId):
        print(f"[TTS] Done: {utteranceId}")
        self.event.set()

    @java_method('(Ljava/lang/String;I)V')
    def onError(self, utteranceId, errorCode):
        print(f"[TTS] Error: {utteranceId}, error code: {errorCode}")
        self.event.set()

# custom class using android native TTS, kept same name as PiperTts
class PiperTts:
    def __init__(self, save_dir=save_path, model_path=model_path):
        self.save_dir = save_dir
        self.model_path = model_path
        self._init_event = Event()
        self._init_listener = MyOnInitListener(self._init_event)
        self.tts = TextToSpeech(activity, self._init_listener)
        self._init_event.wait()

    def set_model(self, model_name):
        try:
            voices = self.tts.getVoices()
            for voice in voices.toArray():
                if voice.getName() == model_name:
                    result = self.tts.setVoice(voice)
                    if result == TextToSpeech.SUCCESS:
                        print(f"Voice '{model_name}' set successfully.")
                        return True
                    else:
                        print(f"Failed to set voice '{model_name}'")
                        return False
        except Exception as e:
            self.tts.setLanguage(Locale.US)
            print(f"Failed to set voice '{model_name}' with error: {e}")
            return True

    def transcribe(self, message: str, filename: str):
        event = Event()
        callback = MyTTSCallback(event)
        pyListener = PyTTSListener()
        pyListener.setCallback(callback)
        self.tts.setOnUtteranceProgressListener(pyListener)
        full_save_path = os.path.join(self.save_dir, f"{filename}.wav")
        file_obj = File(full_save_path) # java file object where the wav will be saved

        try:
            # Convert Python str to Java String (implements CharSequence)
            java_msg = JavaString(message)
            java_utteranceId = JavaString(filename)
            # Optional params
            bundle = Bundle()
            bundle.putString(TextToSpeechEngine.KEY_PARAM_UTTERANCE_ID, filename) # filename is "unique id"
            # Synthesize to file
            result = self.tts.synthesizeToFile(java_msg, bundle, file_obj, java_utteranceId)
            if result != TextToSpeech.SUCCESS:
                return "Failed to start TTS synthesis"
        except Exception as e:
            print(f"transcribe error: {e}")
            return f"transcribe error: {e}"

        event.wait()
        return f"audio saved at: {full_save_path}" # success & wait is complete

    def models_list(self):
        all_models = []
        try:
            voices = self.tts.getVoices()
            for voice in voices.toArray():
                all_models.append(voice.getName())
                #print(f"Downloaded voice: {voice.getName()}")
                print(f"Voice: {voice.getName()}, Country: {voice.getLocale().getCountry()}, Language: {voice.getLocale().getLanguage()}, Requires network: {voice.isNetworkConnectionRequired()}")
        except Exception as e:
            print(f"Error while fetching android voices: {e}")
        return all_models
