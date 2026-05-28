import os
import string
import random
from enum import Enum

from twitchAPI.object.eventsub import ChannelChatMessageEvent
from twitchAPI.object.eventsub import ChannelPointsCustomRewardRedemptionAddEvent

# Used for function annotation. Not required at runtime.
from audio_module_audio_player import Audio_Manager
from connection_http_requests import HTTP_Requests


######### Enum and Constants List #########

FREE_SOUND_EFFECT_FOLDER_PATH_BASE = ".\\free_sound_effects\\"

POINT_SOUND_EFFECT_FOLDER_PATH_BASE = ".\\point_sound_effects\\"


# If you want different titles for the point rewards set up by this code, specify them here.
class Reward_Titles(Enum):

    BABY = "Wehhhhh"




class Sound_Manager(object):
    def __init__(self, audio_player:"Audio_Manager", http_requests:"HTTP_Requests") -> None:
        
        self._audio_player = audio_player
        self.http_requests = http_requests

        # Creates dictionary of available commands as well as values to identify conditions for gameplay.
        self._last_message = None

        self._chat_commands = {}

     # Creates list of commands based on sound effect folder names.
        free_sound_effect_commands = os.listdir(FREE_SOUND_EFFECT_FOLDER_PATH_BASE)

        for command in free_sound_effect_commands:
            self._chat_commands.update(dict.fromkeys([command], command))

        # Adds aliases to commands if desired.
        self._chat_commands.update(dict.fromkeys(["myar", "mrow", "mrowr"], "meow"))
        self._chat_commands.update(dict.fromkeys(["bap", "bop"], "bonk"))
        self._chat_commands.update(dict.fromkeys(["garama"], "garava"))


        # Sets up reward IDs for TTS redemptions. Additional TTS redemptions will be added later with fancier voices if desired.
        self._reward_titles = {}

        # The values in [] brackets MUST match the point rewards on your channel, whichever is changed.
        self._reward_titles.update(dict.fromkeys([Reward_Titles.BABY.value], "baby cry"))



    

    
    # Randomly selects a .ogg or .wav sound effect from the provided folder path out of the valid files that exist in the folder.
    def _select_sound_effect(self, folder_path) -> str:
        
        sound_effect_list = os.listdir(folder_path)

        # Removes all files in the list that are not .wav or .ogg files.
        for i, _ in enumerate(sound_effect_list):
            while sound_effect_list[i][-4:] != ".wav" and sound_effect_list[i][-4:] != ".ogg":
                sound_effect_list.pop(i)


        # Selects a random sound effect from the list, testing the file to ensure it is valid before returning the path for playing the file.
              
        while len(sound_effect_list) > 0:

            sound = random.choice(sound_effect_list)

            if os.path.isfile(folder_path + sound):
                return folder_path + sound
            else:
                print(f"File {folder_path}{sound} does not actually exist!")
                sound_effect_list.remove(sound)
        
        print("No matching files. Returning empty string.")
        return ""



    ##### Public functions



        # Plays a sound from the given sound effect folder, if the folder exists.
    def play_random_sound_effect(self, folder_name, folder_path_base):

        if folder_name in os.listdir(folder_path_base): 

            folder_path = folder_path_base + f"{folder_name}\\"

            self._audio_player.play_sound(self._select_sound_effect(folder_path))



    async def terminate_module(self) -> None:

        # Deletes TTS reward so it is no longer redeemable.
        self.http_requests.delete_reward(reward_title = Reward_Titles.BABY.value)



    async def update(self) -> None:

        # Sound Effect Rewards
        try:
            self.http_requests.create_reward(Reward_Titles.BABY.value, cost = 5000, user_input_required = False, background_color = "#392e5c", global_cooldown_seconds = 600, prompt = "Open Skye's inventory and disturb the baby. ")

        except Exception as e:
            print("!!Attempting to create the TTS reward resulted in the following exception!!")
            print(e)



    # Receives chat message event and directs it according to the matching command based on self._chat_commands.
    async def handle_chat_message(self, chat_message:"ChannelChatMessageEvent") -> None:


        # Normalizes username to lowercase and removes punctuation for flexible command matching.
        text = str.lower(chat_message.event.message.text)
        text.translate(str.maketrans('', '', string.punctuation))

        if text != self._last_message:

            # Special response to "bap" messages
            if text == "bap":
                self.http_requests.send_chat_message("Bop!", chat_message.event.message_id)

            # Plays sound effect if a match is identified
            self.play_random_sound_effect(self._chat_commands.get(text), FREE_SOUND_EFFECT_FOLDER_PATH_BASE)


        self._last_message = text


    # Receives channel point redemption event and directs it according to the matching point reward based on self._reward_titles.
    async def handle_point_reward(self, point_reward:"ChannelPointsCustomRewardRedemptionAddEvent") -> None:
        
        

        # TTS messages are only placed on the queue. update() constantly awaits the next TTS message.
        match self._reward_titles.get(point_reward.event.reward.title): 
            case "baby cry":
                print(f"{point_reward.event.user_name} is being a whiny baby!")
                self.play_random_sound_effect("crying_greyroot_bud", POINT_SOUND_EFFECT_FOLDER_PATH_BASE)
                