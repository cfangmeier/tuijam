import hashlib
import logging
from datetime import datetime

import requests
import yaml

from tuijam import __version__, CONFIG_DIR
from tuijam.utility import lookup_keys


class LastFMAPI:
    API_KEY = None
    API_SECRET = None
    API_ROOT_URL = "http://ws.audioscrobbler.com/2.0/"
    USER_AGENT = "TUIJam/" + __version__

    def __init__(self, sk=None):
        # Initialize session key with None
        self.sk = sk

        if LastFMAPI.API_KEY is None or LastFMAPI.API_SECRET is None:
            LastFMAPI.API_KEY, LastFMAPI.API_SECRET = lookup_keys(
                "LASTFM_API_KEY", "LASTFM_API_SECRET"
            )

    def call_method(self, method_name: str, params=None) -> dict:
        # Construct API request parameters dict
        if params is None:
            params = {}

        api_params = {"method": method_name, "api_key": LastFMAPI.API_KEY}
        api_params.update(params)

        # Construct api_sig (https://www.last.fm/api/desktopauth#6)
        m = hashlib.md5()
        for key in sorted(api_params.keys()):
            m.update((key.encode("utf-8") + str(api_params[key]).encode("utf-8")))
        m.update(LastFMAPI.API_SECRET.encode("utf-8"))

        # Add api_sig to the request parameters
        api_params.update({"api_sig": m.hexdigest()})

        # Last.fm API docs don't even say that you DON'T need to put it in api_sig.
        # Unlike other methods, auth.getToken works with it.
        # Shame on you, Last.fm!
        api_params.update({"format": "json"})

        r = requests.post(
            LastFMAPI.API_ROOT_URL,
            params=api_params,
            headers={"User-Agent": LastFMAPI.USER_AGENT},
        )
        return r.json()

    def get_token(self):
        token_response = self.call_method("auth.getToken")
        if not token_response.get("error"):
            return token_response.get("token")
        else:
            # TODO throw an exception?
            return None

    def get_auth_url(self, token):
        return "http://www.last.fm/api/auth/?api_key=%s&token=%s" % (
            LastFMAPI.API_KEY,
            token,
        )

    def auth_by_token(self, token):
        response = self.call_method("auth.getSession", {"token": token})
        logging.warning("LASTFM: auth_by_token: " + response.__str__())
        if response.get("error", False):
            return False
        self.sk = response.get("session").get("key")
        return True

    def update_now_playing(self, artist, track, album, duration):
        if self.sk is None:
            return
        response = self.call_method(
            "track.updateNowPlaying",
            {
                "artist": artist,
                "track": track,
                "album": album,
                "duration": duration,
                "sk": self.sk,
            },
        )
        logging.warning("LASTFM: updateNowPlaying: " + response.__str__())
        # TODO error handle

    def update_now_playing_song(self, song):
        try:
            self.update_now_playing(
                song.artist,
                song.title,
                song.album,
                song.length[1] * 60 + song.length[0],
            )
            song.lastfm_ts_start = int(datetime.now().timestamp())
            # ^ there could be a bug when tracks are scrobbled in the past or the future
            #   (depends on timezone)
        except Exception as e:
            logging.exception("LASTFM: updateNowPlaying: " + e.__str__())
            logging.error("LASTFM: updateNowPlaying: failed to update")

    def scrobble(self, artist, track, album, duration, ts_start):
        # See: https://www.last.fm/api/scrobbling#when-is-a-scrobble-a-scrobble
        # Minimum 30 seconds long + has been listened for min(50% of its length or 4 minutes)
        # See the scrobble method reference (https://www.last.fm/api/show/track.scrobble)
        if self.sk is None or duration < 30:
            return

        response = self.call_method(
            "track.scrobble",
            {
                "timestamp[0]": str(ts_start),
                "artist[0]": artist,
                "track[0]": track,
                "album[0]": album,
                "duration[0]": duration,
                "sk": self.sk,
            },
        )
        logging.warning("LASTFM: scrobble: response = " + response.__str__())

    def scrobble_song(self, song):
        try:
            self.scrobble(
                song.artist,
                song.title,
                song.album,
                song.length[1] * 60 + song.length[0],
                song.lastfm_ts_start,
            )
            song.lastfm_scrobbled = True
        except Exception as e:
            logging.exception("LASTFM: scrobble: " + e.__str__())
            logging.error("LASTFM: scrobble: failed to scrobble")

    @staticmethod
    def configure():
        from os.path import join, isfile
        from getpass import getpass

        config_file = join(CONFIG_DIR, "config.yaml")
        if not isfile(config_file):
            print("It seems that you haven't run tuijam yet.")
            print("Please run it first, then authorize to Last.fm.")
            return

        print("generating Last.fm authentication token")
        api = LastFMAPI()
        token = api.get_token()
        auth_url = api.get_auth_url(token)

        import webbrowser

        webbrowser.open_new_tab(auth_url)

        print()
        print(
            "Please open this link in your browser and authorize the app in case the window "
            "hasn't been opened automatically:"
        )
        print(auth_url)
        print()
        input("After that, press Enter to get your session key...")
        if not api.auth_by_token(token):
            print("Failed to get a session key. Have you authorized?")
        else:
            with open(config_file, "r+") as f:
                lastfm_sk = api.sk
                config = yaml.safe_load(f.read())
                if config.get("encrypted", False):

                    from scrypt import decrypt, encrypt

                    print("The config is encrypted, encrypting session key...")
                    config_pw = getpass("Enter tuijam config pw: ")
                    try:
                        decrypt(config["email"], config_pw, maxtime=20)
                        lastfm_sk = encrypt(lastfm_sk, config_pw, maxtime=0.5)
                    except Exception as e:
                        print(e)
                        print("Could not decrypt config file.")
                        exit(1)

                config.update({"lastfm_sk": lastfm_sk})
                f.seek(0)
                yaml.safe_dump(config, f, default_flow_style=False)
                f.truncate()
                f.close()
            print("Successfully authenticated.")
