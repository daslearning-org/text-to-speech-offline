# Offline TTS & STT
Offline text to speach and speach to text app which can run on `Android`, `iOS`, `Windows` & `Linux`.

### Some common troubleshootings

- Known buildozer [breaking modules](https://github.com/kivy/python-for-android/blob/develop/ci/constants.py)

- Capture buildozer logs
```bash
buildozer android debug 2>&1 | tee build_log.txt
```
