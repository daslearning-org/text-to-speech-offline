## Changes on the app

### v0.3.0
- Changing the initial voice selection method.
- Adding desktop app & dekstop voice models can be downloaded from `Piper-TTS` repo in an easy prompted manner.
- The desktop voices can be deleted as well [not yet implemented]

### v0.2.2
- Fixing the edge cut out issue on android 15
- Changing permissions for different android versions
- Using ndk:28c for 16kb page support & target api version to 35 (android 15)
- Closing the drop down menu after voice model selection

### v0.2.1
- Added Kivy Accordion in Settings for better manageability
- Replaced links with clickable IconListItem under Help & Support
- Some minor code restructure for better reusability (example: dedicated function for pop dialog)

### v0.2.0
- Added a Cleanup option to delete all generated audio files and also added relevant links into `Settings`

### v0.1.8
- Creating & Opening `TTS` folder under `Music` folder as the default Download location to avoid any unwanted permission issues. 

### v0.1.7
- Back button to parent folder (from current folder) till you reach `sdcard` in android or `root` in other OS.
- Fixes the back button not exiting from app main screen.

### v0.1.6
- Added in-app file-explorer to downlaod the audio file(s). Due to android permission restrictions, the file can only be saved into `Music` folder in phone storage. Just select the `Music` folder & click on the `Check` button at the bottom-right.

### v0.1.4
- Adding keyboard suggestion feature for text input

### v0.1.2
- Changing the app logo

### v0.1.1
- Merging Indian text fonts `Bengali`, `Gujarat`, `Kannada`, `Malayalam`, `Oriya`, `Tamil`, `Telugu` into `NotoSans` to recognize those in text input.
- Used `TextField` instead of `Label` for User messages to show multilingual fonts.

### v0.1.0
- Adding custom font `NotoSans` for huge language coverage in TextInput

### v0.0.1
- Initial version of the app
