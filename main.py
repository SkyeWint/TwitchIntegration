import keyboard
import asyncio
import time

from enum import Enum

from web_connections.auth import get_auth
from web_connections.client_server_connections import Websocket_Connection, HTTP_Requests

# Used for function annotation. Not required at runtime.
from utils.message_parsing import Message



######### Script Init & General Variables #########

class MSG_TYPE(Enum):
    
    NOTIFICATION = "notification"
    SESSION_KEEPALIVE = "session_keepalive"
    SESSION_RECONNECT = "session_reconnect"
    REVOCATION = "revocation"



######### Private Functions #########

class Integration(object):
    def __init__(self, module_list:"list"):
        # Initializes websocket connection.
        auth = get_auth()
        self.http_requests = HTTP_Requests(auth)
        self.websocket_connection = Websocket_Connection(self.http_requests)
        self.websocket_connection.add_message_handler(self.message_handler)

        print(module_list)

        self.module_list = module_list

        # Initiates main loop after other initialization is complete.
        asyncio.run(self.main())

    async def main(self) -> None:
        
        

        # Used to create a reference to all async functions run as concurrent tasks, to prevent python's garbage collector from killing them mid-execution.
        tasks = set()

        # Adds all selected stream module update() functions and websocket connection to Task Manager to execute in concurrent loops.
        async with asyncio.TaskGroup() as tg:

            escape_task = tg.create_task(self.background_loop())
            tasks.add(escape_task)
            escape_task.add_done_callback(tasks.discard)    


            for module in self.module_list:
                if callable(getattr(module, "update", None)):
                    update_task = tg.create_task(module.update())
                    tasks.add(update_task)
                    update_task.add_done_callback(tasks.discard)


            # Adding websocket connection to Twitch after setting up updates.
            connection_task = tg.create_task(self.websocket_connection.connect())
            tasks.add(connection_task)
            connection_task.add_done_callback(tasks.discard)

        exit()


    # Monitors for a key combination of shift + enter + backspace to close the program. Cannot be called directly from create_hotkey due to async functions within it.
    async def background_loop(self) -> None:

        start_time = time.monotonic()
        running = True
        while running:
            if keyboard.is_pressed("shift+enter+backspace"):
                await self.end_program()
                break

            if int(time.monotonic() - start_time) % 1 == 0:
                # Only checks if the websocket connection has timed out every second instead of every 0.05 seconds.
                if self.websocket_connection.check_if_timed_out():
                    self.websocket_connection.reconnect()

            await asyncio.sleep(0.05)
        

    # Closes program gracefully.
    async def end_program(self) -> None:

        print("Terminating tasks.")
        # Closes out existing tasks gracefully instead of terminating them mid-execution.
        await self.websocket_connection.close_connection()

        for module in self.module_list:
            if callable(getattr(module, "terminate_module", None)):
                await module.terminate_module()

        print("All tasks should be terminated now. Closing program.")




    ######### Event Handler Functions #########
    # Should only be added to handler lists.

    # Sorts parsed messages from the websocket connection based on type.
    async def message_handler(self, msg:"Message") -> None:

        # Primary message type received from 
        if msg.message_type() == MSG_TYPE.NOTIFICATION.value:
            self.websocket_connection.reset_timeout_limit()
            for module in self.module_list:
                if callable(getattr(module, "handle_notification", None)):
                    await module.handle_notification(msg)
            #print(f"DEBUG: received {msg.message_type()} message for {msg.subscription_type()}")
            

        elif msg.message_type() == MSG_TYPE.SESSION_KEEPALIVE.value:
            self.websocket_connection.reset_timeout_limit()
            #print(f"DEBUG: received {msg.message_type()}")

        elif msg.message_type() == MSG_TYPE.SESSION_RECONNECT.value:
            self.websocket_connection.reconnect()
            #print(f"DEBUG: received {msg.message_type()}")
        
        elif msg.message_type() == MSG_TYPE.REVOCATION.value:
            raise Exception(f"Yo dude ur {msg.subscription_type()} version {msg.subscription_version()} broke, here's why: {msg.subscription_status()} \nCmon, you can fix it. Five minute coding adventure.")
        
        else:
            raise Exception(f"Unexpected message type: {msg.message_id()}")

