import asyncio

from enum import Enum

from twitch_api import Twitch_Connection

from utils_config import validate_config_file
from utils_hotkey_manager import Hotkey_Manager
from mode_minigolf import Minigolf_Manager
from audiomodule_audio_player import Audio_Manager
from audiomodule_sound_effects import Sound_Manager
from audiomodule_TTS import TTS_Manager



######### Script Init & General Variables #########

class MSG_TYPE(Enum):
    
    NOTIFICATION = "notification"
    SESSION_KEEPALIVE = "session_keepalive"
    SESSION_RECONNECT = "session_reconnect"
    REVOCATION = "revocation"



######### Private Functions #########

game_options = [
    "Minigolf"
]



class Integration(object):
    def __init__(self):
        # Initializes websocket connection.
        

        self.hotkey_manager = Hotkey_Manager()

        # Sets up kill switch.
        self.running = True
        self.hotkey_manager.create_hotkey("Terminate Program", "right ctrl+right shift+backspace", self._stop_running, force_assignment = True)

        self.module_list = self.get_module_list()

        # Used to create a reference to all async functions run as concurrent tasks, to prevent python's garbage collector from killing them mid-execution.
        self.tasks = set()

        
    async def main(self) -> None:
        
        self.twitch_connection = Twitch_Connection(self.module_list)
        await self.twitch_connection.initialize_twitch()

        # Adds all selected stream module update() functions and websocket connection to Task Manager to execute in concurrent loops. Maintains in a loop until self.tg no longer has tasks to manage.
        async with asyncio.TaskGroup() as self.tg:

            kill_switch = self.tg.create_task(self.kill_switch())
            self.tasks.add(kill_switch)
            kill_switch.add_done_callback(self.tasks.discard)

            for module in self.module_list:
                if callable(getattr(module, "update", None)):
                    update_task = self.tg.create_task(module.update())
                    self.tasks.add(update_task)
                    update_task.add_done_callback(self.tasks.discard)

            connection_task = self.tg.create_task(self.twitch_connection.run())
            self.tasks.add(connection_task)
            connection_task.add_done_callback(self.tasks.discard)


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

        self.twitch_connection.stop_running()


        print("All tasks should be terminated now. Closing program.")


    # Requests input on list of modules to run in the integration program, initializes them, then returns the list.
    def get_module_list(self) -> list:
        
        
        module_list = []

        print("Would you like sound effects enabled during this stream? y/n   [Default: y]")
        if input() != "n":
            audio_manager = Audio_Manager()
            module_list.append(audio_manager)
            module_list.append(Sound_Manager(audio_manager))

        print("Would you like Text to Speech enabled during this stream? y/n   [Default: y]")
        if input() != "n":
            try:
                module_list.append(TTS_Manager(self.hotkey_manager, audio_manager))
            except:
                module_list.append(TTS_Manager(self.hotkey_manager, Audio_Manager()))

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
                    case "Minigolf":
                        module_list.append(Minigolf_Manager(self.hotkey_manager))

        except:
            print("\nNo game selected.\n")

        # Prints all relevant hotkeys to the session.
        print("Hotkeys are: ")

        for k, v in self.hotkey_manager.get_hotkey_dict().items():
            print('{:<20}  |  {:<25}'.format(k,v))

        print("")
        
        return module_list



##### Run code

if __name__ == "__main__":

    print("Welcome to SkyeWint's Twitch Integration program!\n")

    validate_config_file()

    program = Integration()

    # Initiates main loop after other initialization is complete.
    asyncio.run(program.main())