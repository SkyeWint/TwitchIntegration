import string
import pydirectinput
import asyncio
import pyautogui
import numpy
from enum import Enum

from utils_keycodes import *

from twitchAPI.object.eventsub import ChannelChatMessageEvent, ChannelPointsCustomRewardRedemptionAddEvent

# Used for function annotation. Not required at runtime.
from utils_hotkey_manager import Hotkey_Manager
from audio_module_audio_player import Audio_Manager
from connection_http_requests import HTTP_Requests



# For Rain World


class Reward_Titles(Enum):

    SPEED_UP = "Make the game FASTER"
    SLOW_DOWN = "Make the game slower..."
    PAUSE = "Pause the Rain!!"
    SPAWN_DLL = "Spawn Daddy Long Legs"
    SPAWN_SNAILS = "Spawn Snails"





class Rain_World_Manager():
    def __init__(self, hotkey_manager:"Hotkey_Manager", audio_manager:"Audio_Manager", http_requests:"HTTP_Requests") -> None:
        
        pyautogui.FAILSAFE = False

        self.audio_manager = audio_manager
        self.http_requests = http_requests


        # Defines mouse movement vectors. ...and some limits to movement. Movement speed is measured in mickeys/0.02s
        self._vectors = [0,0]
        self._vector_limit = 50

        # Sets up ability to pause without closing the function.
        self._paused = True
        hotkey_manager.create_hotkey("Pause Rain World Integration Updates", "right shift+P", self._pause_unpause, force_assignment = True)

        # Creates dictionary of available chat commands as well as values to identify conditions for gameplay.
        self._aiming = True
        self._last_command = None

        # Speed altering stream variables.
        self._gamespeed = 1  # Max of 9, should increment game speed by 0.25
        self._gamespeed_mod = 0
        self._rain_paused = False
        self._reset_gamespeed = False
        hotkey_manager.create_hotkey("Reset Rain World Gamespeed", "left shift+r", self._encountered_echo, force_assignment = True)


        self._chat_commands = {}

        # Adding library of chat commands and command aliases. Grouped by function.
        """ self._chat_commands.update(dict.fromkeys(["up", "mario"], "up"))
        self._chat_commands.update(dict.fromkeys(["down"], "down"))
        self._chat_commands.update(dict.fromkeys(["left", "luigi"], "left"))
        self._chat_commands.update(dict.fromkeys(["right"], "right")) """


        # Sets up point reward IDs.
        self._reward_titles = {}

        # The values in [] brackets MUST match the point rewards on your channel, whichever is changed.
        self._reward_titles.update(dict.fromkeys([Reward_Titles.SPEED_UP.value], "faster"))
        self._reward_titles.update(dict.fromkeys([Reward_Titles.SLOW_DOWN.value], "slower"))
        self._reward_titles.update(dict.fromkeys([Reward_Titles.PAUSE.value], "pause"))
        self._reward_titles.update(dict.fromkeys([Reward_Titles.SPAWN_DLL.value], "dll"))
        self._reward_titles.update(dict.fromkeys([Reward_Titles.SPAWN_SNAILS.value], "snails"))

    


    ### In-game control functions, do not call from outside the class

    async def _pause_rain_timer(self) -> None:

        await hold_and_release_key(NUMPAD_0, 0.01)

        self._rain_paused = not self._rain_paused

        if self._rain_paused:
            self.audio_manager.play_sound("D:\\Streaming\\Sound Effects\\Rain-World-Sounds-main\\UI\\UIPitch2.wav")

            with open("D:\\Streaming\\is_rain_timer_paused.txt", "w") as file:
                file.write("Rain Timer:\nPaused!")

        else:
            self.audio_manager.play_sound("D:\\Streaming\\Sound Effects\\Rain-World-Sounds-main\\UI\\UIPitch1.wav")

            with open("D:\\Streaming\\is_rain_timer_paused.txt", "w") as file:
                file.write("Rain Timer:\nRunning!")




    async def _gamespeed_trigger(self, key_number:"int") -> None:
        
        match key_number:
            case 1:
                await hold_and_release_key(NUMPAD_1, 0.01)

                with open("D:\\Streaming\\current_game_speed.txt", "w") as file:
                    file.write("Current game speed:\n1x")

            case 2:
                await hold_and_release_key(NUMPAD_2, 0.01)
                
                with open("D:\\Streaming\\current_game_speed.txt", "w") as file:
                    file.write("Current game speed:\n1.25x")

            case 3:
                await hold_and_release_key(NUMPAD_3, 0.01)
                
                with open("D:\\Streaming\\current_game_speed.txt", "w") as file:
                    file.write("Current game speed:\n1.5x")

            case 4:
                await hold_and_release_key(NUMPAD_4, 0.01)
                
                with open("D:\\Streaming\\current_game_speed.txt", "w") as file:
                    file.write("Current game speed:\n1.75x")

            case 5:
                await hold_and_release_key(NUMPAD_5, 0.01)
                
                with open("D:\\Streaming\\current_game_speed.txt", "w") as file:
                    file.write("Current game speed:\n2x")

            case 6:
                await hold_and_release_key(NUMPAD_6, 0.01)
                
                with open("D:\\Streaming\\current_game_speed.txt", "w") as file:
                    file.write("Current game speed:\n2.25x")

            case 7:
                await hold_and_release_key(NUMPAD_7, 0.01)
                
                with open("D:\\Streaming\\current_game_speed.txt", "w") as file:
                    file.write("Current game speed:\n2.5x")

            case 8:
                await hold_and_release_key(NUMPAD_8, 0.01)
                
                with open("D:\\Streaming\\current_game_speed.txt", "w") as file:
                    file.write("Current game speed:\n2.75x")

            case 9:
                await hold_and_release_key(NUMPAD_9, 0.01)
                
                with open("D:\\Streaming\\current_game_speed.txt", "w") as file:
                    file.write("Current game speed:\n3x")

        self.audio_manager.play_sound("D:\\Streaming\\Sound Effects\\Rain-World-Sounds-main\\UI\\UIWoodHit.wav")
            


    # Changes game speed by {mod} units. Cannot be less than 1 or greater than 9. Calling function with 0 as argument resets the game speed to 1.
    async def _alter_gamespeed(self, mod:"int", permanent:"bool" = False) -> None:

        if permanent:

            if mod == 0:
                self._gamespeed = 1
            else:
                self._gamespeed += mod

                numpy.clip(self._gamespeed, 1, 9)

        else:
            self._gamespeed_mod += mod

            await self._gamespeed_trigger(numpy.clip((self._gamespeed + self._gamespeed_mod), 1, 9))

            await asyncio.sleep(30)

            self._gamespeed_mod -= mod

        await self._gamespeed_trigger(numpy.clip((self._gamespeed + self._gamespeed_mod), 1, 9))


    def _encountered_echo(self):

        self._reset_gamespeed = True


    # To be called via hotkey only. Pauses command processing and movement.
    def _pause_unpause(self) -> None:
        self._paused = not self._paused
        if self._paused:
            print("Rain World integration is now paused.")
        elif not self._paused:
            print("Rain World integration is now unpaused.")


    ##### Public functions

    async def terminate_module(self) -> None:
        self._running = False


    async def update(self) -> None:
        
        self._counter = 0

        with open("D:\\Streaming\\time_until_speed_up.txt", "w") as file:
            text = f"Game speed increases in\n{5 - int(self._counter / 60)} minutes."
            file.write(text)

        print("Wrote initial file.")

        self._running = True
        while self._running:
            if self._reset_gamespeed:
                self._reset_gamespeed = False

                await self._alter_gamespeed(0, True)
                self._counter = 0

                await asyncio.sleep(1)
                continue

            if self._paused:
                # Less frequent checking occurs while paused to improve performance.
                await asyncio.sleep(1)

            else:
                await asyncio.sleep(1)
                self._counter += 1


                if self._counter >= 300:
                    self._counter = 0
                    await self._alter_gamespeed(1, True)
                    with open("D:\\Streaming\\time_until_speed_up.txt", "w") as file:
                        text = f"Game speed increases in\n{5 - int(self._counter / 60)} minutes."
                        file.write(text)

                elif self._counter % 60 == 0:

                    print(str(int(self._counter / 60)))

                    with open("D:\\Streaming\\time_until_speed_up.txt", "w") as file:
                        text = f"Game speed increases in\n{5 - int(self._counter / 60)} minutes."
                        file.write(text)
    


    # Receives chat message event and directs it according to the matching command based on self._chat_commands.
    async def _handle_chat_message(self, chat_message:"ChannelChatMessageEvent"):

        
        # Normalizes username to lowercase and removes punctuation for flexible command matching.
        text = str.lower(chat_message.event.message.text)
        text.translate(str.maketrans('', '', string.punctuation))

        if self._paused:
            return

        match self._chat_commands.get(text):
            case "up":
                pass

                


        if text in self._chat_commands.keys():
            self._last_command = self._chat_commands.get(text)


    # Receives channel point redemption event and directs it according to the matching point reward based on self._reward_titles.
    async def handle_point_reward(self, point_reward:"ChannelPointsCustomRewardRedemptionAddEvent") -> None:


        print(f"Received point reward: {point_reward.event.reward.title}")
        

        # TTS messages are only placed on the queue. update() constantly awaits the next TTS message.
        match self._reward_titles.get(point_reward.event.reward.title): 
            case "faster":
                print(f"You're going too slow. Go faster, damn it.")
                await self._alter_gamespeed(1)

            case "slower":
                print(f"Things are a bit too fast, let's slow down a bit please...")
                await self._alter_gamespeed(-1)

            case "pause":
                print("Rain Timer now paused (or unpaused!)")
                await self._pause_rain_timer()

            case "dll":
                await hold_and_release_key(D, 0.01)

            case "snails":
                await hold_and_release_key(S, 0.01)