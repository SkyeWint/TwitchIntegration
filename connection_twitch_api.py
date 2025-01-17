#### Twitch API imports.

from twitchAPI.twitch import Twitch
from twitchAPI.helper import first
from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.type import AuthScope
from twitchAPI.eventsub.websocket import EventSubWebsocket
from twitchAPI.object.eventsub import ChannelChatMessageEvent, ChannelPointsCustomRewardRedemptionAddEvent


#### General imports.

import asyncio


#### Imports from this project.

from utils_config import get_config



class Twitch_Connection():
    def __init__(self, module_list:"list") -> None:

        # Preps empty sets for all required callback functions from current modules.
        self.chat_message_callbacks = set()
        self.point_reward_callbacks = set()

        # Cycles through all modules passed to the twitch connection on initialization and adds them to the lists.
        for module in module_list:

            # Verifies the callback functions exist in the module list, then adds existing functions to their relevant lists.
            if callable(getattr(module, "handle_chat_message", None)):
                self.chat_message_callbacks.add(module.handle_chat_message)

            if callable(getattr(module, "handle_point_reward", None)):
                self.point_reward_callbacks.add(module.handle_point_reward)


        # Declares main relevant variables for future usage.
        self.running = True
        self.client_id = None
        self.client_secret = None
        self.twitch = None
        self.helper = None
        self.user = None



    ##### Private Functions


    ## Event callback functions: Calls all callbacks based on the given chat message.

    # Only to be awaited by eventsub in run().
    async def _on_chat_message(self, data:"ChannelChatMessageEvent") -> None:

        for callback in self.chat_message_callbacks:
            await callback(data)


    async def _on_point_redemption(self, data:"ChannelPointsCustomRewardRedemptionAddEvent") -> None:

        for callback in self.point_reward_callbacks:
            await callback(data)



    ##### Public Functions


    # Informs twitch integration to disconnect gracefully.
    def stop_running(self) -> None:

        self.running = False


    # Initializes Twitch object in the class based on data in config.ini.
    async def initialize_twitch(self) -> None:
        initialization_dict = get_config("INITIALIZATION")

        self.client_id = initialization_dict.get("client_id")
        self.client_secret = initialization_dict.get("client_secret")

        # Initializes API instance with app authentication.
        self.twitch = await Twitch(self.client_id, self.client_secret)

        print("App authentication complete.")

        # Initializes user authentication and sets up helper to maintain auth tokens.
        target_scopes = []
        for scope in str(initialization_dict.get("scope")).split():
            target_scopes.append(AuthScope[scope])

        self.helper = UserAuthenticationStorageHelper(self.twitch, target_scopes)
        await self.helper.bind()

        print("User authentication complete.")


        # Establishes currently logged-in user and all information from it.
        self.user = await first(self.twitch.get_users(logins=initialization_dict.get("login_name")))

        print(f"Current user is {self.user.display_name}")


    # Runs active event subscriptions until hotkey is detected to stop running the functions.
    async def run(self) -> None:
        
        # Starts the client 
        eventsub = EventSubWebsocket(self.twitch)
        eventsub.start()


        # Sets up all callback functions.
        await eventsub.listen_channel_chat_message(self.user.id, self.user.id, self._on_chat_message)
        await eventsub.listen_channel_points_custom_reward_redemption_add(self.user.id, self._on_point_redemption)


        while self.running:
            await asyncio.sleep(2)

        print("Closing eventsub and API connection...")

        await eventsub.stop()
        await self.twitch.close()

        print("Fully shut down. Exiting.")

