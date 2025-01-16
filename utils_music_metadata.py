import asyncio
import hashlib

METADATA_FILENAME = "D:\\Streaming\\foobar2k_now_playing.txt"
SONGNAME_FILENAME = "D:\\Streaming\\current_song_name.txt"
ARTISTS_FILENAME = "D:\\Streaming\\current_song_artists.txt"
SOURCE_FILENAME = "D:\\Streaming\\current_song_source.txt"
COPYRIGHT_FILENAME = "D:\\Streaming\\current_song_copyright.txt"



class Metadata_Manager():
    def __init__(self) -> None:
        with open(METADATA_FILENAME, "rb") as file:

            self.metadata_hash = hashlib.md5(file.read()).hexdigest()
            self.current_metadata = []


    def split_metadata(self):

        # Opens metadata file from foobar.
        with open(METADATA_FILENAME, "r") as file:

            metadata = file.readline()
            self.current_metadata = str(metadata).split("---")
        
        # Writes current song's name.
        with open(SONGNAME_FILENAME, 'w') as file:
            song_name = self.current_metadata[0]
            file.write(song_name)

        # Writes current song's artists.
        with open(ARTISTS_FILENAME, 'w') as file:
            song_artists = self.current_metadata[1]
            file.write(song_artists)

        # Writes current song's source.
        with open(SOURCE_FILENAME, 'w') as file:
            song_source = self.current_metadata[2]
            file.write(song_source)

        # Writes current song's copyright.
        with open(COPYRIGHT_FILENAME, 'w') as file:
            song_copyright = self.current_metadata[3]
            file.write(song_copyright)

        


        


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

            self.split_metadata()
                    



if __name__ == "__main__":


    manager = Metadata_Manager()

    print(manager.metadata_hash)

    asyncio.run(manager.update())