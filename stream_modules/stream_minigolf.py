import string
import pydirectinput
import asyncio
import pyautogui
import numpy

from utils.keycodes import *

# Used for function annotation. Not required at runtime.
from utils.hotkey_manager import Hotkey_Manager
from utils.message_parsing import SubscriptionMessage



class Minigolf_Manager():
    def __init__(self, hotkey_manager:"Hotkey_Manager") -> None:
        
        pyautogui.FAILSAFE = False


        # Defines mouse movement vectors. ...and some limits to movement. Movement speed is measured in mickeys/0.02s
        self._vectors = [0,0]
        self._vector_limit = 50
        self._power_total = 0
        self._power_limit = 2000

        # Sets up ability to pause without closing the function.
        self._paused = False
        hotkey_manager.create_hotkey("Pause Button", "right shift+P", self._pause_unpause, force_assignment = True)

        # Creates dictionary of available commands as well as values to identify conditions for gameplay.
        self._aiming = True
        self._last_command = None

        self._slight_power_adjustment_limit = 3
        self._slight_power_adjustment_counter = 0

        self._slight_aim_adjustment_limit = 3
        self._slight_aim_adjustment_counter = 0

        self._chat_commands = {}

        # Adding library of chat commands and command aliases. Grouped by function.
        self._chat_commands.update(dict.fromkeys(["up", "mario"], "up"))
        self._chat_commands.update(dict.fromkeys(["down"], "down"))

        self._chat_commands.update(dict.fromkeys(["left", "luigi"], "left"))
        self._chat_commands.update(dict.fromkeys(["slightly left", "slighty left", "sleft"], "slightly left"))

        self._chat_commands.update(dict.fromkeys(["right"], "right"))
        self._chat_commands.update(dict.fromkeys(["slightly right", "slighty right", "slight", "sright"], "slightly right"))

        self._chat_commands.update(dict.fromkeys(["more", "moar", "morio"], "more"))
        self._chat_commands.update(dict.fromkeys(["slightly more", "slighty more", "smore", "smores"], "slightly more"))

        self._chat_commands.update(dict.fromkeys(["less"], "less"))
        self._chat_commands.update(dict.fromkeys(["slightly less", "slighty less", "sless"], "slightly less"))

        self._chat_commands.update(dict.fromkeys(["stop", "stahp", "gandalf"], "stop"))
        self._chat_commands.update(dict.fromkeys(["aim", "cancel", "retarget"], "aim"))
        self._chat_commands.update(dict.fromkeys(["fire", "shoot", "launch", "swing", "shmup"], "fire"))
        self._chat_commands.update(dict.fromkeys(["targeted", "target lock", "focus", "lock in", "lock on"], "lock in"))

        self._chat_commands.update(dict.fromkeys(["jump", "yeet"], "jump"))
    

    # Args for this function are generic and can be used according to the specific command messages desired.
    def _handle_chat_message(self, user:str, text:str):
        
        # Normalizes username to lowercase and removes punctuation for flexible command matching.
        text = str.lower(text)
        text.translate(str.maketrans('', '', string.punctuation))

        if self._paused:
            return

        # Some commands should only be usable while aiming, others should only be usable once aiming is over.
        if self._aiming:
            match self._chat_commands.get(text):
                case "up":
                    self._change_vectors(0, 4)

                case "down":
                    self._change_vectors(0, -4)

                case "left":
                    self._change_vectors(-4, 0)

                case "right":
                    self._change_vectors(4, 0)
                
                case "lock in":
                    self._lock_in_aim()

                case "slightly right":
                    if self._slight_aim_adjustment_counter < self._slight_aim_adjustment_limit:
                        self._slight_movement(15, 0)
                        self._slight_aim_adjustment_counter += 1
                    print(self._slight_aim_adjustment_counter)

                case "slightly left":
                    if self._slight_aim_adjustment_counter < self._slight_aim_adjustment_limit:
                        self._slight_movement(-15, 0)
                        self._slight_aim_adjustment_counter += 1
                    print(self._slight_aim_adjustment_counter)


        else:
            match self._chat_commands.get(text):
                case "more":
                    self._change_vectors(0, 4)

                case "less":
                    self._change_vectors(0, -4)

                case "slightly more":
                    if self._slight_power_adjustment_counter < self._slight_power_adjustment_limit:
                        self._slight_movement(0, 15)
                        self._slight_power_adjustment_counter += 1
                    print(self._slight_power_adjustment_counter)

                case "slightly less":
                    if self._slight_power_adjustment_counter < self._slight_power_adjustment_limit:
                        self._slight_movement(0, -15)
                        self._slight_power_adjustment_counter += 1
                    print(self._slight_power_adjustment_counter)

                case "aim":
                    if self._last_command == "aim":
                        self._go_back_to_aiming()

                        # Power adjustment-related counters are reset when aiming.
                        self._slight_power_adjustment_counter = 0

                case "fire":
                    if self._last_command == "fire":
                        self._fire()

                        # All counters are reset when firing as the turn is over. 
                        self._slight_power_adjustment_counter = 0
                        self._slight_aim_adjustment_counter = 0
                        self._power_total = 0


        match self._chat_commands.get(text):
            case "stop":
                self._reset_vectors()
            
            case "jump":
                hold_and_release_key(J, 0.02)


        if text in self._chat_commands.keys():
            self._last_command = self._chat_commands.get(text)


    ### In-game control functions, do not call from outside the class

    # Movement vectors are changed according to xmod and ymod. Called by most chat message commands.
    def _change_vectors(self, xmod:int, ymod:int) -> None:
        
        mod = [xmod, ymod]

        for i, item in enumerate(mod):
            # Resets vector to 0 if mod has the opposite sign.
            if self._vectors[i] * mod[i] < 0:
                self._vectors[i] = 0

            self._vectors[i] += mod[i]

        # Ensures that vector values do not exceed limits.
        numpy.clip(self._vectors, self._vector_limit * -1, self._vector_limit)

        


    # Movement vectors are reset. Called at state transition points and during slight movement adjustment.
    def _reset_vectors(self) -> None:
        for i, item in enumerate(self._vectors):
            self._vectors[i] = 0


    # Moves the mouse slightly after stopping constant movement.
    def _slight_movement(self, x:int, y:int):
        self._reset_vectors()
        self._move_mouse(x, y)


    # Mouse is moved at a smoothed rate.
    def _move_mouse(self, x:int, y:int) -> None:

        # Increasing power is disabled if the power quantity exceeds the limit because dear god was that excessive in Golf It last time.
        if self._power_total >= self._power_limit and y > 0:
            self._vectors[1] = 0
        
        pydirectinput.moveRel(x, y, duration = 0.02, relative = True)

        # Total power quantity is actively tracked each time the mouse is moved.
        if not self._aiming:
            self._power_total += y
            numpy.clip(self._power_total, 0, self._power_limit)



    def _lock_in_aim(self):
        self._reset_vectors()
        pydirectinput.mouseDown()
        self._aiming = False


    def _go_back_to_aiming(self):
        self._reset_vectors()
        pydirectinput.moveRel(0, -5000, relative = True)
        pydirectinput.rightClick()
        pydirectinput.mouseUp()
        self._aiming = True


    def _fire(self):
        self._reset_vectors()
        pydirectinput.mouseUp()
        self._aiming = True
        print("Debug: FIRE!")


    # To be called via hotkey only. Pauses command processing and movement.
    def _pause_unpause(self) -> None:
        self._paused = not self._paused
        if self._paused:
            print("Minigolf integration is now paused.")
        elif not self._paused:
            print("Minigolf integration is now unpaused.")


    ##### Public functions

    async def terminate_module(self) -> None:
        self._running = False


    async def update(self) -> None:
        
        self._running = True
        while self._running:
            if not self._paused:
                self._move_mouse(self._vectors[0], self._vectors[1])

                await asyncio.sleep(0.02)
            else:
                # Less frequent checking occurs while paused to improve performance.
                await asyncio.sleep(1)
    

    async def handle_notification(self, msg:"SubscriptionMessage") -> None:
        if msg.subscription_type() == "channel.chat.message":
            print(f'{msg.event_data().chatter_user_name} said "{msg.event_data().message['text']}"')
            self._handle_chat_message(user = msg.event_data().chatter_user_name, text = msg.event_data().message['text'])

        # No channel point reward redemptions for this module. Uncomment if any are added.
        """ if msg.subscription_type() == "channel.channel_points_custom_reward_redemption.add":
            print(f'{msg.event_data().user_name} redeemed "{msg.event_data().reward['title']}"')
            await self._handle_point_reward(user = msg.event_data().user_name, reward = msg.event_data().reward['id']) """