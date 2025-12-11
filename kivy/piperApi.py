from piper.voice import PiperVoice
from kivy.clock import Clock
import os
import sys
import wave

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

class PiperTts:
    def __init__(self, save_dir=save_path, model_path=model_path):
        self.default_model = "en_US-lessac-medium"
        self.save_dir = save_dir
        self.model_path = model_path

    def set_model(self, model_name):
        model_onnx = os.path.join(self.model_path, f"{model_name}.onnx")
        model_json = os.path.join(self.model_path, f"{model_name}.onnx.json")
        try:
            self.voice = PiperVoice.load(model_onnx, config_path=model_json)
            return True
        except Exception as e:
            print(f"Error loading piper model: {e}")
            return False

    def transcribe(self, message: str, filename: str, callback=None):
        status = False
        full_save_path = os.path.join(self.save_dir, f"{filename}.wav")
        with wave.open(full_save_path, 'wb') as file:
            file.setnchannels(1)
            file.setsampwidth(2) # For 16-bit PCM
            file.setframerate(self.voice.config.sample_rate)
            try:
                self.voice.synthesize_wav(message, file)
                status = True
            except Exception as e:
                print(f"Error during transcribe: {e}")
        if callback:
            Clock.schedule_once(lambda dt: callback(status))
        else:
            return status

    def models_list(self):
        all_models = []
        try:
            for filename in os.listdir(self.model_path):
                if filename.endswith(".onnx"):
                    only_filename = filename.split('.')[0]
                    all_models.append(only_filename)
        except Exception as e:
            print(f"An error occurred while reading directory '{self.model_path}': {e}")
        return all_models

