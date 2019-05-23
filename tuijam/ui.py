import logging

import urwid

from .music_objects import (
    Song,
    Artist,
    YTVideo,
    Album,
    Situation,
    RadioStation,
    Playlist,
)
from .utility import sec_to_min_sec

WELCOME = """
   ▄             ▀       ▀               
 ▄▄█▄▄  ▄   ▄  ▄▄▄     ▄▄▄    ▄▄▄   ▄▄▄▄▄
   █    █   █    █       █   ▀   █  █ █ █
   █    █   █    █       █   ▄▀▀▀█  █ █ █
   ▀▄▄  ▀▄▄▀█  ▄▄█▄▄     █   ▀▄▄▀█  █ █ █
                         █               
                       ▀▀                
         - A Google Music Player -       
"""  # noqa

RATE_UI = {
    0: "-",  # No rating
    1: "▼",  # Thumbs down
    2: "▼",  # Legacy
    3: "-",  # Legacy
    4: "▲",  # Legacy
    5: "▲",  # Thumbs up
}


class SearchInput(urwid.Edit):
    def __init__(self, app):
        self.app = app
        super().__init__("search > ", multiline=False, allow_tab=False)

    def keypress(self, size, key):
        if key == "enter":
            txt = self.edit_text
            if txt:
                self.set_edit_text("")
                self.app.search(txt)
            else:
                self.app.listen_now()
        else:
            size = (size[0],)
            return super().keypress(size, key)


class SearchPanel(urwid.ListBox):
    class SearchResults:
        def __init__(self, categories):
            self.artists = []
            self.albums = []
            self.songs = []
            self.situations = []
            self.radio_stations = []
            self.playlists = []
            self.yt_vids = []
            for category in categories:
                if not category:
                    continue
                if isinstance(category[0], Artist):
                    self.artists = category
                elif isinstance(category[0], Album):
                    self.albums = category
                elif isinstance(category[0], Song):
                    self.songs = category
                elif isinstance(category[0], Situation):
                    self.situations = category
                elif isinstance(category[0], RadioStation):
                    self.radio_stations = category
                elif isinstance(category[0], Playlist):
                    self.playlists = category
                elif isinstance(category[0], YTVideo):
                    self.yt_vids = category

        def __iter__(self):
            yield self.artists
            yield self.albums
            yield self.songs
            yield self.situations
            yield self.radio_stations
            yield self.playlists
            yield self.yt_vids

    def __init__(self, app):
        self.app = app
        self.walker = urwid.SimpleFocusListWalker([])
        self.search_history = []
        self.search_results = self.SearchResults([])
        self.line_box = None
        self.viewing_previous_songs = False

        super().__init__(self.walker)

        self.walker.append(urwid.Text(WELCOME, align="center"))

    def keypress(self, size, key):
        if key == "q" or key == "Q":

            add_to_front = key == "Q"
            selected = self.selected_search_obj()

            if not selected:
                return

            if isinstance(selected, (Song, YTVideo)):
                self.app.queue_panel.add_song_to_queue(selected, add_to_front)
            elif type(selected) == Album:
                self.app.queue_panel.add_album_to_queue(selected, add_to_front)
            elif type(selected) == RadioStation:
                radio_song_list = self.app.get_radio_songs(
                    selected.get_station_id(self.app.g_api)
                )

                if add_to_front:
                    radio_song_list = reversed(radio_song_list)

                for song in radio_song_list:
                    self.app.queue_panel.add_song_to_queue(song, add_to_front)
            elif type(selected) == Playlist:
                self.app.queue_panel.add_songs_to_queue(selected.songs, add_to_front)

        elif key in ("e", "enter"):
            if self.selected_search_obj() is not None:
                self.app.expand(self.selected_search_obj())
        elif key == "backspace":
            self.back()
        elif key == "r":
            if self.selected_search_obj() is not None:
                self.app.create_radio_station(self.selected_search_obj())
        elif key == "j":
            super().keypress(size, "down")
        elif key == "k":
            super().keypress(size, "up")
        else:
            super().keypress(size, key)

    def back(self):
        if self.search_history:
            prev_focus, search_history = self.search_history.pop()

            self.set_search_results(list(search_history))
            self.viewing_previous_songs = False
            self.line_box.set_title("Search Results")

            try:
                self.set_focus(prev_focus)
            except:
                pass

    def update_search_results(
        self, *categories, title="Search Results", isprevsong=False
    ):
        if not self.viewing_previous_songs:  # only remember search history
            self.search_history.append((self.get_focus()[1], self.search_results))

        self.viewing_previous_songs = isprevsong

        self.set_search_results(categories)
        self.line_box.set_title(title)

    def view_previous_songs(self, songs, yt_vids):
        self.update_search_results(
            songs, yt_vids, title="Previous Songs", isprevsong=True
        )

    def set_search_results(self, categories):
        def filter_none(lst, limit=30):
            filtered = [obj for obj in lst if obj is not None]

            if self.viewing_previous_songs:
                return filtered
            else:
                return filtered[:limit]

        categories = [filter_none(cat) for cat in categories]
        self.search_results = self.SearchResults(categories)
        self.walker.clear()

        for category in self.search_results:
            if category:
                self.walker.append(type(category[0]).header())

            for item in category:
                self.walker.append(item.ui())

        if self.walker:
            self.walker.set_focus(1)

    def selected_search_obj(self):
        focus_id = self.walker.get_focus()[1]

        try:
            for category in self.search_results:
                if category:
                    focus_id -= 1

                    if focus_id < len(category):
                        return category[focus_id]

                    focus_id -= len(category)

        except (IndexError, TypeError):
            pass


