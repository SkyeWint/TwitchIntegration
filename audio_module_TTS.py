import math
import random
import numpy
import asyncio
import string
import re
from syllables import estimate as estimate_syllables
from enum import Enum


from utils_config import get_config
from audio_module_TTS_subtitles import generate_subtitles

from twitchAPI.object.eventsub import ChannelPointsCustomRewardRedemptionAddEvent

# TTS generators
import pyttsx3


# Used for function annotation. Not required at runtime.
from utils_hotkey_manager import Hotkey_Manager
from audio_module_audio_player import Audio_Manager
from connection_http_requests import HTTP_Requests
from connection_obs_websocket import OBS_WS_Connection


######### Enum List #########


# If you want different titles for the point rewards set up by this code, specify them here.
class Reward_Titles(Enum):

    NORMAL_TTS = "Text to Speech" 


class Voice_Codes(Enum):

    PYTTS_MASCULINE = "[m]"
    PYTTS_FEMININE = "[f]"

    RANDOM = "[r]"

    ENGLISH_DAVID = "[david]"         # 0  
    GERMAN_KARSTEN = "[m]"        # 5  
    GERMAN_KATJA = "[f]"          # 7  
    ENGLISH_CATHERINE = "[f]"     # 10 
    ENGLISH_JAMES = "[m]"         # 11 
    ENGLISH_MATILDA = "[f]"       # 12 
    ENGLISH_EVA_CA = "[f]"        # 13 
    ENGLISH_SUSAN = "[f]"         # 17 
    ENGLISH_SEAN = "[m]"          # 18 
    ENGLISH_HEERA = "[f]"         # 19 
    ENGLISH_RAVI = "[ravi]"     # 20 
    ENGLISH_EVA_US = "[f]"        # 21 
    SPANISH_LAURA = "[laura]"   # 24 
    FRENCH_NATHALIE = "[f]"       # 31 
    FRENCH_GUILLAUME = "[m]"      # 32 
    FRENCH_JULIE = "[f]"          # 34 
    CROATIAN_MATEJ = "[m]"        # 39 
    ITALIAN_COSIMO = "[cosimo]" # 42 
    JAPANESE_SAYAKA = "[f]"       # 47 
    MALAY_RIZWAN = "[rizwan]"   # 49 
    ROMANIAN_ANDREI = "[m]"       # 58
    SLOVAK_FILIP = "[filip]"    # 61 
    ENGLISH_HAZEL = "[f]"         # 77 
    BULGARIAN_IVAN = "[m]"        # 78 
    ENGLISH_ZIRA = "[f]"          # 79 

ALLOWED_CHARACTER_REGEX = '[^[:alnum:][:punct:]]'



