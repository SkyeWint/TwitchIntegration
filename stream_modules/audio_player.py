import os
import asyncio
from pydub import AudioSegment

from pygame import mixer

from tkinter import *

class Audio_Manager():
    def __init__(self) -> None:

        mixer.init()

        # Sets up a dedicated channel for TTS messages. 
        mixer.set_reserved(1)
        self._TTS_channel = mixer.Channel(0)

        # Sets up tkinter window to send audio through.
        self._window = Tk()
        self._tk_label = Label(self._window, text="Stream audio player window.")
        self._tk_label.pack()


        self._audio_file_exts = [".wav", ".ogg"]
    
    # Converts the given .mp3 into a .wav file
    def _convert_mp3_to_wav(self, file_path) -> str:

        if os.path.isfile(file_path) and file_path[-4:] == ".mp3":
            pass
        else:
            print(f"{file_path} does not lead to a valid mp3 file. Only mp3 files can be converted.")
            return ""

        sound = AudioSegment.from_mp3(file_path)
        sound.export(file_path[:-4] + ".wav", format="wav")
        
        return file_path[:-4] + ".wav"

    # Plays a sound with the given file path.
    def play_sound(self, file_path) -> None:
    

        if os.path.isfile(file_path) and file_path[-4:] in self._audio_file_exts:
            pass
        elif os.path.isfile(file_path) and file_path[-4:] == ".mp3":
            # Converts from mp3 to wav if needed.
            file_path = self._convert_mp3_to_wav(file_path)
        else:
            print(f"{file_path} does not lead to a playable audio file. Please make sure the audio file has an extension from the following list: {self._audio_file_exts}")
            return
        
        sound = mixer.Sound(file_path)

        sound.play()



    # This function is awaited until TTS is no longer playing, in order to allow deletion of TTS file after playing.
    async def play_TTS(self, file_path) -> None:


        if os.path.isfile(file_path) and file_path[-4:] in self._audio_file_exts:
            pass
        elif os.path.isfile(file_path) and file_path[-4:] == ".mp3":
            # Converts from mp3 to wav if needed.
            file_path = self._convert_mp3_to_wav(file_path)

            # Deletes previous mp3 file in order to allow a new TTS file to be generated, if generated TTS file is mp3 format.
            os.remove(file_path[:-4] + ".mp3")

        else:
            print(f"{file_path} does not lead to a playable audio file. Please make sure the audio file has an extension from the following list: {self._audio_file_exts}")
            return
        
        TTS = mixer.Sound(file_path)

        self._TTS_channel.play(TTS)

        while self._TTS_channel.get_busy():
            await asyncio.sleep(0.7) # Provides other concurrent functions time to run while TTS messages are being played.

        # Removes tts after it plays, in order to allow a new TTS file to be generated
        os.remove(file_path)
        return
    
    # Skips the current TTS message being played.
    def skip_TTS(self):
        self._TTS_channel.stop()

    # Closes tkinter window properly. 
    async def terminate_module(self) -> None:
        self._window.quit()

    # Maintains tkinter window.
    async def update(self) -> None:
        print("Updating tkinter window")
        self._window.update()
        await asyncio.sleep(0.05)