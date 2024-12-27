import os
import string
import random

# Used for function annotation. Not required at runtime.
from audio_player import Audio_Manager
from utils.message_parsing import SubscriptionMessage



class Sound_Manager(object):
    def __init__(self, audio_player:"Audio_Manager") -> None:
        
        self._audio_player = audio_player

        # Creates dictionary of available commands as well as values to identify conditions for gameplay.
        self._last_command = None

        self._chat_commands = {}

        self._chat_commands.update(dict.fromkeys(["meow", "myar", "mrow", "mrowr"], "meow"))
        self._chat_commands.update(dict.fromkeys(["bonk", "bap"], "bonk"))


    # Args for this function are generic and can be used according to the specific command messages desired.
    def _handle_chat_message(self, user:str, text:str) -> None:
        
        # Normalizes username to lowercase and removes punctuation for flexible command matching.
        text = str.lower(text)
        text.translate(str.maketrans('', '', string.punctuation))

        match self._chat_commands.get(text): 

            case "meow":
                if self._chat_commands.get(text) != self._chat_commands.get(self._last_command):
                    meow = self._construct_filepath("meow", variations=17)
                    self._audio_player.play_sound(meow)

            case "bonk":
                if self._chat_commands.get(text) != self._chat_commands.get(self._last_command):
                    bonk = self._construct_filepath("bonk")
                    self._audio_player.play_sound(bonk)

                    
        if text in self._chat_commands.keys():
            self._last_command = self._chat_commands.get(text)
    

    # Verifies that a .ogg or .wav file exists based on a given sound name. Ogg files are always prioritized over Wav files.
    # A number of variations can be provided to check a list of files in the sound_effects\ folder, with each file in the list following the format: [name][index][filetype].
    def _construct_filepath(self, sound_name:str, variations:int = 1) -> str:
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

    async def handle_notification(self, msg:"SubscriptionMessage") -> None:
        if msg.subscription_type() == "channel.chat.message":
            #print(f'{msg.event_data().chatter_user_name} said "{msg.event_data().message['text']}"')
            self._handle_chat_message(user = msg.event_data().chatter_user_name, text = msg.event_data().message['text'])

        # No channel point reward redemptions for this module. Uncomment if any are added.
        """ if msg.subscription_type() == "channel.channel_points_custom_reward_redemption.add":
            print(f'{msg.event_data().user_name} redeemed "{msg.event_data().reward['title']}"')
            await self._handle_point_reward(user = msg.event_data().user_name, reward = msg.event_data().reward['id']) """