class TTS_Manager(object):
    def __init__(self, hotkey_manager:"Hotkey_Manager", audio_player:"Audio_Manager", http_requests:"HTTP_Requests", obs_ws:"OBS_WS_Connection") -> None:

        self._audio_player = audio_player
        self.http_requests = http_requests
        self._obs_ws = obs_ws

        # Base pyTTS objects, baserate is used for speech speed.
        self._pyTTS = pyttsx3.init()
        self._pyTTS_baserate = 200

        # Sets up ability to pause without closing the function.
        self._running = True
        self._paused = False
        hotkey_manager.create_hotkey("Pause playing TTS", "backspace+P", self._pause_unpause, force_assignment = True)
        hotkey_manager.create_hotkey("Stop TTS Button", "right shift+backspace", self._skip_current_TTS)

        # Used for generating files.
        self._file_path_base = ".\\tts\\"

        self._TTS_list = []
        self._TTS_parts = []
    
        # Sets up reward IDs for TTS redemptions. Additional TTS redemptions will be added later with fancier voices if desired.
        self._reward_titles = {}

        # The values in [] brackets MUST match the point rewards on your channel, whichever is changed.
        self._reward_titles.update(dict.fromkeys([Reward_Titles.NORMAL_TTS.value], "normal TTS"))




    # Gets the next TTS message from the queue and processes it while TTS is not paused.
    async def _next_TTS_message(self) -> None:
        
        # Allows concurrent functions to execute while checking for TTS messages every 3 seconds.
        while True:

            if not self._running:
                return

            if len(self._TTS_list) > 0:
                next_message = self._TTS_list.pop(0)
                break
            else:
                await asyncio.sleep(1) # Prevents loop from blocking.
                continue

        print(f'next_message = {next_message}')

        username = next_message[0]

        text = next_message[1]

        # Adjusts rate according to remaining messages in queue as well as length of message. Only for pyTTS audio.
        rate = int(math.sqrt(len(self._TTS_list) + 15) * 45) + 20
        

        self._TTS_parts = self._split_TTS_parts(text)

        TTS_path_list = await self._generate_TTS_parts(rate)

        await self._obs_ws.update_text_detail("TTS Character Label", username) #PLACEHOLDER pls fix

        await self._obs_ws.tts_character_toggle("Chat Iterator", True)

        await asyncio.sleep(0.3)


        # Plays all TTS parts in order before getting the next message to process.
        for i, TTS_Part in enumerate(TTS_path_list):

            subtitles = asyncio.create_task(
                generate_subtitles(rate, self._TTS_parts[i], self._obs_ws, self._audio_player, Voice_Codes)
            )
            
            play_TTS = asyncio.create_task(
                self._audio_player.play_TTS(TTS_Part)
            )
            
            await subtitles
            await play_TTS

            print("Stopping current subtitles.")

            subtitles.cancel()
            

        await self._obs_ws.tts_character_toggle("Chat Iterator", False)

        await asyncio.sleep(0.3)
        
        await self._obs_ws.update_text_detail("TTS Subtitles", "")



    # Generates a series of TTS files based on the list of TTS parts held by the TTS_Manager object. Returns a list of file paths to the generated TTS files.
    # TTS files are generated with an index after them in the format: [path\speech1.ext, path\speech2.ext, path\speech3.ext, etc]
    async def _generate_TTS_parts(self, pyTTS_rate:"int") -> list:
        
        TTS_path_list = []
        pytts_masc_voices = {
            "English_David": 0, 
            "German_Karsten": 5, 
            "English_James": 11, 
            "English_Sean": 18, 
            "French_Guillame": 32, 
            "Croatian_Matej": 39, 
            "Romanian_Andrei": 58, 
            "Bulgarian_Ivan": 78
        }
        pytts_fem_voices = {
            "German_Katja": 7, 
            "English_Catherine": 10, 
            "English_Matilda": 12, 
            "English_Eva_CA": 13,
            "English_Susan": 17, 
            "English_Heera": 19, 
            "English_Eva_US": 21, 
            "French_Nathalie": 31, 
            "French_Julie": 34, 
            "Japanese_Sayaka": 47, 
            "English_Hazel": 77, 
            "English_Zira": 79
        }

        #print(f"DEBUG: TTS_parts = '{self._TTS_parts}'")

        for i, tts in enumerate(self._TTS_parts):

            #print(f"DEBUG: '{tts}' <-- Message | Index--> '{str(i)}'")

            await asyncio.sleep(0.1) # Provides a period for other concurrent functions to run as needed.

            tts = tts.translate(str.maketrans('', '', '<>'))

            tts = re.sub(ALLOWED_CHARACTER_REGEX, '', tts)

            if re.sub('[^[:punct:]]', '', tts) == "":
                continue

            # Checks if a voice code exists at the start of the TTS part and maintains the full string if none are detected.
            if tts.split(maxsplit = 1)[0] not in [k.value for k in Voice_Codes]:


                # Randomly selects voice type.
                voice_type = random.randint(1, 2)
                if voice_type == 1:
                    voice = random.choice(list(pytts_masc_voices))
                    print(f'Randomly selected voice is {voice}')
                    TTS_file_path = self.generate_pyTTS(tts, voice = pytts_masc_voices.get(voice), rate = pyTTS_rate, TTS_fragment_index=i)

                elif voice_type == 2:
                    voice = random.choice(list(pytts_fem_voices))
                    print(f'Randomly selected voice is {voice}')
                    TTS_file_path = self.generate_pyTTS(tts, voice = pytts_fem_voices.get(voice), rate = pyTTS_rate, TTS_fragment_index=i)

                print(f"DEBUG: File path generated: {TTS_file_path}")

                TTS_path_list.append(TTS_file_path)

                continue
                
                

            # If a voice code does exist at the start of the string, the voice code is split and used to identify the voice to use, while the remainder of the string is passed to TTS generation.
            tts = tts.split(maxsplit = 1)

            if len(tts) < 2:
                continue


            match tts[0]:
                case Voice_Codes.PYTTS_MASCULINE.value:
                    voice = random.choice(list(pytts_masc_voices))
                    print(f'Randomly selected male voice is {voice}')
                    TTS_file_path = self.generate_pyTTS(tts[1], voice = pytts_masc_voices.get(voice), rate = pyTTS_rate, TTS_fragment_index=i)

                case Voice_Codes.PYTTS_FEMININE.value:
                    voice = random.choice(list(pytts_fem_voices))
                    print(f'Randomly selected female voice is {voice}')
                    TTS_file_path = self.generate_pyTTS(tts[1], voice = pytts_fem_voices.get(voice), rate = pyTTS_rate, TTS_fragment_index=i)

                case Voice_Codes.RANDOM.value:
                    voice_type = random.randint(1, 2)
                    if voice_type == 1:
                        voice = random.choice(list(pytts_masc_voices))
                        print(f'Randomly selected voice is {voice}')
                        TTS_file_path = self.generate_pyTTS(tts[1], voice = pytts_masc_voices.get(voice), rate = pyTTS_rate, TTS_fragment_index=i)

                    elif voice_type == 2:
                        voice = random.choice(list(pytts_fem_voices))
                        print(f'Randomly selected voice is {voice}')
                        TTS_file_path = self.generate_pyTTS(tts[1], voice = pytts_fem_voices.get(voice), rate = pyTTS_rate, TTS_fragment_index=i)

                case Voice_Codes.ENGLISH_DAVID.value:
                    TTS_file_path = self.generate_pyTTS(tts[1], voice = 0, rate = pyTTS_rate, TTS_fragment_index=i)

                case Voice_Codes.ENGLISH_RAVI.value:
                    TTS_file_path = self.generate_pyTTS(tts[1], voice = 20, rate = pyTTS_rate, TTS_fragment_index=i)

                case Voice_Codes.SPANISH_LAURA.value:
                    TTS_file_path = self.generate_pyTTS(tts[1], voice = 24, rate = pyTTS_rate, TTS_fragment_index=i)

                case Voice_Codes.ITALIAN_COSIMO.value:
                    TTS_file_path = self.generate_pyTTS(tts[1], voice = 42, rate = pyTTS_rate, TTS_fragment_index=i)

                case Voice_Codes.MALAY_RIZWAN.value:
                    TTS_file_path = self.generate_pyTTS(tts[1], voice = 49, rate = pyTTS_rate, TTS_fragment_index=i)

                case Voice_Codes.SLOVAK_FILIP.value:
                    TTS_file_path = self.generate_pyTTS(tts[1], voice = 61, rate = pyTTS_rate, TTS_fragment_index=i)

            print(f"DEBUG: File path generated: {TTS_file_path}")

            TTS_path_list.append(TTS_file_path)

        
        return TTS_path_list


    # Returns a list of TTS sections divided by voice codes in the enum Voice_Codes.
    def _split_TTS_parts(self, text:"str") -> list:
        text_words = text.split()

        text_parts = []
        text_part = ""

        for i in range(len(text_words)):

            if text_words[i] in [k.value for k in Voice_Codes]:

                # Prevents a blank initial fragment in the list. Otherwise, adds existing fragment into list if a voice code is detected.
                # The new fragment will then begin by appending the voice code as the first piece of the TTS part.
                if text_part != "":
                    text_parts.append(text_part)
                text_part = ""
            
            text_part = text_part + text_words[i] + " "
        
        text_parts.append(text_part)

        return text_parts


    # Estimates the number of syllables in a full TTS string.
    def _estimate_syllables(self, text:"str") -> int:
        syllable_count = 0
        words = text.split()

        print("DEBUG: Generating syllables.")

        for word in words:
            syllable_count += estimate_syllables(word)

        return syllable_count
    

    def _skip_current_TTS(self) -> None:
        self._TTS_parts = []
        self._audio_player.skip_TTS()


    # To be called via hotkey only. Pauses command processing and movement.
    def _pause_unpause(self) -> None:
        self._paused = not self._paused
        if self._paused:
            print("Text to speech integration is now paused.")
        elif not self._paused:
            print("Text to speech integration is now unpaused.")





    ##### Public functions


    # Generates TTS file using pyTTS voices. Voices are random by default.
    def generate_pyTTS(self, text:"str", voice:"int" = -1, rate:"int" = 200, filename:"str" = "speech", TTS_fragment_index:"int" = 1) -> str:
        file_path = self._file_path_base + filename + str(TTS_fragment_index) + ".wav"
        
        print(f"DEBUG: Text is {text}")

        pyTTS_voices = self._pyTTS.getProperty('voices')

        if voice < -1:
            voice = random.randint(0, len(pyTTS_voices) - 1)

        #print(f'DEBUG: Index of selected voice is {voice}')
        
        try:
            self._pyTTS.setProperty("voice", pyTTS_voices[voice].id)
            self._pyTTS.setProperty("rate", rate)

            self._pyTTS.save_to_file(text, file_path)
            self._pyTTS.runAndWait()
            self._pyTTS.stop()
        
        except:
            print("Illegal character detected in TTS! Skipping.")
            return None

        print(f'DEBUG: Text generated is: {text}')

        return file_path
    

    # Async handling functions & termination functions.

    async def terminate_module(self) -> None:

        # Deletes TTS reward so it is no longer redeemable.
        self.http_requests.delete_reward(reward_title = Reward_Titles.NORMAL_TTS.value)
        
        self._running = False
        self._audio_player.skip_TTS()

        print("TTS module has terminated.")
    

    async def update(self) -> None:

        # Creates TTS reward, to allow it to be redeemed while the code is active.
        try:
            self.http_requests.create_reward(Reward_Titles.NORMAL_TTS.value, user_input_required= True, background_color = "#392e5c", prompt = "Play text to speech! You can pick voices by typing a voice code before text, even in the middle of a sentence. You can see the voice codes by typing !voicecodes. For example: \"This is [m] a message.\"")

        except Exception as e:
            print("!!Attempting to create the TTS reward resulted in the following exception!!")
            print(e)

        # Resets character position.
        await self._obs_ws.tts_character_toggle("Chat Iterator", False)


        self._running = True
        while self._running:
            if not self._paused:
                print("Waiting for next TTS message")
                await self._next_TTS_message()
            else:
                # Less frequent checking occurs while paused to improve performance.
                await asyncio.sleep(5)

        

    
    
    # Receives channel point redemption event and directs it according to the matching point reward based on self._reward_titles.
    async def handle_point_reward(self, point_reward:"ChannelPointsCustomRewardRedemptionAddEvent") -> None:
        
        

        # TTS messages are only placed on the queue. update() constantly awaits the next TTS message.
        match self._reward_titles.get(point_reward.event.reward.title): 
            case "normal TTS":
                print(f"TTS redemption from {point_reward.event.user_name} with text: {point_reward.event.user_input}")
                self._TTS_list.append([point_reward.event.user_name, point_reward.event.user_input])



    async def test(self):

        test_phrase = "ooooo ooooo ooooooo ooooooo ooooo oooo ooooo oooooooooo ooooooo ooooooo oooooo oooo oooooo ooooo oooo ooooooo ooooooo ooooooooo oooo oooooooo ooooooo ooooo ooooo ooo ooooo ooooooo oooooo"
        self._TTS_list.append(["test person", test_phrase])
        await self._next_TTS_message()

        pass




##### DEBUG CODE

async def main(tts):
    
    await obs_ws.init_connection()
    await tts.test()

    pass

if __name__ == "__main__":
    hk = Hotkey_Manager()
    http = HTTP_Requests()
    obs_ws = OBS_WS_Connection(http)
    player = Audio_Manager("TTS Audio Source Test")
    tts = TTS_Manager(hk, player, http, obs_ws)

    asyncio.run(main(tts))

    