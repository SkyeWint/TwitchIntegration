import os
import string
import random

from twitchAPI.object.eventsub import ChannelChatMessageEvent

# Used for function annotation. Not required at runtime.
from audiomodule_audio_player import Audio_Manager



class Sound_Manager(object):
    def __init__(self, audio_player:"Audio_Manager") -> None:
        
        self._audio_player = audio_player

        # Creates dictionary of available commands as well as values to identify conditions for gameplay.
        self._last_message = None

        self._chat_commands = {}

        self._chat_commands.update(dict.fromkeys(["meow", "myar", "mrow", "mrowr"], "meow"))
        self._chat_commands.update(dict.fromkeys(["bonk", "bap"], "bonk"))

    

    # Verifies that a .ogg or .wav file exists based on a given sound name. Ogg files are always prioritized over Wav files.
    # A number of variations can be provided to check a list of files in the sound_effects\ folder, with each file in the list following the format: [name][index][filetype].
    def _construct_filepath(self, sound_name:"str", variations:"int" = 1) -> str:
        file_path_base = ".\\sound_effects\\"

        if variations > 1:
            variation_list = []
            for i in range(variations):
                variation_list.append(i)

            while len(variation_list) > 0:

                variation = random.randint(0, len(variation_list) - 1)

                if os.path.isfile(file_path_base + sound_name + str(variation) + ".ogg"):
                    return file_path_base + sound_name + str(variation) + ".ogg"
                elif os.path.isfile(file_path_base + sound_name + str(variation) + ".wav"):
                    return file_path_base + sound_name + str(variation) + ".wav"
                else:

                    variation_list.pop(variation)
        else:
            if os.path.isfile(file_path_base + sound_name + ".ogg"):
                return file_path_base + sound_name + ".ogg"
            elif os.path.isfile(file_path_base + sound_name + ".wav"):
                return file_path_base + sound_name + ".wav"
        
        print("No matching files. Returning empty string.")
        return ""
            



    ##### Public functions


    # Receives chat message event and directs it according to the matching command based on self._chat_commands.
    async def handle_chat_message(self, chat_message:"ChannelChatMessageEvent") -> None:
        
        # Normalizes username to lowercase and removes punctuation for flexible command matching.
        text = str.lower(chat_message.event.message.text)
        text.translate(str.maketrans('', '', string.punctuation))

        match self._chat_commands.get(text): 

            case "meow":
                if self._chat_commands.get(text) != self._chat_commands.get(self._last_message):
                    meow = self._construct_filepath("meow", variations=17)
                    self._audio_player.play_sound(meow)

            case "bonk":
                if self._chat_commands.get(text) != self._chat_commands.get(self._last_message):
                    bonk = self._construct_filepath("bonk")
                    self._audio_player.play_sound(bonk)

        
        self._last_message = text