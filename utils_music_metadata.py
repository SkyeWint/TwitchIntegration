import asyncio
import hashlib
import numpy


from connection_http_requests import HTTP_Requests
from connection_obs_websocket import OBS_WS_Connection

METADATA_FILENAME = "D:\\Streaming\\foobar2k_now_playing.txt"
SONGNAME_FILENAME = "D:\\Streaming\\current_song_name.txt"
ARTISTS_FILENAME = "D:\\Streaming\\current_song_artists.txt"
SOURCE_FILENAME = "D:\\Streaming\\current_song_source.txt"
COPYRIGHT_FILENAME = "D:\\Streaming\\current_song_copyright.txt"



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
            # Writes current song's name.
            with open(SONGNAME_FILENAME, 'w') as file:
                song_name = self.current_metadata[0]
                file.write(song_name)


            await asyncio.sleep(0) # Breakpoint to allow other async functions to run.


            # Writes current song's artists.
            with open(ARTISTS_FILENAME, 'w') as file:
                song_artists = self.current_metadata[1]
                file.write(song_artists)


            await asyncio.sleep(0) # Breakpoint to allow other async functions to run.


            # Writes current song's source.
            with open(SOURCE_FILENAME, 'w') as file:
                song_source = self.current_metadata[2]
                file.write(song_source)


            await asyncio.sleep(0) # Breakpoint to allow other async functions to run.


            # Writes current song's copyright.
            with open(COPYRIGHT_FILENAME, 'w') as file:
                song_copyright = self.current_metadata[3]
                file.write(song_copyright)


            await asyncio.sleep(2)


            # Causes metadata for each field to scroll if needed.
            if len(song_name.strip()) > 18:
                await self._obs_ws.update_music_metadata_scroll("Song Name", int(numpy.clip((len(song_name.strip()) * 9), 170, 350)))
            else:
                await self._obs_ws.update_music_metadata_scroll("Song Name", 0)

            if len(song_artists.strip()) > 18:
                await self._obs_ws.update_music_metadata_scroll("Song Artists", int(numpy.clip((len(song_name.strip()) * 9), 170, 350)))
            else:
                await self._obs_ws.update_music_metadata_scroll("Song Artists", 0)

            if len(song_source.strip()) > 18:
                await self._obs_ws.update_music_metadata_scroll("Song Source", int(numpy.clip((len(song_name.strip()) * 9), 170, 350)))
            else:
                await self._obs_ws.update_music_metadata_scroll("Song Source", 0)

        
        except Exception as e:
            print(f"Failed to write song information to new file. Current metadata is: {self.current_metadata}")
            print(f"Encountered exception: \n{e}")

        


        


    ##### Public functions

    async def terminate_module(self) -> None:
        self._running = False


    async def update(self) -> None:
        
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
                    



if __name__ == "__main__":


    manager = Metadata_Manager()

    print(manager.metadata_hash)

    asyncio.run(manager.update())