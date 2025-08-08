# Own Java Class with Interface for Pyjnius
Here ths the [java file](./MyTTSListener.java) which can be accessed from `jnuis` in kivy app like below.

## Access code
We can use below code in our kivy project.

```python
from jnius import autoclass, PythonJavaClass, java_method
from threading import Event

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

    @java_method('(Ljava/lang/String;)V')
    def onError(self, utteranceId):
        print(f"[TTS] Error: {utteranceId}")
        self.event.set()

# Use in your TTS logic
event = Event()
callback = MyTTSCallback(event)
PyTTSListener.setCallback(callback)

# Now assign the listener
listener = PyTTSListener()
tts.setOnUtteranceProgressListener(listener)

# Wait until done
event.wait()
```

## Update buildozer spec
In order to get the effective java class, we need to update our java path & class details

```ini
source.include_exts = java

# (Other settings)
# The directory in which the java files for your application are located.
android.srca = ./javaSrc # no such options

# (Other settings)
# Additional java classes to include in the build.
android.add_src = ./javaSrc

```
