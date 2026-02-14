import string
import asyncio
from enum import Enum

# Used for function annotation. Not required at runtime.
from utils_hotkey_manager import Hotkey_Manager
from audio_module_audio_player import Audio_Manager
from connection_http_requests import HTTP_Requests
from twitchAPI.object.eventsub import ChannelChatMessageEvent, ChannelPointsCustomRewardRedemptionAddEvent, ChannelRaidEvent, ChannelAdBreakBeginEvent


class Reward_Titles(Enum):

    RUN_COMMERCIAL = "Subject the people to ADS!"


class General_Twitch_Functions():
    def __init__(self, http_requests:"HTTP_Requests") -> None:
        
        self.http_requests = http_requests

        # General variables used for maintaining update and preventing repeat chat commands (if desired).
        self._running = True
        self._last_command = ""

        # Chat-based command list for the match case.
        self._chat_commands = {}

        # List of point reward strings for the match case.
        self._reward_titles = {}
        
        self._reward_titles.update(dict.fromkeys([Reward_Titles.RUN_COMMERCIAL.value], "commercial"))



        
        # Used to identify how long it takes before another commercial break can be run.
        self.commercial_redeem_wait_time = 0





##### Public functions

    async def terminate_module(self) -> None:
        self._running = False


    async def update(self) -> None:
        
        self._running = True
        while self._running:

            await asyncio.sleep(1)

            if self.commercial_redeem_wait_time > 0:
                self.commercial_redeem_wait_time -= 1

                if self.commercial_redeem_wait_time == 0:
                    pass # Unpause commercial point redeem.


    # Receives chat message event and directs it according to the matching command based on self._chat_commands.
    async def _handle_chat_message(self, chat_message:"ChannelChatMessageEvent"):

        
        # Normalizes username to lowercase and removes punctuation for flexible command matching.
        text = str.lower(chat_message.event.message.text)
        text.translate(str.maketrans('', '', string.punctuation))

        if self._paused:
            return

        match self._chat_commands.get(text):
            case "null":
                pass

                

        if text in self._chat_commands.keys():
            self._last_command = self._chat_commands.get(text)



    # Receives channel point redemption event and directs it according to the matching point reward based on self._reward_titles.
    async def handle_point_reward(self, point_reward:"ChannelPointsCustomRewardRedemptionAddEvent") -> None:
        

        # TTS messages are only placed on the queue. update() constantly awaits the next TTS message.
        match self._reward_titles.get(point_reward.event.reward.title): 
            case "commercial":
                if self.commercial_redeem_wait_time == 0:
                    try:
                        self.commercial_redeem_wait_time = self.http_requests.start_commercial(point_reward.event.user_name)

                        if self.commercial_redeem_wait_time == 0:
                            self.http_requests.update_point_redemption_status(point_reward.event.id, point_reward.event.reward.id, "CANCELED")
                        else:
                            self.http_requests.update_point_redemption_status(point_reward.event.id, point_reward.event.reward.id, "FULFILLED")


                            

                    except Exception as e:
                        print(f"Encountered exception when starting commercial: \n{e}")
                        self.http_requests.update_point_redemption_status(point_reward.event.id, point_reward.event.reward.id, "CANCELED")
                    

                else:

                    self.http_requests.update_point_redemption_status(point_reward.event.id, point_reward.event.reward.id, "CANCELED")



    # Receives a raid event and responds appropriately, by shouting out the raider and thanking them for the raid.
    async def handle_raid(self, raid_info:"ChannelRaidEvent") -> None:


        if raid_info.event.viewers > 1:

            if raid_info.event.viewers >= 5:
                self.http_requests.send_shoutout(raid_info.event.from_broadcaster_user_id)

            channel_info = self.http_requests.get_channel_info(raid_info.event.from_broadcaster_user_id)

            self.http_requests.send_chat_message(f"{raid_info.event.from_broadcaster_user_name}! Thank you for dropping off your crew of {raid_info.event.viewers} people here! I hope that you had fun playing {channel_info['game_name']}!")

        return
    


    # Receives an ad break event and responds appropriately, by shouting out the raider and thanking them for the raid.
    async def handle_ad_break(self, ad_break_info:"ChannelAdBreakBeginEvent") -> None:

        self.http_requests.send_chat_announcement(f"THE AIDS ARE COMING! They will last for {ad_break_info.event.duration_seconds} seconds! Everybody panic!")

        await asyncio.sleep(0.2)

        self.http_requests.send_chat_message(f"Actually, don't panic. The ads are just to prevent prerolls from slapping people in the face when they join. If you would like to skip ads, feel free to subscribe! If you have Amazon Prime, you can use that to sub for free, too.")

        return