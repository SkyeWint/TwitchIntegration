import asyncio

from enum import Enum

from connection_twitch_api import Twitch_Connection
from connection_http_requests import HTTP_Requests
from connection_obs_websocket import OBS_WS_Connection

from utils_config import validate_config_file, generate_config
from utils_hotkey_manager import Hotkey_Manager
from utils_music_metadata import Metadata_Manager
from utils_general_twitch_functions import General_Twitch_Functions
from stream_module_minigolf import Minigolf_Manager
from stream_module_rainworld import Rain_World_Manager
from audio_module_audio_player import Audio_Manager
from audio_module_sound_effects import Sound_Manager
from audio_module_TTS import TTS_Manager



######### Script Init & General Variables #########

class MSG_TYPE(Enum):
    
    NOTIFICATION = "notification"
    SESSION_KEEPALIVE = "session_keepalive"
    SESSION_RECONNECT = "session_reconnect"
    REVOCATION = "revocation"



######### Private Functions #########

game_options = [
    "Minigolf",
    "Rain World"
]



class Integration(object):
    def __init__(self) -> None:
        # Initializes websocket connection.
        
        self.hotkey_manager = Hotkey_Manager()
        self.http_requests = HTTP_Requests()
        self.obs_websocket = OBS_WS_Connection(self.http_requests)

        # Sets up kill switch.
        self.running = True
        self.hotkey_manager.create_hotkey("Terminate Program", "right ctrl+right shift+backspace", self._stop_running, force_assignment = True)

        self.module_list = self.get_module_list()

        # Used to create a reference to all async functions run as concurrent tasks, to prevent python's garbage collector from killing them mid-execution.
        self.tasks = set()

        
    async def main(self) -> None:
        
        self.twitch_connection = Twitch_Connection(self.module_list)
        await self.twitch_connection.initialize_twitch()
        
        await self.obs_websocket.init_connection()

        self.http_requests.init_user_id()

        self.http_requests.send_chat_announcement("The integration code is now connected and running! TTS, sound effects, and other fun things should (hopefully) now work! skyewiGormsip")

        # Adds all selected stream module update() functions and websocket connection to Task Manager to execute in concurrent loops. Maintains in a loop until self.tg no longer has tasks to manage.
        #try:

        async with asyncio.TaskGroup() as self.tg:

            kill_switch = self.tg.create_task(self.kill_switch())
            self.tasks.add(kill_switch)
            kill_switch.add_done_callback(self.tasks.discard)

            connection_task = self.tg.create_task(self.twitch_connection.run())
            self.tasks.add(connection_task)
            connection_task.add_done_callback(self.tasks.discard)

            for module in self.module_list:
                if callable(getattr(module, "update", None)):
                    update_task = self.tg.create_task(module.update())
                    self.tasks.add(update_task)
                    update_task.add_done_callback(self.tasks.discard)

        #except Exception as e:

            #print(f"Encountered exception {e}")

            #self.http_requests.send_chat_message("Something went wrong! Please tell Skye to check the exception log! skyewiPlank")

        exit()


    # Only to be called by hotkey. Tells the program to stop running, obviously.
    def _stop_running(self) -> None:

        print("Program shutdown initiated. Please wait for program to shut down...")
        self.running = False
        

    # Closes program gracefully once program is told to stop running.
    async def kill_switch(self) -> None:
        
        # Perpetually sleeps until hotkey is pressed to stop the program from continuing to run, then shuts down the program.
        while self.running:
            await asyncio.sleep(2)


        print("Terminating list of running tasks.")
        # Closes out existing tasks gracefully instead of terminating them mid-execution.

        for module in self.module_list:
            if callable(getattr(module, "terminate_module", None)):
                await module.terminate_module()

        self.http_requests.send_chat_announcement("The integration code is no longer running! skyewiGerald")

        print("Terminating connection to Twitch...")
        self.twitch_connection.stop_running()

        print("Terminating connection to OBS...")
        await self.obs_websocket.terminate_module()

        print("All tasks should be terminated now. Closing program.")

        exit()


    # Requests input on list of modules to run in the integration program, initializes them, then returns the list.
    def get_module_list(self) -> list:
        
        
        module_list = []

        metadata_manager = Metadata_Manager(self.http_requests, self.obs_websocket)
        general_twitch_functions = General_Twitch_Functions(self.http_requests)

        audio_manager = None

        module_list.append(metadata_manager)
        module_list.append(general_twitch_functions)
        

        print("Would you like sound effects enabled during this stream? y/n   [Default: y]")
        if input() != "n":

            # Creates audio output window for OBS if necessary.
            if audio_manager == None:
                audio_manager = Audio_Manager("Integration Audio Output")
                module_list.append(audio_manager)

            module_list.append(Sound_Manager(audio_manager, self.http_requests))

        print("Would you like Text to Speech enabled during this stream? y/n   [Default: y]")
        if input() != "n":
            
            # Creates audio output window for OBS if necessary.
            if audio_manager == None:
                audio_manager = Audio_Manager("Integration Audio Output")
                module_list.append(audio_manager)

            module_list.append(TTS_Manager(self.hotkey_manager, audio_manager, self.http_requests, self.obs_websocket))

        print("Pick the integration mode from the following options:")
        print("1: None. [Default]")
        for i, game in enumerate(game_options):
            print(f"{str(i + 2)}: {game}")

        try:
            selection = int(input()) - 2
            if selection < 0 or selection >= len(game_options):
                raise Exception("No game selected.")
            else:
                match game_options[selection]:
                    case "Minigolf":
                        print("\nMinigolf selected.\n")
                        module_list.append(Minigolf_Manager(self.hotkey_manager, self.http_requests))

                match game_options[selection]:
                    case "Rain World":
                        print("\nRain World selected.\n")
                        module_list.append(Rain_World_Manager(self.hotkey_manager, audio_manager, self.http_requests))

        except:
            print("\nNo game selected.\n")

        # Prints all relevant hotkeys to the session.
        print("Hotkeys are: ")

        for k, v in self.hotkey_manager.get_hotkey_dict().items():
            print('{:<50}  |  {:<50}'.format(k,v))

        print("")
        
        return module_list



##### Run code

if __name__ == "__main__":

    print("Welcome to SkyeWint's Twitch Integration program!\n")

    # Validates config file and forces regeneration if it is invalid.
    if validate_config_file() == False:
        generate_config()

    program = Integration()

    # Initiates main loop after other initialization is complete.
    asyncio.run(program.main())