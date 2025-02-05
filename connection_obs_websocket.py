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


        return True
    

    # Updates the music metadata filters after the text is changed in the .txt file.
    async def update_music_metadata_scroll(self, source_name:"str", speed:"int") -> bool:

        # Identifies scene item ID based on source name. Must be in Music Metadata scene.
        req = simpleobsws.Request("GetSceneItemId", {"sceneName": "Music Metadata", "sourceName": source_name})
        res = await self._obs_ws.call(req)

        itemId = res.responseData["sceneItemId"]

        # Identifies scene item source's Uuid based on item Id.
        req = simpleobsws.Request("GetSceneItemSource", {"sceneName": "Music Metadata", "sceneItemId": itemId})
        res = await self._obs_ws.call(req)

        sourceUuid = res.responseData["sourceUuid"]

        # Identifies current filter settings.
        req = simpleobsws.Request("GetSourceFilter", {"sourceUuid": sourceUuid, "filterName": "Scroll"})
        res = await self._obs_ws.call(req)

        if speed == 0 and res.responseData["filterEnabled"]:
            req = simpleobsws.Request("SetSourceFilterEnabled", {"sourceUuid": sourceUuid, "filterName": "Scroll", "filterEnabled": False})
            await self._obs_ws.call(req)

        elif not res.responseData["filterEnabled"]:
            req = simpleobsws.Request("SetSourceFilterEnabled", {"sourceUuid": sourceUuid, "filterName": "Scroll", "filterEnabled": True})
            await self._obs_ws.call(req)

        filterSettings = res.responseData["filterSettings"]

        # Ensures the filter settings are not the same to save on an unnecessary websocket call.
        if filterSettings["speed_x"] == speed:
            return

        filterSettings["speed_x"] = speed


        # Updates scroll speed.
        req = simpleobsws.Request("SetSourceFilterSettings", {"sourceUuid": sourceUuid, "filterName": "Scroll", "filterSettings": filterSettings})
        res = await self._obs_ws.call(req)



        




    

if __name__ == "__main__":

    connection = OBS_WS_Connection(HTTP_Requests())

    asyncio.run(connection.init_connection())