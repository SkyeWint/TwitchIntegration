import requests
import json
import time
from enum import Enum
import websockets
from websockets.asyncio.client import connect

from utils.config import get_config
from utils.message_parsing import parse_message
from web_connections.subscriptions import Subscription_Data
from web_connections.subscriptions import RequestType

# Used for function annotation. Not required at runtime.
from web_connections.auth import Auth



######### Enum List #########

class _TWITCH_URI(Enum):
    
    SUBSCRIPTION = "https://api.twitch.tv/helix/eventsub/subscriptions"
    WEBSOCKET = "wss://eventsub.wss.twitch.tv/ws"
    USERS = "https://api.twitch.tv/helix/users"



##### Websocket_Connection handles listening to the websocket connection to Twitch as well as handling the initial subscriptions to 

class Websocket_Connection(object):
    def __init__(self, http_requests:"HTTP_Requests") -> None:

        # See the HTTP_Requests class in this module for details.
        self._http_requests = http_requests

        # Functions to deal with incoming websocket messages are assigned to this list.
        self._message_handlers = []

        # Connection-related variables.
        self._running = True
        self._timeout_limit = time.monotonic()
        self._websocket = None


    ##### Connection-related functions

    # Establishes a websocket connection with Twitch in order to receive EventSub notifications, required for interactivity with Twitch. 
    # All functions other than get_http_request_headers() and get_user_id() WILL NOT WORK if this has not been called first.
    async def connect(self) -> None:

        # Automatically reconnects if transient disconnections occur, with exponential backoff.
        async with connect(_TWITCH_URI.WEBSOCKET.value, additional_headers = self._http_requests.get_http_request_headers()) as self._websocket:
            try: 

                msg = await self._websocket.recv()
                msg = parse_message(msg)
                if msg.message_type() != "session_welcome":
                    raise Exception(f"First message must be welcome message, got {msg.type} instead.")
                
                self._session_id = msg._payload.session.id
                self._timeout_period = msg._payload.session.keepalive_timeout_seconds
                self._timeout_limit = time.monotonic() + self._timeout_period

                print("Handshake with server successful, now subscribing to events..")


                self._subscribe_to_all_events()
                print("Event subscriptions successful, message receiver loop will now begin...")


                self._running = True
                while self._running:
                    msg = await self._websocket.recv() # This point in the function allows other concurrent functions to run while it waits for a new message via the websocket.

                    msg = parse_message(msg)

                    for subscriber in self._message_handlers:
                        await subscriber(msg)


            except websockets.exceptions.ConnectionClosed:
                self._websocket = None
        


    # Waits for the websocket to close properly. Should only be called when the program is ending.
    async def close_connection(self) -> None:
        self._running = False
        await self._websocket.close()
        self._websocket = None
        print("Connection closed.")

        return



    # Must be run periodically to verify that the websocket connection has not timed out. The reconnect() function should be called if this function returns False.
    def check_if_timed_out(self) -> bool:
        if self._websocket != None and time.monotonic() > self._timeout_limit:
            return True
        else:
            return False


    # Alters the current timeout limit. Should only be called by a message handler function if a Notification or KeepAlive message is received.
    def reset_timeout_limit(self) -> None:
        self._timeout_limit = time.monotonic() + self._timeout_period



    # Adds a function to the message handler list. Functions used as arguments MUST take Message or SubscriptionMessage objects as arguments. 
    # See message_parsing.py for details about Message and SubscriptionMessage objects.
    def add_message_handler(self, handler_function:"function") -> None:
        self._message_handlers.append(handler_function)
    


    ##### Other functions

    def get_session_id(self) -> str:
        return self._session_id

    
    # Used to reduce clutter and improve readability in connect(). Should only be called within Websocket_Connection.
    def _subscribe_to_all_events(self) -> None:

        
        subscription_data = Subscription_Data(self._session_id, self._http_requests.get_user_id(get_config("STREAM INFO").get("login_name"))) #TODO: Change hardcoded username to be set in config.cfg.

        # See subscriptions.py for information about RequestType and Subscription_Data.
        for type in RequestType:
            self._http_requests.subscribe_to_event(subscription_data, type)


        


##### HTTP_Requests handles all HTTP requests for 

class HTTP_Requests(object):
    def __init__(self, auth:"Auth") -> None:

        # Auth is stored in init and kept for get_http_request_headers() as it should only be acquired once per program runtime. See auth.py for details about the Auth object.
        self._auth = auth


    # Generic function for headers of all http requests sent to twitch URIs. Returns dict, needs to be submitted to http requests as **kwargs instead of being passed directly.
    def get_http_request_headers(self, incl_content_type:"bool" = False) -> dict:

        if incl_content_type:
            return {'Authorization': self._auth.get_bearer_token(),
                'Client-Id': self._auth.client_id,
                'Content-Type': 'application/json'
                }
        
        return {
            'Authorization': self._auth.get_bearer_token(),
            'Client-Id': self._auth.client_id
            }


    # Generic function to obtain a twitch user's ID number based on their login username - i.e. what is used to log into Twitch, also displayed on a streamer's channel.
    def get_user_id(self, username:"str") -> str:

        res = requests.get(f"{_TWITCH_URI.USERS.value}?login={username}", headers=self.get_http_request_headers())
        
        if res.status_code == 200:
            return res.json()["data"][0]["id"]
        
        elif res.status_code == 401:
            print("Invalid OAuth token. Requesting new bearer token and attempting to get user ID again.")
            self._auth.refresh_access_token()
            return self.get_user_id(username)

        else:
            raise Exception(f"Request failed; received status code {res.status_code} with error {res.text}")


    # Generic function to subscribe to a Twitch EventSub. Necessary in order to receive event notifications for the specified subscription type.
    def subscribe_to_event(self, subscription_data:"Subscription_Data", sub_type:"str") -> None:

        res = requests.post(_TWITCH_URI.SUBSCRIPTION.value, headers={
                **self.get_http_request_headers(incl_content_type = True),
            }, 
            data=json.dumps(subscription_data.get_subscription_data(sub_type)))
        
        if res.status_code == 401: 
            print("Invalid OAuth token. Requesting new bearer token and attempting subscription request again.")
            self._auth.refresh_access_token()
            self.subscribe_to_event(subscription_data, sub_type)

        elif res.status_code != 202:
            raise Exception(f"Subscription request not accepted; received status code {res.status_code} with error {res.text}")