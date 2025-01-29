import requests
import json
import random
from enum import Enum

from utils_config import get_config

class _TWITCH_URI(Enum):
    
    USER_INFO = "https://api.twitch.tv/helix/users"
    CHANNEL_INFO = "https://api.twitch.tv/helix/channels"
    SEND_CHAT_MESSAGE = "https://api.twitch.tv/helix/chat/messages"
    SEND_CHAT_ANNOUNCEMENT = "https://api.twitch.tv/helix/chat/announcements"
    SEND_SHOUTOUT = "https://api.twitch.tv/helix/chat/shoutouts"
    RUN_COMMERCIAL = "https://api.twitch.tv/helix/channels/commercial"
    UPDATE_REDEMPTION_STATUS = "https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions"

TOKENS = 'user_token.json'


##### HTTP_Requests handles all HTTP requests for Twitch stuff.


class HTTP_Requests(object):
    def __init__(self) -> None:

        init_dict = get_config("INITIALIZATION")

        self.client_id = init_dict.get("client_id")

        self.user_id = init_dict.get("login_name")


    # Initializes the user ID based on what was provided in config.ini. 
    # Should be called separately, after the twitch connection is established. 
    # Calling this function before a new twitch connection is established may result in using an old and invalid refresh key.
    def init_user_id(self) -> None:

        self.user_id = self.get_user_id(self.user_id)


    # Sends a message to your channel using the given message. Can be used to reply to somebody.
    def send_chat_message(self, msg:"str", reply_target:"str" = "") -> None:

        payload = {
            "broadcaster_id": self.user_id,
            "sender_id": self.user_id,
            "message": msg
        }

        # Adds the target message to reply to if the message is meant to reply to somebody.
        if reply_target != "":
            payload.update(dict.fromkeys(["reply_parent_message_id"], reply_target))

        res = requests.post(url = _TWITCH_URI.SEND_CHAT_MESSAGE.value, data = json.dumps(payload), headers = self.get_http_request_headers(True))

        if res.status_code == 200:
            res = res.json()

            if res["data"][0]["is_sent"] != "true":
                pass


        else:
            raise Exception(f"Request failed; received status code {res.status_code} with error {res.text}")


    # Sends a highlighted announcement message to your channel. The announcement will use your channel's accent color for highlighting it.
    def send_chat_announcement(self, msg:"str") -> None:

        query_params = {
            "broadcaster_id": self.user_id,
            "moderator_id": self.user_id,
        }

        query = "?"
        for k,v in query_params.items():
            query = query + k + "=" + v + "&"

        query = query[:-1]


        payload = {
            "message": msg
        }


        print(f"DEBUG: \n{payload}\n\n")

        res = requests.post(url = f"{_TWITCH_URI.SEND_CHAT_ANNOUNCEMENT.value}{query}", data = json.dumps(payload), headers = self.get_http_request_headers(True))


        if res.status_code == 204:
            pass

        else:
            raise Exception(f"Request failed; received status code {res.status_code} with error {res.text}")



    # Shouts out the target channel based on the given ID. You can't give yourself a shoutout or give a shoutout when you aren't streaming.
    def send_shoutout(self, shoutout_target_id:"str") -> None:

        query_params = {
            "from_broadcaster_id": self.user_id,
            "to_broadcaster_id": shoutout_target_id,
            "moderator_id": self.user_id,
        }

        query = "?"
        for k,v in query_params.items():
            query = query + k + "=" + v + "&"

        query = query[:-1]

        res = requests.post(url = f"{_TWITCH_URI.SEND_SHOUTOUT.value}{query}", headers = self.get_http_request_headers())


        if res.status_code == 204:
            pass

        else:
            raise Exception(f"Request failed; received status code {res.status_code} with error {res.text}")
        
    

    # Updates the redemption status of a channel point reward. Requires speciic reward redemption ID along with the point reward ID. 
    # Possible statuses to declare are "CANCELED" and "FULFILLED". "CANCELED" will refund the channel points to the person that redeemed the reward.
    def update_point_redemption_status(self, redemption_id:"str", reward_id:"str", status:"str"):

        query_params = {
            "id": redemption_id,
            "broadcaster_id": self.user_id,
            "reward_id": reward_id,
        }

        query = "?"
        for k,v in query_params.items():
            query = query + k + "=" + v + "&"

        query = query[:-1]


        payload = {
            "status": status
        }


        res = requests.patch(url = f"{_TWITCH_URI.UPDATE_REDEMPTION_STATUS.value}{query}", data = payload, headers = self.get_http_request_headers(True))


        if res.status_code == 200:
            res = res.json()

            if res["data"][0]["status"] != status:
                print(f"REDEMPTION NOT UPDATED PROPERLY, CURRENT STATUS IS {res["data"][0]["status"]}!!!!")


        else:
            raise Exception(f"Request failed; received status code {res.status_code} with error {res.text}")


    
    # Starts a commercial on your channel. Why would you do this intentionally. 
    #
    # Length is read in seconds and is approximate. The actual commercial served by Twitch may be longer or shorter.
    # Any length >180 will be treated as 180 by Twitch.
    #
    # Returns an int of the number of seconds that must pass before a new commercial can be run. 
    # The returned value will generally be at least 60 seconds in case a commercial could not be served.
    def start_commercial(self, username:"str", length:"int" = random.randint(1,180)) -> int:

        payload = {
            "broadcaster_id": self.user_id,
            "length": length
        }

        res = requests.post(url = f"{_TWITCH_URI.RUN_COMMERCIAL.value}", data = payload, headers = self.get_http_request_headers(True))

        if res.status_code == 200:
            res_data = res.json()["data"][0]
            next_ad_time = [int(res_data["retry_after"] / 60), res_data["retry_after"] % 60]
            if next_ad_time > 0:
                self.send_chat_message(f"{username} has inflicted {res_data["length"]} seconds of advertisements upon you! How AWFUL. Fortunately, nobody can do it again for another {next_ad_time[0]} minutes and {next_ad_time[1]} seconds...")

        else:
            raise Exception(f"Request failed; received status code {res.status_code} with error {res.text}")




    # Generic function to obtain a twitch user's ID number based on their login username - i.e. what is used to log into Twitch, also displayed on a streamer's channel.
    def get_user_id(self, username:"str") -> str:

        query = f"?login={username}"

        res = requests.get(url = f"{_TWITCH_URI.USER_INFO.value}{query}", headers = self.get_http_request_headers())
        
        if res.status_code == 200:
            return res.json()["data"][0]["id"]

        else:
            raise Exception(f"Request failed; received status code {res.status_code} with error {res.text}")
        

    
    # Gets information about a channel, specified via user ID. Returns dict full of data about that channel.
    def get_channel_info(self, channel_id:"str") -> json:

        query = f"?broadcaster_id={channel_id}"

        res = requests.get(url = f"{_TWITCH_URI.CHANNEL_INFO.value}{query}", headers = self.get_http_request_headers())

        if res.status_code == 200:
            return res.json()["data"][0]

        else:
            raise Exception(f"Request failed; received status code {res.status_code} with error {res.text}")

        


    # Generic function for headers of all http requests sent to twitch URIs. Returns dict, needs to be submitted to http requests as **kwargs instead of being passed directly.
    def get_http_request_headers(self, incl_content_type:"bool" = False) -> dict:

        with open(TOKENS, "r") as file:
            tokens = json.load(file)

            print(f"Auth token is: {tokens['token']}\nRefresh token is: {tokens['refresh']}")


            if incl_content_type:
                return {
                    'Authorization': f'Bearer {tokens["token"]}',
                    'Client-Id': self.client_id,
                    'Content-Type': 'application/json'
                    }
            
            return {
                'Authorization': f'Bearer {tokens["token"]}',
                'Client-Id': self.client_id
                }



if __name__ == "__main__":

    http_requests = HTTP_Requests()

    http_requests.init_user_id()
    http_requests.send_chat_message("Hi, this is a test chat message.")
    http_requests.send_chat_announcement("And this is a test announcement!")