import string
import pydirectinput
import asyncio
import pyautogui
import numpy
import random
from enum import Enum

from utils.keycodes import *

# Used for function annotation. Not required at runtime.
from utils.hotkey_manager import Hotkey_Manager
from utils.message_parsing import SubscriptionMessage



#########################################################################################################
###############  Primarily used for integration with rain world via the Dev Console mod.  ###############
###############                                                                           ###############
###############      Requires manual updating for different game types. No default.       ###############
#########################################################################################################



class Reward_Titles(Enum):

    SNAILS = "SNAILS!!!"
    DIRECT_SPAWN = "Spawn Lock-on"
    DOUBLE_SPAWN = "Double Spawn Rate"
    TRAIN_SPAWN = "CHOO CHOO"



class Rain_World_Manager():
    def __init__(self, hotkey_manager:"Hotkey_Manager") -> None:
        
        pyautogui.FAILSAFE = False
        pydirectinput.FAILSAFE = False

        # Defines gameplay variables
        self._spawn_key = ONE
        self._spawn_rate = 1  # Per second

        # Defines mouse movement vectors. Movement speed is mickeys/0.02s
        self._vectors = [0,0]

        # Sets up ability to pause without closing the function.
        self._paused = False
        hotkey_manager.create_hotkey("Pause Button", "right shift+P", self._pause_unpause, force_assignment = True)
        hotkey_manager.create_hotkey("Swap Between Pearl Mode and Fruit Mode", "right shift+S", self._pause_unpause, force_assignment = True)

        # Creates dictionary of available commands as well as values to identify conditions for gameplay.
        self._last_command = None

        self._chat_commands = {}

        self._chat_commands.update(dict.fromkeys(["up"], "up"))
        self._chat_commands.update(dict.fromkeys(["down"], "down"))
        self._chat_commands.update(dict.fromkeys(["left"], "left"))
        self._chat_commands.update(dict.fromkeys(["right"], "right"))
        self._chat_commands.update(dict.fromkeys(["stop", "stahp"], "stop"))

        self._reward_IDs = {}

        self._reward_IDs.update(dict.fromkeys([Reward_Titles.SNAILS.value], "snails"))
        self._reward_IDs.update(dict.fromkeys([Reward_Titles.DIRECT_SPAWN.value], "direct_spawn"))
        self._reward_IDs.update(dict.fromkeys([Reward_Titles.DOUBLE_SPAWN.value], "double_spawn"))
        self._reward_IDs.update(dict.fromkeys([Reward_Titles.TRAIN_SPAWN.value], "train_spawn"))
        

    # Args for this function are generic and can be used according to the specific command messages desired.
    def _handle_chat_message(self, user:"str", text:"str") -> None:
        
        # Normalizes username to lowercase and removes punctuation for flexible command matching.
        text = str.lower(text)
        text.translate(str.maketrans('', '', string.punctuation))

        # Pausing prevents any rewards from occurring.
        if self._paused:
            return

        match self._chat_commands.get(text): 

            case "up":
                self._change_vectors(0, 4)

            case "down":
                self._change_vectors(0, -4)

            case "left":
                self._change_vectors(-4, 0)

            case "right":
                self._change_vectors(4, 0)

            case "stop":
                self._reset_vectors()

        if text in self._chat_commands.keys():
            self._last_command = self._chat_commands.get(text)


    # Args for this function are generic and can be used according to the specific rewards being used.
    async def _handle_point_reward(self, user:"str", reward:"str", text:"str") -> None:


        # Pausing prevents rewards from occurring.
        if self._paused:
            return
        

        match self._reward_IDs.get(reward): 
            case "snails":
                asyncio.create_task(self._spawn_snails())

            case "direct_spawn":
                asyncio.create_task(self._direct_spawning())

            case "double_spawn":
                asyncio.create_task(self._double_spawn())

            case "train_spawn":
                asyncio.create_task(self._train_spawn())


    ### In-game control functions, do not call from outside the class

    def _spawn_object(self) -> None:
        hold_and_release_key(self._spawn_key, 0.02)


    async def _spawn_snails(self) -> None:
        self._spawn_key = NUMPAD_2
        print("Snails have been activated.")
        await asyncio.sleep(30)
        self._spawn_key = NUMPAD_1
        print("Snails have been deactivated.")


    async def _direct_spawning(self) -> None:
        self._spawn_key = NUMPAD_3
        print("Spawning on top of you.")
        await asyncio.sleep(40)
        self._spawn_key = NUMPAD_1
        print("Spawning normally again.")


    async def _double_spawn(self) -> None:
        self._spawn_rate = self._spawn_rate * 2
        print("Spawning at double time.")
        await asyncio.sleep(60)
        self._spawn_rate = self._spawn_rate / 2
        print("Spawning normally again.")


    async def _double_spawn(self) -> None:
        print("Spawning a TRAIN.")
        hold_and_release_key(NUMPAD_4, 0.02)


    def _pearl_mode(self) -> None:
        print("Changing to pearl mode.")


    # Movement vectors are changed according to xmod and ymod. Called by most chat message commands.
    def _change_vectors(self, xmod:"int", ymod:"int") -> None:
        
        mod = [xmod,ymod]

        for i, item in enumerate(mod):

            # Resets vector to 0 if mod has the opposite sign.
            if self._vectors[i] * mod[i] < 0:
                self._vectors[i] = 0

            self._vectors[i] += mod[i]


    # Movement vectors are reset. Called at state transition points and during slight movement adjustment.
    def _reset_vectors(self) -> None:
        for i, item in enumerate(self._vectors):
            self._vectors[i] = 0


    # Mouse is moved at a smoothed rate.
    def _move_mouse(self, x:"int", y:"int") -> None:
        pydirectinput.moveRel(x, y, duration = 0.02)

        # Clamps cursor location to within primary monitor.
        x = numpy.clip(pydirectinput.position()[0], 0, 2560)
        y = numpy.clip(pydirectinput.position()[1], 0, 1440)
        if pydirectinput.position() != [x,y]:
            pydirectinput.moveTo(x, y)
        

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

        start_time = time.monotonic()

        self._running = True
        while self._running:
            if not self._paused:
                self._move_mouse(self._vectors[0], self._vectors[1])

                if (int((time.monotonic() - start_time) * 50) % (50/self._spawn_rate)) == 0:
                    self._spawn_object()

                await asyncio.sleep(0.02)
            else:
                # Less frequent checking occurs while paused to improve performance.
                await asyncio.sleep(1)
            
            

    async def handle_notification(self, msg:"SubscriptionMessage") -> None:
        if msg.subscription_type() == "channel.chat.message":
            print(f'{msg.event_data().chatter_user_name} said "{msg.event_data().message['text']}"')
            self._handle_chat_message(user = msg.event_data().chatter_user_name, text = msg.event_data().message['text'])

        if msg.subscription_type() == "channel.channel_points_custom_reward_redemption.add":
            print(f'{msg.event_data().user_name} redeemed "{msg.event_data().reward['title']}"')
            await self._handle_point_reward(user = msg.event_data().user_name, reward = msg.event_data().reward['id'], text = msg.event_data().user_input)