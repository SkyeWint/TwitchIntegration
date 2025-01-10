import time
import random

from utils.config import validate_config_file
from utils.hotkey_manager import Hotkey_Manager
from stream_modules.stream_minigolf import Minigolf_Manager
from audio_modules.audio_player import Audio_Manager
from audio_modules.stream_sound_effects import Sound_Manager
from audio_modules.stream_TTS import TTS_Manager
from main import Integration


game_options = [
    "Rain World",
    "Minigolf"
]



# Requests input on list of modules to run in the integration program, initializes them, then returns the list.
def get_module_list() -> list:
    
    hotkey_manager = Hotkey_Manager()
    module_list = []

    print("Would you like sound effects enabled during this stream? y/n   [Default: y]")
    if input() != "n":
        audio_manager = Audio_Manager()
        module_list.append(audio_manager)
        module_list.append(Sound_Manager(audio_manager))

    print("Would you like Text to Speech enabled during this stream? y/n   [Default: y]")
    if input() != "n":
        try:
            module_list.append(TTS_Manager(hotkey_manager, audio_manager))
        except:
            module_list.append(TTS_Manager(hotkey_manager, Audio_Manager()))

    print("Select the game you are playing from the following options:")
    print("1: None [Default]")
    for i, game in enumerate(game_options):
        print(f"{str(i + 2)}: {game}")

    try:
        selection = int(input()) - 2
        if selection < 0 or selection >= len(game_options):
            raise Exception("No game selected.")
        else:
            match game_options[selection]:
                case "Rain World":
                    module_list.append(Rain_World_Manager(hotkey_manager))
                case "Minigolf":
                    module_list.append(Minigolf_Manager(hotkey_manager))

    except:
        print("\nNo game selected.\n")

    # Prints all relevant hotkeys to the session.
    print("Hotkeys are: ")
    print('{:<20}  |  {:<25}'.format("End Program","ctrl+shift+backspace"))

    for k, v in hotkey_manager.get_hotkey_dict().items():
        print('{:<20}  |  {:<25}'.format(k,v))

    print("")
    
    return module_list



if __name__ == "__main__":
    print("Checking if config is valid...")

    time.sleep(random.uniform(0.2,0.4)) # Makes it feel more like the program is doing something instead of having it happen near-instantly.

    validate_config_file()

    print("\n")
    
    program = Integration(get_module_list())
