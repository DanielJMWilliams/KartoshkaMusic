import datetime
import json

import requests
from decouple import config
import base64


class SpotifyAuth():
    access_token = None
    refresh_token = None
    expiry_time=None

    code = None
    auth = None

    def __init__(self, code=None, access_token=None, refresh_token=None, expiry_time=None):
        #if allows us to have two different constructors
        if code!=None:
            #print("code constructor")
            self.code = code
            self.access_token=None
            self.refresh_token=None
            self.expiry_time=None
            self.auth=None
            self.getAccessToken()
        elif access_token!=None and refresh_token!=None and expiry_time!=None:
            #print("token constructor")
            self.access_token=access_token
            self.refresh_token=refresh_token
            self.expiry_time=self.stringToDateTime(expiry_time)

    def stringToDateTime(self, string):
        # time = "2020-06-05 16:30:34.392897"
        return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%S.%f')
    
    def getAuth(self):
        accessToken=self.getAccessToken()
        return "Bearer " + accessToken

    def getAccessToken(self):
        now = datetime.datetime.now()

        # Return current access token if still valid
        if self.expiry_time is not None and self.expiry_time > now:
            print("Token still valid, expires:", self.expiry_time)
            return self.access_token

        # Set up headers for token requests
        headers = {
            "Authorization": "Basic " + base64.b64encode(
                f"{config('SPOTIFY_CLIENT_ID')}:{config('SPOTIFY_CLIENT_SECRET')}".encode()
            ).decode("utf-8"),
            "content-type": "application/x-www-form-urlencoded",
        }

        # Initialize payload
        payload = {
            "redirect_uri": config("SPOTIFY_REDIRECT_URI"),
        }

        # Check whether to use authorization_code or refresh_token flow
        if self.expiry_time is None or self.refresh_token is None:
            if self.code is None:
                raise ValueError("No code or refresh token available to fetch a new access token.")
            payload["grant_type"] = "authorization_code"
            payload["code"] = self.code
            print("Using authorization code to fetch token.")
        else:
            payload["grant_type"] = "refresh_token"
            payload["refresh_token"] = self.refresh_token
            print(f"Token expired at {self.expiry_time}, using refresh token to fetch a new one.")

        try:
            # Request a new token
            response = requests.post("https://accounts.spotify.com/api/token", data=payload, headers=headers)

            if response.status_code != 200:
                print("Error response:", response.text)
                raise Exception(f"Failed to fetch new token. Status code: {response.status_code}. Error: {response.text}")

            res_json = response.json()
            print("Obtained new token, response:", res_json)

            # Update the token details
            self.expiry_time = self.calculateExpiryTime(res_json["expires_in"])
            self.access_token = res_json["access_token"]
            self.refresh_token = res_json.get("refresh_token", self.refresh_token)  # Keep old refresh token if not updated
            self.code = None  # Clear the authorization code as it’s not reusable

            return self.access_token

        except requests.RequestException as e:
            print(f"Request to Spotify API failed: {e}")
            raise


    def getRefreshToken(self):
        return self.refresh_token
        
    def getexpiryTime(self):
        return self.expiry_time

    def toJSON(self):
        d = {
            "access_token" : self.access_token,
            "refresh_token" : self.refresh_token,
            "expiry_time": str(self.expiry_time),
        }
        return json.dumps(d)
        #expiry_time is a datetime object so must be serialized...

    def calculateExpiryTime(self, secondsUntilexpiry):
        now = datetime.datetime.now()
        expiryTime = now + datetime.timedelta(seconds=secondsUntilexpiry)
        return expiryTime