import requests
import json
from enum import Enum

from utils_config import get_config

class _TWITCH_URI(Enum):
    
    USERS = "https://api.twitch.tv/helix/users"

TOKENS = 'user_token.json'

##### HTTP_Requests handles all HTTP requests for 

class HTTP_Requests(object):
    def __init__(self) -> None:

        self.client_id = get_config("INITIALIZATION").get("client_id")
        


    # Generic function for headers of all http requests sent to twitch URIs. Returns dict, needs to be submitted to http requests as **kwargs instead of being passed directly.
    def get_http_request_headers(self, incl_content_type:"bool" = False) -> dict:

        with json.load(open(TOKENS, "r")) as tokens:
            print(tokens)

            if incl_content_type:
                return {'Authorization': tokens["token"],
                    'Client-Id': self.client_id,
                    'Content-Type': 'application/json'
                    }
            
            return {
                'Authorization': tokens["token"],
                'Client-Id': self.client_id
                }
        


    # Generic function to obtain a twitch user's ID number based on their login username - i.e. what is used to log into Twitch, also displayed on a streamer's channel.
    def get_user_id(self, username:"str") -> str:

        res = requests.get(f"{_TWITCH_URI.USERS.value}?login={username}", headers=self.get_http_request_headers())
        
        if res.status_code == 200:
            return res.json()["data"][0]["id"]

        else:
            raise Exception(f"Request failed; received status code {res.status_code} with error {res.text}")

