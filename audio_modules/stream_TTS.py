import math
import random
import queue
import asyncio
from syllables import estimate as estimate_syllables
from enum import Enum

from utils.config import get_config

# TTS generators
from gtts import gTTS
import pyttsx3

# Used for function annotation. Not required at runtime.
from utils.hotkey_manager import Hotkey_Manager
from utils.message_parsing import SubscriptionMessage
from audio_modules.audio_player import Audio_Manager


######### Enum List #########


class Reward_Titles(Enum):

    NORMAL_TTS = get_config("STREAM INFO").get("tts_reward_title")



class Voice_Codes(Enum):

    PYTTS_MALE = "[m]"
    PYTTS_FEMALE = "[f]"
    GTTS = "[g]"
    RANDOM = "[r]"



class TTS_Manager(object):
    def __init__(self, hotkey_manager:"Hotkey_Manager", audio_player:"Audio_Manager") -> None:

        self._audio_player = audio_player

        # Base pyTTS objects, baserate is used for speech speed.
        self._pyTTS = pyttsx3.init()
        self._pyTTS_baserate = 200

        # Sets up ability to pause without closing the function.
        self._paused = False
        hotkey_manager.create_hotkey("Pause playing TTS", "backspace+P", self._pause_unpause, force_assignment = True)
        hotkey_manager.create_hotkey("Stop TTS Button", "right shift+backspace", self._skip_current_TTS)

        # Used for generating files.
        self._file_path_base = ".\\audio_modules\\sound_effects\\"

        self._TTS_queue = queue.Queue(0)
        self._TTS_parts = []
    
        # Sets up reward IDs for TTS redemptions. Additional TTS redemptions will be added later with fancier voices if desired.
        self._reward_titles = {}

        # The values in [] brackets MUST match the point rewards on your channel, whichever is changed.
        self._reward_titles.update(dict.fromkeys([Reward_Titles.NORMAL_TTS.value], "normal TTS"))


    # Args for this function are generic and can be used according to the specific rewards being used.
    async def _handle_point_reward(self, user:"str", reward:"str", text:"str") -> None:
        

        # TTS messages are only placed on the queue. update() constantly awaits the next TTS message.
        match self._reward_titles.get(reward): 
            case "normal TTS":
                print(f"TTS redemption: {text}")
                self._TTS_queue.put(text)


    # Gets the next TTS message from the queue and processes it while TTS is not paused.
    async def _next_TTS_message(self) -> None:
        
        # Allows concurrent functions to execute while checking for TTS messages every second.
        while True:
            try:
                text = self._TTS_queue.get(timeout = 0.02)
            except queue.Empty:
                if not self._running:
                    print("No longer listening to TTS message.")
                    return
                await asyncio.sleep(1)
            else:
                print(f"TTS message detected: {text}")
                break

        # Adjusts rate according to remaining messages in queue as well as length of message. Only for pyTTS audio.
        rate = int(math.sqrt(self._TTS_queue.qsize() + 15) * 45)
        rate += int(self._estimate_syllables(text) * 0.5)

        self._TTS_parts = self._split_TTS_parts(text)

        TTS_path_list = await self._generate_TTS_parts(rate)

        # Plays all TTS parts in order before getting the next message to process.
        for TTS_Part in TTS_path_list:
            await self._audio_player.play_TTS(TTS_Part)


    # Generates a series of TTS files based on the list of TTS parts held by the TTS_Manager object. Returns a list of file paths to the generated TTS files.
    # TTS files are generated with an index after them in the format: [path\speech1.ext, path\speech2.ext, path\speech3.ext, etc]
    async def _generate_TTS_parts(self, pyTTS_rate:"int") -> list:
        
        TTS_path_list = []

        for i, TTS in enumerate(self._TTS_parts):

            #print(f"DEBUG: {TTS} <-- Message | Index--> {str(i)}")

            await asyncio.sleep(0.1) # Provides a period for other concurrent functions to run as needed.

            # Checks if a voice code exists at the start of the TTS part and maintains the full string if none are detected.
            if TTS.split(maxsplit = 1)[0] not in [k.value for k in Voice_Codes]:

                # Randomly selects voice type.
                voice_type = random.randint(0,len(Voice_Codes)-2)
                if voice_type in [0,1]:
                    TTS_file_path = self.generate_pyTTS(TTS, voice = voice_type, rate = pyTTS_rate, TTS_fragment_index=i)
                elif voice_type == 2:
                    TTS_file_path = self.generate_gTTS(TTS, TTS_fragment_index=i)
                TTS_path_list.append(TTS_file_path)
                continue
                


            # If a voice code does exist at the start of the string, the voice code is split and used to identify the voice to use, while the remainder of the string is passed to TTS generation.
            TTS = TTS.split(maxsplit = 1)

            match TTS[0]:
                case Voice_Codes.PYTTS_MALE.value:
                    TTS_file_path = self.generate_pyTTS(TTS[1], voice = 0, rate = pyTTS_rate, TTS_fragment_index=i)

                case Voice_Codes.PYTTS_FEMALE.value:
                    TTS_file_path = self.generate_pyTTS(TTS[1], voice = 1, rate = pyTTS_rate, TTS_fragment_index=i)

                case Voice_Codes.GTTS.value:
                    TTS_file_path = self.generate_gTTS(TTS[1], TTS_fragment_index=i)

                case Voice_Codes.RANDOM.value:
                    voice_type = random.randint(0,len(Voice_Codes)-2)
                    if voice_type in [0,1]:
                        TTS_file_path = self.generate_pyTTS(TTS[1], voice = voice_type, rate = pyTTS_rate, TTS_fragment_index=i)
                    elif voice_type == 2:
                        TTS_file_path = self.generate_gTTS(TTS[1], TTS_fragment_index=i)

            #print(f"DEBUG: File path generated: {TTS_file_path}")

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

    # Generates TTS file using google voice.
    def generate_gTTS(self, text:"str", slow:"bool" = False, filename:"str" = "speech", TTS_fragment_index:"int" = 1) -> str:
        file_path = self._file_path_base + filename + str(TTS_fragment_index) + ".mp3"

        speech = gTTS(text = text, lang = "en", slow = False)
        speech.save(file_path)



        return file_path


    # Generates TTS file using pyTTS voices. Voices are male or female by default and selected using a random int.
    def generate_pyTTS(self, text:"str", voice:"int" = random.randint(0,1), rate:"int" = 200, filename:"str" = "speech", TTS_fragment_index:"int" = 1) -> str:
        file_path = self._file_path_base + filename + str(TTS_fragment_index) + ".wav"

        pyTTS_voices = self._pyTTS.getProperty('voices')

        
        self._pyTTS.setProperty("voice", pyTTS_voices[voice].id)
        self._pyTTS.setProperty("rate", rate)

        self._pyTTS.save_to_file(text, file_path)
        self._pyTTS.runAndWait()

        return file_path
    

    # Async handling functions & termination functions.

    async def terminate_module(self) -> None:

        self._running = False
        self._TTS_queue.shutdown(immediate = True)
        self._audio_player.skip_TTS()
        await asyncio.sleep(3)
    

    async def update(self) -> None:
        self._running = True
        while self._running:
            if not self._paused:
                print("Waiting for next TTS message")
                try:
                    await self._next_TTS_message()
                except Exception as e:
                    print(f"TTS Queue is shut down.")
                    break
            else:
                # Less frequent checking occurs while paused to improve performance.
                await asyncio.sleep(5)


    async def handle_notification(self, msg:"SubscriptionMessage") -> None:
        # No chat message commands for this module. Uncomment if any are added.
        """ if msg.subscription_type() == "channel.chat.message":
            print(f'{msg.event_data().chatter_user_name} said "{msg.event_data().message['text']}"')
            self._handle_chat_message(user = msg.event_data().chatter_user_name, text = msg.event_data().message['text']) """

        
        if msg.subscription_type() == "channel.channel_points_custom_reward_redemption.add":
            print(f'{msg.event_data().user_name} redeemed "{msg.event_data().reward['title']}"')
            await self._handle_point_reward(user = msg.event_data().user_name, reward = msg.event_data().reward['title'], text = msg.event_data().user_input)
