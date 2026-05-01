import simpleobsws
import asyncio
import json

from utils_config import get_config

# Used for function annotation. Not required at runtime.
from connection_http_requests import HTTP_Requests


class OBS_WS_Connection(object):
    def __init__(self, http_requests:"HTTP_Requests") -> None:
        self._obs_ws = simpleobsws.WebSocketClient(url = "ws://127.0.0.1:4455", password = get_config("INITIALIZATION").get("obs_ws_password"))
        self._http_requests = http_requests


    # Initializes connection to OBS. Returns True if it successfully initializes, 
    async def init_connection(self) -> bool:
        try:
            await self._obs_ws.connect()
            await self._obs_ws.wait_until_identified()

        except Exception as e:
            print("Exception occurred during OBS websocket initialization:")
            print(e)
            return False

        print("Connected to OBS and identified, awaiting instructions.")

        # Test code

        await self.update_text_detail("Music today is from game", "Music is from\ngame today")

        return True
    

    # Causes a given TTS character to be moved on or off screen based on their name.
    async def tts_character_toggle(self, character_name:"str", active:"bool"):
        print("Toggling TTS character")

        # Identifies current filter settings.
        if active:
            # Moves character up.
            req = simpleobsws.Request("SetSourceFilterEnabled", {"sourceName": "TTS", "filterName": character_name + " TTS Static Part - Up", "filterEnabled": True})
            await self._obs_ws.call(req)
            req = simpleobsws.Request("SetSourceFilterEnabled", {"sourceName": "TTS", "filterName": character_name + " TTS Moving Part 1 - Up", "filterEnabled": True})
            await self._obs_ws.call(req)
            req = simpleobsws.Request("SetSourceFilterEnabled", {"sourceName": "TTS", "filterName": "TTS Character Label - Up", "filterEnabled": True})
            await self._obs_ws.call(req)
            req = simpleobsws.Request("SetSourceFilterEnabled", {"sourceName": "TTS", "filterName": "TTS Subtitles - Up", "filterEnabled": True})
            await self._obs_ws.call(req)

            await asyncio.sleep(0.3)

            # Enables audio-based movement of character's moving part. 
            # Must be enabled AFTER the move is complete (300ms) because it will snap the moving part of the character to the base coordinate without the move animation.
            req = simpleobsws.Request("SetSourceFilterEnabled", {"sourceName": "6- TTS Audio", "filterName": character_name + " TTS Audio Move 1", "filterEnabled": True})
            await self._obs_ws.call(req)
            req = simpleobsws.Request("SetSourceFilterEnabled", {"sourceName": "6- TTS Audio", "filterName": character_name + " TTS Audio Move 2", "filterEnabled": True})
            await self._obs_ws.call(req)

        else:
            # Disabled audio-based movement of head.
            # Must be disabled BEFORE the character is moved down because it will force the moving part of the character to stay at its base coordinate rather than traveling along with the rest of the character.
            req = simpleobsws.Request("SetSourceFilterEnabled", {"sourceName": "6- TTS Audio", "filterName": character_name + " TTS Audio Move 1", "filterEnabled": False})
            await self._obs_ws.call(req)
            req = simpleobsws.Request("SetSourceFilterEnabled", {"sourceName": "6- TTS Audio", "filterName": character_name + " TTS Audio Move 2", "filterEnabled": False})
            await self._obs_ws.call(req)

            # Moves character down.
            req = simpleobsws.Request("SetSourceFilterEnabled", {"sourceName": "TTS", "filterName": character_name + " TTS Static Part - Down", "filterEnabled": True})
            await self._obs_ws.call(req)
            req = simpleobsws.Request("SetSourceFilterEnabled", {"sourceName": "TTS", "filterName": character_name + " TTS Moving Part 1 - Down", "filterEnabled": True})
            await self._obs_ws.call(req)
            req = simpleobsws.Request("SetSourceFilterEnabled", {"sourceName": "TTS", "filterName": "TTS Character Label - Down", "filterEnabled": True})
            await self._obs_ws.call(req)
            req = simpleobsws.Request("SetSourceFilterEnabled", {"sourceName": "TTS", "filterName": "TTS Subtitles - Down", "filterEnabled": True})
            await self._obs_ws.call(req)


    # Updates the specified text source input in OBS to the specified text string.
    async def update_text_detail(self, input_name:"str", new_text:"str") -> bool:


        # Identifies current source settings.
        req = simpleobsws.Request("GetInputSettings", {"inputName": input_name})
        res = await self._obs_ws.call(req)

        if res.responseData["inputSettings"]["text"] == new_text:
            return
        
        inputSettings = res.responseData["inputSettings"]
        inputSettings["text"] = new_text

        req = simpleobsws.Request("SetInputSettings", {"inputName": input_name, "inputSettings": inputSettings})
        res = await self._obs_ws.call(req)


    # Updates the music metadata filters after the text is changed in the .txt file.
    async def update_music_metadata_scroll(self, source_name:"str", speed:"int") -> bool:


        # Identifies current filter settings.
        req = simpleobsws.Request("GetSourceFilter", {"sourceName": source_name, "filterName": "Scroll"})
        res = await self._obs_ws.call(req)

        if speed == 0 and res.responseData["filterEnabled"]:
            req = simpleobsws.Request("SetSourceFilterEnabled", {"sourceName": source_name, "filterName": "Scroll", "filterEnabled": False})
            await self._obs_ws.call(req)

        elif speed > 0 and not res.responseData["filterEnabled"]:

            await asyncio.sleep(2) # Awaits to introduce delay and allow start of text to be read.

            req = simpleobsws.Request("SetSourceFilterEnabled", {"sourceName": source_name, "filterName": "Scroll", "filterEnabled": True})
            await self._obs_ws.call(req)
            

        filter_settings = res.responseData["filterSettings"]


        # Ensures the filter settings are not the same to save on an unnecessary websocket call.
        if filter_settings["speed_x"] == speed:
            return

        filter_settings["speed_x"] = speed


        # Updates scroll speed.
        req = simpleobsws.Request("SetSourceFilterSettings", {"sourceName": source_name, "filterName": "Scroll", "filterSettings": filter_settings})
        res = await self._obs_ws.call(req)


    async def terminate_module(self) -> None:
        await self._obs_ws.disconnect()




if __name__ == "__main__":


    connection = OBS_WS_Connection(HTTP_Requests())

    asyncio.run(connection.init_connection())