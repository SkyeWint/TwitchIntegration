# Twitch Integration
### For Twitch Plays, Sound Effects, Text to Speech, etc

These files are what I use to allow Twitch Chat to control my keyboard and mouse to play games, to play sound effects, and even to run text to speech. Feel free to use and/or adapt this code for your own content! You don't have to credit me, but I would appreciate it. You can also follow me at https://www.twitch.tv/skyewint if you'd like!

### Prerequisites:

To run this code, you need to install Python 3.13.0 from the [Python website](https://www.python.org/downloads/ "https://www.python.org/downloads/"). You will also need to install the following list of Python modules using [Pip](https://pip.pypa.io/en/stable/getting-started/ "https://pip.pypa.io/en/stable/getting-started/") by running these commands in the command line:

- py --version (to ensure that python is installed)  
- py -m pip --version (to ensure that pip is working)  
- py -m pip install twitchAPI
- py -m pip install keyboard  
- py -m pip install pydirectinput  
- py -m pip install pydirectinput-rgx  
- py -m pip install pyautogui  
- py -m pip install pynput  
- py -m pip install numpy  
- py -m pip install pygame  
- py -m pip install tk  
- py -m pip install gtts  
- py -m pip install pyttsx3  
- py -m pip install syllables
- py -m pip install pydub  
- py -m pip install audioop-lts  

Additionally, you will need to install ffmpeg and add it to PATH for pydub t owork. I followed [this guide](https://phoenixnap.com/kb/ffmpeg-windows) to do it myself.  

Finally, the last bit of prep you need is to go to the [Twitch developer console](https://dev.twitch.tv/console "https://dev.twitch.tv/console") and follow [these steps](https://dev.twitch.tv/docs/authentication/register-app/ "https://dev.twitch.tv/docs/authentication/register-app/") to get a few pieces of information you'll need when starting the program. If you don't know what to put in OAuth Redirect URLs, simply put in http://localhost:17563 as this is what the twitch API uses.. 

### Now you can start!

Open main.py using Python (right-click and use "open with" if you need to). 

On your first time running the code, it will ask you for information to build a config file. You will need information about your channel as well as information from your [Twitch developer console](https://dev.twitch.tv/console "https://dev.twitch.tv/console").

If you want to replace the config file for some reason, open config.py the same way or just delete the config.ini file and run the program again.

After your config file is set up, you can select the different modules you're going to use. Once they're selected, the program will inform you of the hotkeys you have available and begin listening for events from the twitch channel given in the config (your user login). For more details about specific modules, look at the start of the python files in stream_modules and audio_modules.

Have fun streaming!


#### Additional information and acknowledgements:

Massive thanks to [Tom Marks Talks Code](https://coding.tommarks.xyz/ "[Tom Marks Talks Code website](https://coding.tommarks.xyz/)") for his twitch VODs on youtube. While I am now using the python Twitch API package, I followed [this VOD](https://www.youtube.com/watch?v=ca98xkF-_aY "https://www.youtube.com/watch?v=ca98xkF-_aY - Using the Twitch EventSub/Websocket API from Python (From Scratch)") to build a functional prototype version of the Twitch API package myself. It taught me a lot about good data structuring as well as how to read APIs better, too. This was a pretty big learner project as a result!

Also massive thanks to [BiiirdPrograms](https://github.com/biiirdprograms) for a lot of debugging assistance and for writing the initial config generator to help with this.

Audio files in the repository's sound_effects folder are obtained from free sources under a creative commons 0 license, requiring no accredation or royalties. Feel free to add more of your own (if you have the rights to use them), though you'll need to update stream_sound_effects.py to make sure they can trigger!

I am **NOT** a professional programmer and this was made during my spare time. I can't guarantee that I will review pull requests or be actively developing this outside of my personal preference. Feel free to fork it if you want.