class PlayBar(urwid.ProgressBar):
    vol_inds = [" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

    def __init__(self, app, *args, **kwargs):

        super(PlayBar, self).__init__(*args, **kwargs)
        self.app = app

    def get_prog_tot(self):

        progress = self.app.player.time_pos or 0
        remaining = self.app.player.time_remaining or 0
        total = progress + remaining

        return progress, total

    def get_text(self):
        if self.app.current_song is None:
            return "Idle"

        progress, total = self.get_prog_tot()
        song = self.app.current_song
        rating = ""

        if isinstance(song, Song):
            artist = song.artist

            if song.rating in (1, 5):
                rating = "(" + RATE_UI[song.rating] + ")"

        else:  # YTVideo
            artist = song.channel

        return " {} {} - {} {}[{:d}:{:02d} / {:d}:{:02d}] {}".format(
            ["■", "▶"][self.app.play_state == "play"],
            artist,
            self.app.current_song.title,
            rating,
            *sec_to_min_sec(progress),
            *sec_to_min_sec(total),
            self.vol_inds[self.app.volume],
        )

    def update(self):
        self._invalidate()

        progress, total = self.get_prog_tot()
        if progress >= 0 and total > 0:
            percent = progress / total * 100
            self.set_completion(percent)
            song = self.app.current_song
            if self.app.lastfm and isinstance(song, Song):
                if (
                    not song.lastfm_scrobbled
                    and total >= 30
                    and (percent > 50 or progress > 4 * 60)
                ):
                    self.app.lastfm.scrobble_song(song)

        else:
            self.set_completion(0)


class QueuePanel(urwid.ListBox):
    def __init__(self, app):

        self.app = app
        self.walker = urwid.SimpleFocusListWalker([])
        self.queue = []
        super().__init__(self.walker)

    def add_song_to_queue(self, song, to_front=False):

        if song:

            if to_front:
                self.queue.insert(0, song)
                self.walker.insert(0, song.ui())

            else:
                self.queue.append(song)
                self.walker.append(song.ui())

    def add_songs_to_queue(self, songs, to_front=False):

        song_list = reversed(songs) if to_front else songs

        for song in song_list:
            self.add_song_to_queue(song, to_front)

    def add_album_to_queue(self, album, to_front=False):

        album_info = self.app.g_api.get_album_info(album.id)
        track_list = (
            reversed(album_info["tracks"]) if to_front else album_info["tracks"]
        )

        for track in track_list:
            song = Song.from_dict(track)
            self.add_song_to_queue(song, to_front)

    def drop(self, idx):

        if 0 <= idx < len(self.queue):
            self.queue.pop(idx)
            self.walker.pop(idx)

    def clear(self):
        self.queue.clear()
        self.walker.clear()

    def swap(self, idx1, idx2):

        if (0 <= idx1 < len(self.queue)) and (0 <= idx2 < len(self.queue)):

            obj1, obj2 = self.queue[idx1], self.queue[idx2]
            self.queue[idx1], self.queue[idx2] = obj2, obj1

            ui1, ui2 = self.walker[idx1], self.walker[idx2]
            self.walker[idx1], self.walker[idx2] = ui2, ui1

    def to_top(self, idx):

        if 0 <= idx < len(self.queue):
            obj = self.queue[idx]
            del self.queue[idx]
            self.queue = [obj] + self.queue

            ui = self.walker[idx]
            del self.walker[idx]
            self.walker.insert(0, ui)

    def to_bottom(self, idx):

        if 0 <= idx < len(self.queue):
            obj = self.queue[idx]
            del self.queue[idx]
            self.queue.append(obj)

            ui = self.walker[idx]
            del self.walker[idx]
            self.walker.append(ui)

    def shuffle(self):
        from random import shuffle

        shuffle(self.queue)

        self.walker.clear()
        for s in self.queue:
            self.walker.append(s.ui())

    def play_next(self):

        while self.walker:
            self.walker.pop(0)
            next_song = self.queue.pop(0)

            if self.app.play(next_song):
                next_song.lastfm_scrobbled = False
                if self.app.lastfm and isinstance(next_song, Song):
                    self.app.lastfm.update_now_playing_song(next_song)
                break
        else:
            self.app.current_song = None
            self.app.stop()

    def selected_queue_obj(self):

        try:
            focus_id = self.walker.get_focus()[1]
            return self.queue[focus_id]

        except (IndexError, TypeError):
            return

    def keypress(self, size, key):
        focus_id = self.walker.get_focus()[1]

        if focus_id is None:
            return super().keypress(size, key)

        if key in ("u", "shift up"):
            self.swap(focus_id, focus_id - 1)
            self.keypress(size, "up")

        elif key in ("d", "shift down"):
            self.swap(focus_id, focus_id + 1)
            self.keypress(size, "down")

        elif key in ("v", "U", "ctrl up"):
            self.to_top(focus_id)
            self.walker.set_focus(0)

        elif key in ("D", "ctrl down"):
            self.to_bottom(focus_id)
            self.walker.set_focus(len(self.walker) - 1)

        elif key in ("right",):
            self.play_next()

        elif key in ("delete", "x"):
            self.drop(focus_id)

        elif key == "j":
            super().keypress(size, "down")

        elif key == "k":
            super().keypress(size, "up")

        elif key == "e":
            self.app.expand(self.selected_queue_obj())

        elif key == " ":

            if self.app.play_state == "stop":
                self.play_next()
            else:
                self.app.toggle_play()

        else:
            return super().keypress(size, key)
