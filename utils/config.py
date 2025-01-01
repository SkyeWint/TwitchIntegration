import os
import configparser
import time
import random


#CONFIG_FILENAME = os.path.join(os.pardir, 'config.ini')
CONFIG_FILENAME = '.\\config.ini'


# Gets a specific section of the config file.
def get_config(section:"str") -> dict:
    config = configparser.ConfigParser()
    config.read(CONFIG_FILENAME)
    try:
        return dict(config.items(section))
    except:
        print("\n!! Config file invalid !!\n")
        print(f"Attempted to get {section} from {config} but cannot read section.")
        generate_config()


# Verifies if config.ini is present in the program folder and that it has the fields necessary.
# If config.ini is not present or has incorrect contents, runs generate_config() from config_generator.py
# Otherwise, if config.ini is present, confirms if user wants to generate a new config or if it is fine.
def validate_config_file() -> None:
    try:
        config = configparser.ConfigParser()

        if not os.path.isfile(CONFIG_FILENAME):
            raise Exception("Config file does not exist.")
        
        print("Checking headers...")
        time.sleep(random.uniform(0.2,0.4))

        config.read(CONFIG_FILENAME)

        # Verify section headers.
        sections = config.sections()
        if sections != [
            "AUTHORIZATION", 
            "TOKEN REQUEST",
            "STREAM INFO"
            ]:
            raise Exception("Config headers incorrect.")
        
        print("Validating section keys...")
        time.sleep(random.uniform(0.2,0.6))

        # Defining required keys and any required values.
        placeholder_sections = [
                {
                "response_type": "code", 
                "client_id": None, 
                "redirect_uri": None, 
                "scope": None, 
                "force_verify": None
                },

                {
                "client_id": None, 
                "client_secret": None, 
                "grant_type": "authorization_code", 
                "redirect_uri": None
                },

                {
                "login_name": None,
                "tts_reward_title": None
                }
            ]
        
        
        # Replace section headers in list with their corresponding section dicts, then validate section keys.
        for i, section in enumerate(sections):
            sections[i] = dict(config.items(section))
            
            if sections[i].keys() != placeholder_sections[i].keys():
                raise Exception("Keys incorrect.")
            for k, v in sections[i].items():
                if v != placeholder_sections[i].get(k) and placeholder_sections[i].get(k) != None:
                    raise Exception(f"Static value for key {k} is incorrect.")

    except Exception as e:
        print(str(e) + "\n")
        generate_config()
    
    else:
        print("Existing config file is valid. If issues occur during auth, delete the config.ini file and try again.")


# Generates new config file if there are any issues with the existing config file.
def generate_config() -> None:

    print("Generating new config file...")

    print("\nPlease input your application Client ID from https://dev.twitch.tv/console.")
    id = input()

    print('\nPlease input your application Client Secret from https://dev.twitch.tv/console.')
    secret = input()

    print('\nPlease input the login name for the Twitch account you are livestreaming from.')
    login_name = input()

    print('\nIf you plan to use the Text To Speech part of this code, please input the title of your TTS point redemption.')
    tts_reward_title = input()

    print('\nPlease input your application Redirect URI from https://dev.twitch.tv/console.')
    print('Press Enter without any input for the default of http://localhost/.')
    print('Make sure it matches your twitch.tv dev console before continuing.')
    uri = input()
    if uri == "":
        uri = "http://localhost/"

    print('\nPlease input your desired scope.')
    print('If you do not know your intended scope, press Enter without any input for the default scope.')
    scope = input()
    if scope == "":
        scope = "channel:manage:redemptions moderator:manage:banned_users user:read:chat user:write:chat user:bot channel:manage:predictions bits:read channel:read:charity"
    
    print('\nDo you want to force verification? y/[n]')
    print('Forced verification requires clicking "authorize" after logging into Twitch to authenticate this program.')
    force_verify = input()
    if force_verify == "y":
        force_verify = "true"
    else:
        force_verify = "false"

    # After requesting input on all optional fields, build the config file.
    config = configparser.RawConfigParser()

    config['AUTHORIZATION'] = {
        'response_type': 'code',
        'client_id': id,
        'redirect_uri': uri,
        'scope': scope,
        'force_verify': force_verify
        }

    config['TOKEN REQUEST'] = {
        'client_id': id,
        'client_secret': secret,
        'grant_type': 'authorization_code',
        'redirect_uri': uri
        }

    config['STREAM INFO'] = {
        'login_name': login_name,
        'tts_reward_title': tts_reward_title
        }

    with open(CONFIG_FILENAME, 'w') as configFile:
        config.write(configFile)

    print("\nconfig.ini has been generated. Press Enter to close the program.")
    input()
    exit()


if __name__ == "__main__":
    generate_config()