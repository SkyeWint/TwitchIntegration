import os
import configparser
import time
import random


CONFIG_FILENAME = 'config.ini'


# Gets a specific section of the config file.
def get_config(section:"str") -> dict:
    config = configparser.ConfigParser()
    config.read(CONFIG_FILENAME)
    return dict(config.items(section))


# Verifies if config.ini is present in the program folder and that it has the fields necessary.
# Retuns True if config.ini present and has all necessary fields. Otherwise returns False.
def validate_config_file() -> bool:

    valid = True
    config = configparser.ConfigParser()

    if not os.path.isfile(CONFIG_FILENAME):
        print("ERROR: Config file does not exist.")
        return not valid

    config.read(CONFIG_FILENAME)

    # Verify section headers.
    sections = config.sections()
    if sections != [
        "INITIALIZATION"
        ]:
        print("ERROR: Config headers incorrect.")
        return not valid
    
    time.sleep(random.uniform(0.2,0.6))

    # Defining required keys and any required values.
    placeholder_sections = [
            {
                'client_id': None,
                'client_secret': None,
                'scope': None,
                'login_name': None,
                'obs_ws_password': None
            }
    ]
    
    
    # Replace section headers in list with their corresponding section dicts, then validate section keys.
    for i, section in enumerate(sections):
        sections[i] = dict(config.items(section))
        
        if sections[i].keys() != placeholder_sections[i].keys():
            print("ERROR: Config keys incorrect.")
            return not valid
    
    return valid


# Generates new config file if there are any issues with the existing config file.
def generate_config() -> None:

    print("Generating new config file...")

    print("\nPlease input your application Client ID from https://dev.twitch.tv/console.")
    id = input()

    print('\nPlease input your application Client Secret from https://dev.twitch.tv/console.')
    secret = input()

    print('\nPlease input the login name for the Twitch account you are livestreaming from.')
    login_name = input()

    print('\nPlease input the password for your OBS Websocket Server, if you are using OBS websockets for any reason.')
    print('\nThis can be located under OBS -> Tools -> Websocket Server Settings -> Show Connect Info.')
    obs_ws_password = input()

    print('\nPlease input your desired scope.')
    print('If you do not know your intended scope, press Enter without any input for the default scope.')
    print('Scope definitions are found under the python Twitch API package\'s Type Definitions page.')
    print('If you aren\'t editing this program\'s code directly, you should just use the default scope.')
    scope = input()
    if scope == "":
        scope = "CHANNEL_MANAGE_REDEMPTIONS MODERATOR_MANAGE_BANNED_USERS USER_READ_CHAT USER_WRITE_CHAT CHANNEL_BOT CHANNEL_MANAGE_PREDICTIONS BITS_READ CHANNEL_READ_CHARITY CHANNEL_EDIT_COMMERCIAL MODERATOR_MANAGE_ANNOUNCEMENTS MODERATOR_MANAGE_SHOUTOUTS"

    # After requesting input on all optional fields, build the config file.
    config = configparser.RawConfigParser()

    config['INITIALIZATION'] = {
        'client_id': id,
        'client_secret': secret,
        'scope': scope,
        'login_name': login_name,
        'obs_ws_password': obs_ws_password
        }

    with open(CONFIG_FILENAME, 'w') as configFile:
        config.write(configFile)

    if __name__ == "__main__":
        print("\nconfig.ini has been generated. Press Enter to close the program.")
        input()
        exit()
    else:
        print("\nconfig.ini has been generated. Press Enter to continue.")
        input()
        return



if __name__ == "__main__":
    generate_config()