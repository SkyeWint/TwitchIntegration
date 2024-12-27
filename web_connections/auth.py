import requests
import secrets
from urllib.parse import urldefrag
from urllib.parse import urlsplit
from urllib.parse import parse_qsl
import webbrowser
from config import get_config

# Used for function annotation. Not required at runtime.
from auth import Auth


######### General Variables #########

OAUTH_AUTHORIZE_URL = "https://id.twitch.tv/oauth2/authorize"
OAUTH_TOKEN_URL = "https://id.twitch.tv/oauth2/token"

OAUTH_CODE = None



######### Public Functions #########

def get_auth() -> Auth:
    state = _get_auth_code()
    OAUTH_CODE = _extract_oauth_code(state)

    token_request_dict = get_config("TOKEN REQUEST")

    token_request_dict['code'] = OAUTH_CODE
    
    res = requests.post(OAUTH_TOKEN_URL, data=token_request_dict)
    if res.status_code == 200:
        res_body = res.json()
        if res_body['token_type'] != "bearer":
            raise Exception(f"Unexpected token type: {res_body['token_type']} != \"bearer\"")
        return Auth(res_body['access_token'], res_body['refresh_token'], res_body['scope'], token_request_dict.get("client_id"), token_request_dict.get("client_secret"))

    else:
        raise Exception("Failed auth request.")
    


######### Private Classes #########

class Auth(object):
    def __init__(self, access_token:"str", refresh_token:"str", scope:"str", client_id:"str", client_secret:"str") -> None:
        self.access_token = access_token
        self._refresh_token = refresh_token
        self.scope = scope
        self.client_id = client_id
        self.client_secret = client_secret
    
    
    def refresh_access_token(self) -> None:
        res = requests.post(OAUTH_TOKEN_URL, data={
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self._refresh_token
        })

        
        if res.status_code == 200:
            res_body = res.json()
            if res_body['token_type'] != "bearer":
                raise Exception(f"Unexpected token type: {res_body['token_type']} != \"bearer\"")
            self.access_token = res_body['access_token']
            self._refresh_token = res_body['refresh_token']

    def get_bearer_token(self) -> str:
        return "Bearer " + str(self.access_token)
    


######### Private Functions #########


def _get_auth_code() -> str:

    authorization_dict = get_config("AUTHORIZATION")
    authorization_dict['state'] = secrets.token_hex()

    res = requests.get(OAUTH_AUTHORIZE_URL, params=authorization_dict)

    webbrowser.open(res.url)

    return authorization_dict.get('state')


def _extract_oauth_code(state) -> str:

    res_dict = {}
    while res_dict == {}:
        res = input("Paste the resulting URL from the authorization request here. Press Enter without inputting anything to close the program. \nURL: ")
        if res == "":
            exit()
        res_dict = dict(parse_qsl(urlsplit(res).query))
        if res_dict == {}:
            print("Unable to extract information from provided input. Please try again.")

    if res_dict.get('state') != state:
        print(res_dict.get('state') + " vs " + state)
        print("Response state does not match generated state. Application will be closed due to a potential CSRF attack attempt. Press Enter to close the application.")
        input()
        exit()

    elif 'error' in res_dict.keys():
        print(res_dict.get('error') + ": " + res_dict.get('error_description') + "\nClosing program.")
        exit()
    else:
        return res_dict.get('code')


