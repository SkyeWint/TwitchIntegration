# Twitch Integration
### For Twitch Plays, Sound Effects, Text to Speech, etc

These files are what I use to allow Twitch Chat to control my keyboard and mouse to play games, to play sound effects, and even to run text to speech. Feel free to use and/or adapt this code for your own content! You don't have to credit me, but I would appreciate it. You can also follow me at https://www.twitch.tv/skyewint if you'd like!

### Prerequisites:

To run this code, you need to install Python 3.13.0 from the [Python website](https://www.python.org/downloads/ "https://www.python.org/downloads/"). You will also need to install the following list of Python modules using [Pip](https://pip.pypa.io/en/stable/getting-started/ "https://pip.pypa.io/en/stable/getting-started/") by running these commands in the command line:

- py --version (to ensure that python is installed)  
- py -m pip --version (to ensure that pip is working)  
- py -m pip install keyboard  
- py -m pip install pydirectinput  
- py -m pip install pydirectinput-rgx  
- py -m pip install pyautogui  
- py -m pip install pynput  
- py -m pip install numpy  
- py -m pip install requests  
- py -m pip install websockets  
- py -m pip install pygame  
- py -m pip install tk  
- py -m pip install gtts  
- py -m pip install pyttsx3  
- py -m pip install pydub  
- py -m pip install audioop-lts  

Additionally, you will need to install ffmpeg and add it to PATH for pydub t owork. I followed [this guide](https://phoenixnap.com/kb/ffmpeg-windows) to do it myself.  

Finally, the last bit of prep you need is to go to the [Twitch developer console](https://dev.twitch.tv/console "https://dev.twitch.tv/console") and follow [these steps](https://dev.twitch.tv/docs/authentication/register-app/ "https://dev.twitch.tv/docs/authentication/register-app/") to get a few pieces of information you'll need when starting the program. If you don't know what to put in OAuth Redirect URLs, simply put in http://localhost/. 

### Now you can start!

Open run_program.py using Python (right-click and use "open with" if you need to). 

On your first time running the code, it will build a config file with information about your channel as well as information from your [Twitch developer console](https://dev.twitch.tv/console "https://dev.twitch.tv/console"). Unless you're planning to edit the code much, just use the defaults whenever it offers them. 

If you want to replace the config file, open config.py the same way or just delete the config.ini file and run the program again.

Otherwise, have fun using the code!


#### Additional information and acknowledgements:

Massive thanks to [Tom Marks Talks Code](https://coding.tommarks.xyz/ "[Tom Marks Talks Code website](https://coding.tommarks.xyz/)") for his twitch VODs on youtube. I followed [this one](https://www.youtube.com/watch?v=ca98xkF-_aY "https://www.youtube.com/watch?v=ca98xkF-_aY - Using the Twitch EventSub/Websocket API from Python (From Scratch)") to build a very large chunk of client_server_connections. It taught me a lot about good data structuring as well as how to read APIs better, too. This was a pretty big project to learn this stuff on!

Also massive thanks to [BiiirdPrograms](https://github.com/biiirdprograms) for a lot of debugging assistance and for writing the initial config generator to help with this.

Audio files in the repository's sound_effects folder are obtained from free sources under a creative commons 0 license, requiring no accredation or royalties. Feel free to add more of your own (if you have the rights to use them), though you'll need to update stream_sound_effects.py to make sure they can trigger!

I am **NOT** a professional programmer and this was made during my spare time. I can't guarantee that I will review pull requests or be actively developing this outside of my personal preference. Feel free to fork it if you want.