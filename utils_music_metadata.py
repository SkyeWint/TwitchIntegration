import asyncio
import hashlib
import numpy


from connection_http_requests import HTTP_Requests
from connection_obs_websocket import OBS_WS_Connection


METADATA_FILENAME = "D:\\Streaming\\foobar2k_now_playing.txt"


class Metadata_Manager():
    def __init__(self, http_requests:"HTTP_Requests", obs_ws:"OBS_WS_Connection") -> None:

        self._http_requests = http_requests
        self._obs_ws = obs_ws

        with open(METADATA_FILENAME, "rb") as file:

            self.metadata_hash = hashlib.md5(file.read()).hexdigest()
            self.current_metadata = []


    async def split_metadata(self):

        # Opens metadata file from foobar.
        with open(METADATA_FILENAME, "r") as file:

            try: 
                metadata = file.readline()
            except:
                metadata = "Tell Skye ---This music ---Has an error ---Thanks"
            
            self.current_metadata = str(metadata).split("---")
        
        await asyncio.sleep(0) # Breakpoint to allow other async functions to run.
        
        try: 
            await self._obs_ws.update_text_detail("Current Song Name", self.current_metadata[0])
            await self._obs_ws.update_text_detail("Current Song Artists", self.current_metadata[1])
            await self._obs_ws.update_text_detail("Current Song Source", self.current_metadata[2])
            await self._obs_ws.update_text_detail("Current Song Copyright", self.current_metadata[3][1:])


            await asyncio.sleep(0) # Breakpoint to allow other async functions to run.


            # Causes metadata for each field to scroll if needed.
            if len(self.current_metadata[0].strip()) > 18:
                await self._obs_ws.update_music_metadata_scroll("Current Song Name", int(numpy.clip((len(self.current_metadata[0].strip()) * 9), 170, 350)))
            else:
                await self._obs_ws.update_music_metadata_scroll("Current Song Name", 0)

            if len(self.current_metadata[1].strip()) > 18:
                await self._obs_ws.update_music_metadata_scroll("Current Song Artists", int(numpy.clip((len(self.current_metadata[1].strip()) * 9), 170, 350)))
            else:
                await self._obs_ws.update_music_metadata_scroll("Current Song Artists", 0)

            if len(self.current_metadata[2].strip()) > 18:
                await self._obs_ws.update_music_metadata_scroll("Current Song Source", int(numpy.clip((len(self.current_metadata[2].strip()) * 9), 170, 350)))
            else:
                await self._obs_ws.update_music_metadata_scroll("Current Song Source", 0)

        
        except Exception as e:
            print(f"Failed to write song information to new file. Current metadata is: {self.current_metadata}")
            print(f"Encountered exception: \n{e}")



    ##### Public functions

    async def terminate_module(self) -> None:
        self._running = False

        print("Music metadata splitter utility has terminated.")


    async def update(self) -> None:
        
        await self.split_metadata()

        self._running = True
        while self._running:
            await asyncio.sleep(1)
            
            with open(METADATA_FILENAME, "rb") as file:

                current_hash = hashlib.md5(file.read()).hexdigest() 
                if current_hash == self.metadata_hash:
                    continue
                    

                else:
                    self.metadata_hash = current_hash

            await self.split_metadata()
                    


## Test code

if __name__ == "__main__":

    manager = Metadata_Manager()

    print(manager.metadata_hash)

    asyncio.run(manager.update())