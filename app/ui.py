import signal

import urwid
from gmusicapi import Mobileclient

log = []

# ######################################################33
# ######################################################33

def build_search_collection(N):
    from random import choice
    songs = ['one', 'another on bites the dust', 'enter sandman', 'piano man', 'dance of death']
    artists = ['metallica', 'iron maiden', 'judas priest', 'haken']
    albums = ['some kind of bird egg', 'electric boogaloo', 'another time', '13']
    years = [1967, 2066, 1924, 1098]

    types = (Song, Artist, Album)
    collection = []
    for _ in range(N):
        type_ = choice(types)
        if type_ == Song:
            collection.append(Song(choice(songs), choice(artists), choice(albums), 0))
        elif type_ == Artist:
            collection.append(Artist(choice(artists)))
        else:
            collection.append(Album(choice(albums), choice(artists), choice(years)))
    return (list(filter(lambda o: type(o) == Song, collection)),
            list(filter(lambda o: type(o) == Album, collection)),
            list(filter(lambda o: type(o) == Artist, collection)))
# ######################################################33
# ######################################################33


class MusicObject:
    @staticmethod
    def to_ui(*txts):
        first, *rest = [str(txt) for txt in txts]
        items = [urwid.SelectableIcon(first, 0)]
        for line in rest:
            items.append(urwid.Text(line))
        line = urwid.Columns(items)
        line = urwid.AttrMap(line, 'search normal', 'search select')
        return line

    @staticmethod
    def header_ui(*txts):
        header = urwid.Columns([('weight', 1, urwid.Text(('header', txt)))
                                for txt in txts])
        return urwid.AttrMap(header, 'header_bg')


class Song(MusicObject):
    def __init__(self, title, album, artist, id_):
        self.title = title
        self.album = album
        self.artist = artist
        self.id = id_

    def __repr__(self):
        return f'<Song title:{self.title}, album:{self.album}, artist:{self.artist}>'

    def __str__(self):
        return f'{self.title} by {self.artist}'

    def ui(self):
        return self.to_ui(self.title, self.album, self.artist)

    @staticmethod
    def header():
        return MusicObject.header_ui('Title', 'Album', 'Artist')



class Album(MusicObject):
    def __init__(self, title, artist, year, id_):
        self.title = title
        self.artist = artist
        self.year = year
        self.id = id_

    def __repr__(self):
        return f'<Album title:{self.title}, artist:{self.artist}, year:{self.year}>'

    def ui(self):
        return self.to_ui(self.title, self.artist, self.year)

    @staticmethod
    def header():
        return MusicObject.header_ui('Album', 'Artist', 'Year')


class Artist(MusicObject):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Artist name:{self.name}>'

    def ui(self):
        return self.to_ui(self.name)

    @staticmethod
    def header():
        return MusicObject.header_ui('Artist')


class CommandInput(urwid.Edit):
    def __init__(self, app):
        self.app = app
        super().__init__('search > ', multiline=False, allow_tab=False)

    def keypress(self, size, key):
        if key == 'enter':
            txt = self.edit_text
            if txt:
                self.set_edit_text('')
                self.app.search(txt)
            return None
        else:
            size = (size[0],)
            return super().keypress(size, key)


class SearchPanel(urwid.ListBox):
    def __init__(self, app):
        self.app = app
        self.walker = urwid.SimpleFocusListWalker([])
        super().__init__(self.walker)

    def keypress(self, size, key):
        if key == 'q':
            selected = self.selected_search_obj()
            if selected and type(selected) in (Song, Album):
                self.app.queue_panel.add_to_queue(selected)
        elif key == 'j':
            super().keypress(size, 'down')
        elif key == 'k':
            super().keypress(size, 'up')
        else:
            super().keypress(size, key)

    def set_search_results(self, search_results):
        self.search_results = search_results
        songs, albums, artists = search_results

        self.walker.clear()

        if songs:
            self.walker.append(Song.header())
        for song in songs:
            self.walker.append(song.ui())

        if albums:
            self.walker.append(Album.header())
        for album in albums:
            self.walker.append(album.ui())

        if artists:
            self.walker.append(Artist.header())
        for artist in artists:
            self.walker.append(artist.ui())

        if self.walker:
            self.walker.set_focus(1)

    def selected_search_obj(self):
        focus_id = self.walker.get_focus()[1]
        songs, albums, artists = self.search_results

        try:
            focus_id -= 1
            if focus_id < len(songs):
                return songs[focus_id]
            focus_id -= (1 + len(songs))
            if focus_id < len(albums):
                return albums[focus_id]
            focus_id -= (1 + len(albums))
            return artists[focus_id]
        except IndexError:
            return None


