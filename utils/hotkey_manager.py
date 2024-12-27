import keyboard


#### Used for creating specific sets of hotkeys in individual modules without overlap.

class Hotkey_Manager(object):
    def __init__(self):

        self._hotkey_dict = {}

    def create_hotkey(self, hotkey_name, hotkey_keys, func, force_assignment = False, *args):
        
        successful_assignment = True

        if hotkey_keys in [v for v in self._hotkey_dict.values()] and not force_assignment:
            print("Duplicate hotkeys found, could not register the new hotkey combination!")
            print(f"Duplicate hotkeys are: {str([k for k,v in self._hotkey_dict.items() if v == hotkey_keys])}")
            return not successful_assignment
        elif hotkey_keys in [v for v in self._hotkey_dict.values()] and force_assignment:
            print(f"Duplicate hotkeys found, forcing assignment anyway!!! {hotkey_keys} will perform both functions if pressed.")
            print(f"Duplicate hotkeys are: {str([k for k,v in self._hotkey_dict.items() if v == hotkey_keys])}")


        keyboard.add_hotkey(hotkey_keys, func, *args)
        self._hotkey_dict[hotkey_name] = hotkey_keys
        return successful_assignment
    

    def remove_hotkey(self, hotkey_name):

        hotkey_keys = self._hotkey_dict.get(hotkey_name)
        keyboard.remove_hotkey(hotkey_keys)
        self._hotkey_dict.pop(hotkey_name)

    def remove_all_hotkeys(self):

        keyboard.remove_all_hotkeys()

def test():
    hk = Hotkey_Manager()
    hk.create_hotkey("Test1", "backspace+enter", lambda: print("this is a hotkey!"))
    hk.create_hotkey("Test2", "backspace+enter", lambda: print("this is a hotkey!"), force_assignment=True)
    hk.create_hotkey("Test3", "backspace+enter", lambda: print("this is a hotkey!"))




#### For testing purposes only.

if __name__ == "__main__":
    test()