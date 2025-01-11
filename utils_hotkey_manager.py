import keyboard


#### Used for creating specific sets of hotkeys in individual modules without overlap.

class Hotkey_Manager(object):
    def __init__(self) -> None:

        self._hotkey_dict = {}

    def create_hotkey(self, hotkey_name:"str", hotkey_keys:"str", func:"function", force_assignment:"bool" = False, *args) -> bool:
        
        successful_assignment = True


        if hotkey_name in [k for k in self._hotkey_dict.keys()]:
            print(f"{hotkey_name} is already the name of a hotkey combination bound to the following keys: {self._hotkey_dict.get(hotkey_name)}")
            print("Hotkey names cannot be duplicates. Did you mean to create a hotkey with the same key combination uising 'force_assignment = True'?")
            return not successful_assignment

        elif (hotkey_keys in [v for v in self._hotkey_dict.values()] and not force_assignment):
            print("Duplicate hotkeys found, could not register the new hotkey combination!")
            print(f"Duplicate hotkeys are:")
            for k, v in self.get_hotkey_dict().items():
                if k == hotkey_name or v == hotkey_keys:
                    print('{:<20}  |  {:<25}'.format(k,v))
            print("\n'force_assignment' must be True when creating a hotkey to override this failsafe.")
            return not successful_assignment
        
        elif hotkey_keys in [v for v in self._hotkey_dict.values()] and force_assignment:
            print(f"Duplicate hotkeys found, forcing assignment anyway!!! {hotkey_keys} will perform both functions if pressed.")
            print(f"Duplicate hotkeys are:")
            for k, v in self.get_hotkey_dict().items():
                if k == hotkey_name or v == hotkey_keys:
                    print('{:<20}  |  {:<25}'.format(k,v))


        keyboard.add_hotkey(hotkey_keys, func, *args)
        if hotkey_name not in self._hotkey_dict.keys() or hotkey_keys != self._hotkey_dict.get(hotkey_name):
            self._hotkey_dict[hotkey_name] = hotkey_keys
        return successful_assignment
    

    def remove_hotkey(self, hotkey_name:"str") -> None:

        hotkey_keys = self._hotkey_dict.get(hotkey_name)
        keyboard.remove_hotkey(hotkey_keys)
        self._hotkey_dict.pop(hotkey_name)

    def remove_all_hotkeys(self) -> None:

        keyboard.remove_all_hotkeys()

    def get_hotkey_dict(self) -> dict:
        return self._hotkey_dict