class QueuePanel(urwid.ListBox):
    def __init__(self, app):
        self.app = app
        self.walker = urwid.SimpleFocusListWalker([])
        self.queue = []
        super().__init__(self.walker)

    def add_to_queue(self, music_obj):
        # assume Song for now
        self.queue.append(music_obj)
        self.walker.append(music_obj.ui())

    def drop(self, idx):
        if 0 <= idx < len(self.queue):
            self.queue.pop(idx)
            self.walker.pop(idx)

    def swap(self, idx1, idx2):
        if (0 <= idx1 < len(self.queue)) and (0 <= idx2 < len(self.queue)):
            obj1, obj2 = self.queue[idx1], self.queue[idx2]
            self.queue[idx1], self.queue[idx2] = obj2, obj1

            ui1, ui2 = self.walker[idx1], self.walker[idx2]
            self.walker[idx1], self.walker[idx2] = ui2, ui1

    def keypress(self, size, key):
        focus_id = self.walker.get_focus()[1]
        if focus_id is None:
            return super().keypress(size, key)

        if key == 'u':
            self.swap(focus_id, focus_id-1)
            self.keypress(size, 'up')
        elif key == 'd':
            self.swap(focus_id, focus_id+1)
            self.keypress(size, 'down')
        elif key == 'delete':
            self.drop(focus_id)
        elif key == 'j':
            super().keypress(size, 'down')
        elif key == 'k':
            super().keypress(size, 'up')
        elif key == ' ':
            if self.app.play_state == 'stop':
                self.walker.pop()
                self.app.play(self.queue.pop())
            else:
                self.app.toggle_play()
        else:
            return super().keypress(size, key)


