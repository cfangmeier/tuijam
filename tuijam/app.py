#!/usr/bin/env python3
# coding=utf-8
from os.path import join, isfile
from os import makedirs
import sys

import urwid
import gmusicapi
import logging
import yaml

from .lastfm import LastFMAPI
from .music_objects import (
    Song,
    Album,
    Artist,
    Situation,
    RadioStation,
    Playlist,
    YTVideo,
)
from .music_objects import serialize, deserialize
from .ui import SearchInput, SearchPanel, QueuePanel, PlayBar
from tuijam import CONFIG_DIR, CONFIG_FILE, QUEUE_FILE, HISTORY_FILE, CRED_FILE
from tuijam.utility import lookup_keys


class App(urwid.Pile):

    palette = [
        ("header", "", "", "", "#FFF,underline", ""),
        ("header_bg", "", "", "", "#FFF", ""),
        ("line", "", "", "", "#FFF", ""),
        ("search normal", "", "", "", "#FFF", ""),
        ("search select", "", "", "", "#FFF", "#D32"),
        ("region_bg normal", "", "", "", "#888", ""),
        ("region_bg select", "", "", "", "#FFF", ""),
        ("progress", "", "", "", "#FFF", "#D32"),
        ("progress_remaining", "", "", "", "#FFF", "#444"),
    ]

    def __init__(self):
        import mpv

        self.player = mpv.MPV()
        self.player.volume = 100
        self.player["vid"] = "no"
        self.volume = 8
        self.g_api = None
        self.loop = None
        self.config_pw = None
        self.reached_end_of_track = False
        self.lastfm = None
        self.youtube = None
        self.mpris = None
        self.vim = None
        self.vim_insert = False


        @self.player.event_callback("end_file")
        def end_file_callback(event):

            if event["event"]["reason"] == 0:

                self.reached_end_of_track = True
                if self.lastfm:
                    self.current_song.lastfm_scrobbled = False
                self.schedule_refresh(dt=0.01)

        self.search_panel = SearchPanel(self)
        search_panel_wrapped = urwid.LineBox(self.search_panel, title="Search Results")

        # Give search panel reference to LineBox to change the title dynamically
        self.search_panel.line_box = search_panel_wrapped

        search_panel_wrapped = urwid.AttrMap(
            search_panel_wrapped, "region_bg normal", "region_bg select"
        )
        self.search_panel_wrapped = search_panel_wrapped

        self.playbar = PlayBar(
            self, "progress_remaining", "progress", current=0, done=100
        )

        self.queue_panel = QueuePanel(self)
        queue_panel_wrapped = urwid.LineBox(self.queue_panel, title="Queue")

        queue_panel_wrapped = urwid.AttrMap(
            queue_panel_wrapped, "region_bg normal", "region_bg select"
        )
        self.queue_panel_wrapped = queue_panel_wrapped

        self.search_input = urwid.Edit("> ", multiline=False)
        self.search_input = SearchInput(self)

        urwid.Pile.__init__(
            self,
            [
                ("weight", 12, search_panel_wrapped),
                ("pack", self.playbar),
                ("weight", 7, queue_panel_wrapped),
                ("pack", self.search_input),
            ],
        )

        self.set_focus(self.search_input)

        self.play_state = "stop"
        self.current_song = None
        self.history = []

    def login(self):
        self.g_api = gmusicapi.Mobileclient(debug_logging=False)
        self.load_config()

        if not isfile(CRED_FILE):
            from oauth2client.client import FlowExchangeError
            print("No local credentials file found.")
            print("TUIJam will now open a browser window so you can provide")
            print("permission for TUIJam to access your Google Play Music account.")
            input("Press enter to continue.")
            try:
                self.g_api.perform_oauth(CRED_FILE, open_browser=True)
            except FlowExchangeError:
                raise RuntimeError('Oauth authentication Failed.')

        self.g_api.oauth_login(self.g_api.FROM_MAC_ADDRESS, CRED_FILE)

        if self.lastfm_sk is not None:
            self.lastfm = LastFMAPI(self.lastfm_sk)
            # TODO handle if sk is invalid

        from apiclient.discovery import build
        developer_key, = lookup_keys("GOOGLE_DEVELOPER_KEY")
        self.youtube = build("youtube", "v3", developerKey=developer_key)

    def load_config(self):
        if not isfile(CONFIG_FILE):
            self.write_default_config()

        with open(CONFIG_FILE) as f:
            config = yaml.safe_load(f.read())

            self.lastfm_sk = config.get("lastfm_sk", None)

            self.mpris_enabled = config.get("mpris_enabled", True)
            self.persist_queue = config.get("persist_queue", True)
            self.reverse_scrolling = config.get("reverse_scrolling", False)
            self.video = config.get("video", False)
            self.vim = config.get("vim", False)


    @staticmethod
    def write_default_config():
        cfg = {}
        cfg["mpris_enabled"] = True
        cfg["persist_queue"] = True
        cfg["reverse_scrolling"] = False
        cfg["video"] = False
        cfg["vim"] = False

        with open(CONFIG_FILE, "w") as outfile:
            yaml.safe_dump(cfg, outfile, default_flow_style=False)

    def refresh(self, *args, **kwargs):
        if self.play_state == "play" and self.reached_end_of_track:
            self.reached_end_of_track = False
            self.queue_panel.play_next()

        self.playbar.update()
        self.loop.draw_screen()

        if self.play_state == "play":
            self.schedule_refresh()

    def schedule_refresh(self, dt=0.5):
        self.loop.set_alarm_in(dt, self.refresh)

    def play(self, song):
        try:
            if isinstance(song, Song):
                song.stream_url = self.g_api.get_stream_url(song.id)
            else:  # YTVideo
                song.stream_url = f"https://youtu.be/{song.id}"
        except Exception as e:
            logging.exception(e)
            return False

        self.current_song = song
        self.player.pause = True
        self.player.play(self.current_song.stream_url)
        self.player.pause = False
        self.play_state = "play"
        self.playbar.update()
        self.history.insert(0, song)
        self.history = self.history[:100]
        self.schedule_refresh()

        if self.mpris:
            self.mpris.emit_property_changed("PlaybackStatus")
            self.mpris.emit_property_changed("Metadata")
        return True

    def stop(self):
        try:
            self.player.pause = True
            self.player.seek(0, reference="absolute")
        except SystemError:  # seek throws error if there is no current song in mpv
            pass

        self.play_state = "stop"
        self.playbar.update()

        if self.mpris:
            self.mpris.emit_property_changed("PlaybackStatus")

    def seek(self, dt):
        try:
            self.player.seek(dt)
        except SystemError:
            pass

        self.playbar.update()

    def toggle_play(self):
        if self.play_state == "play":
            self.player.pause = True
            self.play_state = "pause"
            self.playbar.update()

        elif self.play_state == "pause" or (
            self.play_state == "stop" and self.current_song is not None
        ):
            self.player.pause = False
            self.play_state = "play"
            self.playbar.update()
            self.schedule_refresh()

        elif self.play_state == "stop":
            self.queue_panel.play_next()

        if self.mpris:
            self.mpris.emit_property_changed("PlaybackStatus")

    def volume_down(self):
        self.volume = max([0, self.volume - 1])
        self.player.volume = int(self.volume * 100 / 8)
        self.playbar.update()

        if self.mpris:
            self.mpris.emit_property_changed("Volume")

    def volume_up(self):
        self.volume = min([8, self.volume + 1])
        self.player.volume = int(self.volume * 100 / 8)
        self.playbar.update()

        if self.mpris:
            self.mpris.emit_property_changed("Volume")

    def keypress(self, size, key):
        vim_insert_cache = self.vim_insert
        if key == "tab":
            current_focus = self.focus
            if current_focus == self.search_panel_wrapped:
                self.set_focus(self.queue_panel_wrapped)
            elif current_focus == self.queue_panel_wrapped:
                self.set_focus(self.search_input)
            else:
                self.set_focus(self.search_panel_wrapped)
        elif key == "shift tab":
            current_focus = self.focus
            if current_focus == self.search_panel_wrapped:
                self.set_focus(self.search_input)
            elif current_focus == self.queue_panel_wrapped:
                self.set_focus(self.search_panel_wrapped)
            else:
                self.set_focus(self.queue_panel_wrapped)
        elif self.focus != self.search_input:
            if key == ">":
                self.seek(10)
            elif key == "<":
                self.seek(-10)
            elif key in "-_":
                self.volume_down()
            elif key in "+=":
                self.volume_up()
            elif key in ("/", "ctrl f"):
                if self.vim:
                    self.vim_insert = True
                self.set_focus(self.search_input)

        if self.vim and key == "esc":
            self.vim_insert = False

        if self.vim and not vim_insert_cache:
            if key == "p":
                self.toggle_play()
            elif key == "k":
                self.stop()
            elif key == "n":
                self.queue_panel.play_next()
            elif key == "r":
                hist_songs = [item for item in self.history if isinstance(item, Song)]
                hist_yt = [item for item in self.history if isinstance(item, YTVideo)]
                self.search_panel.view_previous_songs(hist_songs, hist_yt)
            elif key == "s":
                self.queue_panel.shuffle()
            elif key == "shift t":
                self.rate_current_song(5)
            elif key == "t":
                self.rate_current_song(1)
            elif key == "w":
                self.queue_panel.clear()
            elif key == "q":
                self.queue_panel.add_songs_to_queue(self.search_panel.search_results.songs)
            elif key == "i":
                self.vim_insert = True
        elif not self.vim:
            if key == "ctrl p":
                self.toggle_play()
            elif key == "ctrl k":
                self.stop()
            elif key == "ctrl n":
                self.queue_panel.play_next()
            elif key == "ctrl r":
                hist_songs = [item for item in self.history if isinstance(item, Song)]
                hist_yt = [item for item in self.history if isinstance(item, YTVideo)]
                self.search_panel.view_previous_songs(hist_songs, hist_yt)
            elif key == "ctrl s":
                self.queue_panel.shuffle()
            elif key == "ctrl u":
                self.rate_current_song(5)
            elif key == "ctrl d":
                self.rate_current_song(1)
            elif key == "ctrl w":
                self.queue_panel.clear()
            elif key == "ctrl q":
                self.queue_panel.add_songs_to_queue(self.search_panel.search_results.songs)

        # Only pass through keys dedicated to UI in vim mode
        if not self.vim or vim_insert_cache or \
            key in ("Q", "q", "e", "enter", "r", "R", "j", "k"):
            return self.focus.keypress(size, key)


    def mouse_event(self, size, event, button, col, row, focus=True):
        up, down = [("up", "down"), ("down", "up")][self.reverse_scrolling]
        if button == 5:
            self.keypress(size, up)
        elif button == 4:
            self.keypress(size, down)
        else:
            super().mouse_event(size, event, button, col, row, focus=focus)

    def expand(self, obj):
        if obj is None:
            return

        songs = []
        albums = []
        artists = []
        situations = []
        radio_stations = []
        playlists = []
        yt_vids = []

        if isinstance(obj, Song):
            album_info = self.g_api.get_album_info(obj.albumId)

            songs = [Song.from_dict(track) for track in album_info["tracks"]]
            albums = [Album.from_dict(album_info)]
            artists = [Artist(obj.artist, obj.artistId)]

        elif isinstance(obj, Album):
            album_info = self.g_api.get_album_info(obj.id)

            songs = [Song.from_dict(track) for track in album_info["tracks"]]
            albums = [obj]
            artists = [Artist(obj.artist, obj.artistId)]

        elif isinstance(obj, Artist):
            artist_info = self.g_api.get_artist_info(obj.id)

            songs = [Song.from_dict(track) for track in artist_info["topTracks"]]
            albums = [Album.from_dict(album) for album in artist_info.get("albums", [])]
            artists = [
                Artist.from_dict(artist) for artist in artist_info["related_artists"]
            ]
            artists.insert(0, obj)

        elif isinstance(obj, Situation):
            radio_stations = obj.stations
            situations = [obj]

        elif isinstance(obj, RadioStation):
            station_id = obj.get_station_id(self.g_api)
            songs = self.get_radio_songs(station_id)
            radio_stations = [obj]

        elif isinstance(obj, Playlist):
            songs = obj.songs
            playlists = [obj]

        elif isinstance(obj, YTVideo):
            yt_vids = [obj]

        self.search_panel.update_search_results(
            songs, albums, artists, situations, radio_stations, playlists, yt_vids
        )

    def youtube_search(
        self,
        q,
        max_results=50,
        order="relevance",
        token=None,
        location=None,
        location_radius=None,
    ):
        """
        Mostly stolen from: https://github.com/spnichol/youtube_tutorial/blob/master/youtube_videos.py
        """

        search_response = (
            self.youtube.search()
            .list(
                q=q,
                type="video",
                pageToken=token,
                order=order,
                part="id,snippet",
                maxResults=max_results,
                location=location,
                locationRadius=location_radius,
            )
            .execute()
        )

        videos = []
        for search_result in search_response.get("items", []):

            if search_result["id"]["kind"] == "youtube#video":
                videos.append(search_result)

        nexttok = search_response.get("nextPageToken", None)
        return nexttok, videos

    def search(self, query):

        results = self.g_api.search(query)

        songs = [Song.from_dict(hit["track"]) for hit in results["song_hits"]]
        albums = [Album.from_dict(hit["album"]) for hit in results["album_hits"]]
        artists = [Artist.from_dict(hit["artist"]) for hit in results["artist_hits"]]
        ytvids = [YTVideo.from_dict(hit) for hit in self.youtube_search(query)[1]]

        self.search_panel.update_search_results(
            songs, albums, artists, [], [], [], ytvids
        )
        self.set_focus(self.search_panel_wrapped)

    def listen_now(self):

        situations = self.g_api.get_listen_now_situations()
        items = self.g_api.get_listen_now_items()
        playlists = self.g_api.get_all_user_playlist_contents()
        liked = self.g_api.get_top_songs()

        situations = [Situation.from_dict(hit) for hit in situations]
        albums = [Album.from_dict(hit["album"]) for hit in items if "album" in hit]
        radio_stations = [
            RadioStation.from_dict(hit["radio_station"])
            for hit in items
            if "radio_station" in hit
        ]
        playlists = [Playlist.from_dict(playlist) for playlist in playlists]

        liked = [Song.from_dict(song) for song in liked]
        playlists.append(Playlist("Liked", liked, None))

        self.search_panel.update_search_results(
            [], albums, [], situations, radio_stations, playlists, []
        )
        self.set_focus(self.search_panel_wrapped)

    def create_radio_station(self, obj):

        if isinstance(obj, Song):
            station_id = self.g_api.create_station(obj.title, track_id=obj.id)

        elif isinstance(obj, Album):
            station_id = self.g_api.create_station(obj.title, album_id=obj.id)

        elif isinstance(obj, Artist):
            station_id = self.g_api.create_station(obj.name, artist_id=obj.id)

        elif isinstance(obj, RadioStation):
            station_id = obj.get_station_id(self.g_api)

        else:
            return

        for song in self.get_radio_songs(station_id):
            self.queue_panel.add_song_to_queue(song)

    def get_radio_songs(self, station_id, n=50):

        song_dicts = self.g_api.get_station_tracks(station_id, num_tracks=n)
        return [Song.from_dict(song_dict) for song_dict in song_dicts]

    def rate_current_song(self, rating):

        if type(self.current_song) != Song:
            return

        if self.current_song.rating == rating:
            rating = 0

        self.current_song.rating = rating
        track = {}

        if self.current_song.type == "library":
            track["id"] = self.current_song.id

        else:
            track["nid"] = self.current_song.id
            track["trackType"] = self.current_song.trackType

        self.g_api.rate_songs(track, rating)
        self.playbar.update()
        self.loop.draw_screen()

    def cleanup(self, *args, **kwargs):

        self.player.quit()
        del self.player

        self.g_api.logout()
        self.loop.stop()

        if self.persist_queue:
            self.save_queue()

        self.save_history()
        sys.exit()

    def save_queue(self):
        print("saving queue")
        queue = []

        if self.current_song is not None:
            queue.append(self.current_song)

        queue.extend(self.queue_panel.queue)

        with open(QUEUE_FILE, "w") as f:
            f.write(serialize(queue))

    def restore_queue(self):
        try:
            with open(QUEUE_FILE, "r") as f:
                self.queue_panel.add_songs_to_queue(deserialize(f.read()))

        except (AttributeError, FileNotFoundError) as e:
            logging.exception(e)
            print("failed to restore queue. :(")
            self.queue_panel.clear()

    def save_history(self):
        with open(HISTORY_FILE, "w") as f:
            f.write(serialize(self.history))

    def restore_history(self):
        try:
            with open(HISTORY_FILE, "r") as f:
                self.history = deserialize(f.read())
        except (AttributeError, FileNotFoundError) as e:
            logging.exception(e)
            print("failed to restore recently played. :(")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        "TUIJam", description="A fancy TUI client for Google Play Music."
    )
    parser.add_argument(
        "action", choices=["", "configure_last_fm"], default="", nargs="?"
    )
    parser.add_argument("-v", "--verbose", action="store_true")  # TODO: use this
    args = parser.parse_args()

    print("starting up.")
    makedirs(CONFIG_DIR, exist_ok=True)

    log_file = join(CONFIG_DIR, "log.txt")
    logging.basicConfig(filename=log_file, filemode="w", level=logging.WARNING)

    if args.action == "configure_last_fm":
        LastFMAPI.configure()
        exit(0)
    elif args.action != "":
        print(f"Unrecognized option: {args.action}")
        exit(0)

    app = App()
    print("logging in.")
    app.login()

    if app.mpris_enabled:
        from .mpris import setup_mpris

        print("enabling external control.")
        app.mpris = setup_mpris(app)
        if not app.mpris:
            print("Failed.")

    if app.persist_queue:
        print("restoring queue")
        app.restore_queue()

    print("restoring history")
    app.restore_history()

    if app.video:
        app.player["vid"] = "auto"

    import signal
    signal.signal(signal.SIGINT, app.cleanup)

    loop = urwid.MainLoop(app, palette=app.palette, event_loop=urwid.GLibEventLoop())
    app.loop = loop
    loop.screen.set_terminal_properties(256)

    try:
        loop.run()
    except Exception as e:
        logging.exception(e)
        print(
            "Something bad happened! :( see log file ($HOME/.config/tuijam/log.txt) for more information."
        )
        app.cleanup()


if __name__ == "__main__":
    main()