class App(urwid.Pile):

    palette = [
        ('header', 'white,underline', 'black'),
        ('header_bg', 'white', 'black'),
        ('line', 'white', ''),
        ('search normal', 'white', ''),
        ('search select', 'white', 'dark red'),

        ('region_bg normal', '', ''),
        ('region_bg select', '', 'black'),
    ]

    def __init__(self):

        self.g_api = Mobileclient()
        deviceid = "3d9cf4c429a3e170"
        self.g_api.login('cfangmeier74@gmail.com', 'fnqugbdwjyfoqbxf', deviceid)

        import app.mpv as mpv
        self.player = mpv.MPV()

        self.search_panel = SearchPanel(self)
        search_panel_wrapped = urwid.LineBox(self.search_panel, title='Search Results')
        search_panel_wrapped = urwid.AttrMap(search_panel_wrapped, 'region_bg normal', 'region_bg select')
        self.search_panel_wrapped = search_panel_wrapped

        self.now_playing = urwid.Text('')
        self.progress = urwid.Text('0:00/0:00', align='right')
        status_line = urwid.Columns([('weight', 3, self.now_playing),
                                     ('weight', 1, self.progress)])

        self.queue_panel = QueuePanel(self)
        queue_panel_wrapped = urwid.LineBox(self.queue_panel, title='Queue')
        queue_panel_wrapped = urwid.AttrMap(queue_panel_wrapped, 'region_bg normal', 'region_bg select')
        self.queue_panel_wrapped = queue_panel_wrapped

        self.command_input = urwid.Edit('> ', multiline=False)
        self.command_input = CommandInput(self)

        urwid.Pile.__init__(self, [('weight', 12, search_panel_wrapped),
                                   ('pack', status_line),
                                   ('weight', 7, queue_panel_wrapped),
                                   ('pack', self.command_input)
                                   ])
        self.set_focus(self.command_input)

        self.play_state = 'stop'
        self.current_song = None

    @staticmethod
    def sec_to_min_sec(sec_tot):
        if sec_tot is None:
            return 0, 0
        else:
            min_ = int(sec_tot // 60)
            sec = int(sec_tot % 60)
            return min_, sec

    def update_progress(self):
        curr_time_s = self.player.time_pos
        rem_time_s = self.player.time_remaining
        if curr_time_s is not None and rem_time_s is not None:
            curr_time = self.sec_to_min_sec(curr_time_s)
            total_time = self.sec_to_min_sec(curr_time_s+rem_time_s)
        else:
            curr_time = (0, 0)
            total_time = (0, 0)
        self.progress.set_text(f'{curr_time[0]}:{curr_time[1]:02d}/{total_time[0]}:{total_time[1]:02d}')

    def update_now_playing(self, *args, **kwargs):
        if self.play_state == 'play':
            self.update_progress()
            self.now_playing.set_text(f'Now Playing: {str(self.current_song)}')
            self.loop.set_alarm_in(1, self.update_now_playing)
        elif self.play_state == 'pause':
            self.update_progress()
            self.now_playing.set_text(f'Paused: {str(self.current_song)}')
        else:
            self.now_playing.set_text('')

    def play(self, song):
        self.current_song = song
        url = self.g_api.get_stream_url(song.id)
        self.player.play(url)
        self.play_state = 'play'
        self.update_now_playing()
        self.loop.set_alarm_in(1, self.update_now_playing)

    def stop(self, song):
        self.current_song = None
        self.player.quit()
        self.play_state = 'stop'
        self.update_now_playing()

    def toggle_play(self):
        if self.play_state == 'play':
            self.player.pause = True
            self.play_state = 'pause'
            self.update_now_playing()
        elif self.play_state == 'pause':
            self.player.pause = False
            self.play_state = 'play'
            self.update_now_playing()
            self.loop.set_alarm_in(1, self.update_now_playing)

    def keypress(self, size, key):
        if key == 'tab':
            current_focus = self.focus
            if current_focus == self.search_panel_wrapped:
                self.set_focus(self.queue_panel_wrapped)
            elif current_focus == self.queue_panel_wrapped:
                self.set_focus(self.command_input)
            else:
                self.set_focus(self.search_panel_wrapped)
        elif key == 'shift tab':
            current_focus = self.focus
            if current_focus == self.search_panel_wrapped:
                self.set_focus(self.command_input)
            elif current_focus == self.queue_panel_wrapped:
                self.set_focus(self.search_panel_wrapped)
            else:
                self.set_focus(self.queue_panel_wrapped)
        elif key == 'ctrl p':
            self.toggle_play()
        elif key == 'ctrl q':
            self.stop()
        else:
            return self.focus.keypress(size, key)

    def search(self, query):

        results = self.g_api.search(query)

        songs = []
        for hit in results['song_hits']:
            title = hit['track']['title']
            album = hit['track']['album']
            artist = hit['track']['artist']
            try:
                id_ = hit['track']['id']
            except KeyError:
                id_ = hit['track']['storeId']
            songs.append(Song(title, album, artist, id_))

        albums = []
        for hit in results['album_hits']:
            title = hit['album']['name']
            artist = hit['album']['albumArtist']
            year = hit['album']['year']
            id_ = hit['album']['albumId']
            albums.append(Album(title, artist, year, id_))

        self.search_panel.set_search_results((songs, albums, []))
        self.set_focus(self.search_panel_wrapped)

    def cleanup(self):
        self.player.quit()
        del self.player
        self.g_api.logout()


def handle_sigint(signum, frame):
    raise urwid.ExitMainLoop()


if __name__ == '__main__':
    app = App()
    signal.signal(signal.SIGINT, handle_sigint)

    # def show_or_exit(key):
    #     if key == 'esc':
    #         raise urwid.ExitMainLoop()
    #     elif key == 'enter':
    #         app.now_playing.set_text('got an enter!')
    #     else:
    #         app.now_playing.set_text(repr(app.search_panel.get_focus()))
    # loop = urwid.MainLoop(app, app.palette, unhandled_input=show_or_exit)
    loop = urwid.MainLoop(app, app.palette)
    try:
        app.loop = loop
        loop.run()
        app.cleanup()
    except Exception as e:
        print(log)
        app.cleanup()
        raise e
