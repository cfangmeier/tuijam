import urwid

songs = ['one', 'another on bites the dust', 'enter sandman', 'piano man', 'dance of death']
artists = ['metallica', 'iron maiden', 'judas priest', 'haken']
albums = ['some kind of bird egg', 'electric boogaloo', 'another time', '13']

log = []


class Song:
    def __init__(self, title, artist, album):
        self.title = title
        self.album = album
        self.artist = artist

    def __repr__(self):
        return f'<Song title:{self.title}, album:{self.album}, artist:{self.artist}>'


class Album:
    def __init__(self, title, artist):
        self.title = title
        self.artist = artist

    def __repr__(self):
        return f'<Album title:{self.title}, artist:{self.artist}>'


class Artist:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Artist name:{self.name}>'


def build_search_collection(N):
    from random import choice
    types = (Song, Artist, Album)
    collection = []
    for _ in range(N):
        type_ = choice(types)
        if type_ == Song:
            collection.append(Song(choice(songs), choice(artists), choice(albums)))
        elif type_ == Artist:
            collection.append(Artist(choice(artists)))
        else:
            collection.append(Album(choice(albums), choice(artists)))
    return (list(filter(lambda o: type(o) == Song, collection)),
            list(filter(lambda o: type(o) == Album, collection)),
            list(filter(lambda o: type(o) == Artist, collection)))


class UI(urwid.Pile):

    palette = [
        ('header', 'white,underline', 'black'),
        ('header_bg', 'white', 'black'),
        ('line', 'white', ''),
        ('search normal', 'white', ''),
        ('search select', 'white', 'dark red'),

        ('region_bg normal', '', ''),
        ('region_bg select', '', 'black'),
    ]

    def click(self, *args, **kwargs):
        print(args, kwargs)

    def __init__(self):
        self.search_results = urwid.SimpleFocusListWalker([])
        search_results_box = urwid.ListBox(self.search_results)
        search_results_box = urwid.LineBox(search_results_box, title='Search Results')
        search_results_box = urwid.AttrMap(search_results_box, 'region_bg normal', 'region_bg select')

        self.now_playing = urwid.Text('Now Playing')

        # urwid.connect_signal(search_results_box.base_widget, 'click', self.click)

        self.queue = urwid.SimpleFocusListWalker([])
        queue_box = urwid.ListBox(self.queue)
        queue_box = urwid.LineBox(queue_box, title='Queue')
        queue_box = urwid.AttrMap(queue_box, 'region_bg normal', 'region_bg select')

        self.command_input = urwid.Edit('> ', multiline=False, allow_tab=False)

        urwid.Pile.__init__(self, [('weight', 12, search_results_box),
                                   ('pack', self.now_playing),
                                   ('weight', 7, queue_box),
                                   ('pack', self.command_input)
                                   ])

    def header(self, txts):
        header = urwid.Columns([('weight', 1, urwid.Text(('header', txt)))
                                for txt in txts])
        return urwid.AttrMap(header, 'header_bg')

    def line(self, txts):
        first, *rest = txts
        items = [urwid.SelectableIcon(first, 0)]
        for line in rest:
            items.append(urwid.Text(line))
        line = urwid.Columns(items)
        line = urwid.AttrMap(line, 'search normal', 'search select')
        return line

    def selected_search_obj(self):
        focus_id = self.search_results.get_focus()[1]
        songs, albums, artists = self.search_list

        focus_id -= 1
        if focus_id < len(songs):
            return songs[focus_id]
        focus_id -= (1 + len(songs))
        if focus_id < len(albums):
            return albums[focus_id]
        focus_id -= (1 + len(albums))
        return artists[focus_id]

    def enqueue(self, obj):
        pass

    def expand(self, obj):
        pass

    def radio(self, obj):
        pass

    def keypress(self, size, key):
        if key in ('q', 'e', 'r'):
            focus_obj = self.selected_search_obj()
            self.now_playing.set_text(repr(focus_obj))
            if key == 'q' and type(focus_obj) in (Song, Album):
                self.enqueue(focus_obj)
            elif key == 'e':
                self.expand(focus_obj)
            else:
                self.radio(focus_obj)

        else:
            return self.focus.keypress(size, key)

    def display_search_results(self, search_list=None):
        if search_list is None:
            self.search_list = build_search_collection(40)
        songs, albums, artists = self.search_list

        self.search_results.clear()
        if songs:
            self.search_results.append(self.header(['Title', 'Album', 'Artist']))
        for song in songs:
            self.search_results.append(self.line([song.title, song.album, song.artist]))

        if albums:
            self.search_results.append(self.header(['Album', 'Artist']))
        for album in albums:
            self.search_results.append(self.line([album.title, album.artist]))

        if artists:
            self.search_results.append(self.header(['Artist']))
        for artist in artists:
            self.search_results.append(self.line([artist.name]))


ui = UI()


def show_or_exit(key):
    if key == 'esc':
        raise urwid.ExitMainLoop()
    elif key == 'enter':
        ui.display_search_results()
    else:
        # ui.now_playing.set_text(repr(key))
        # try:
        #     ui.now_playing.set_text(repr(ui.search_results.get_focus()[0].base_widget))
        # except AttributeError:
        ui.now_playing.set_text(repr(ui.search_results.get_focus()))
        # current = ui.search_results.get_focus()[1]
        # try:
        #     ui.search_results.set_focus(current+1)
        # except IndexError:
        #     pass


loop = urwid.MainLoop(ui, ui.palette, unhandled_input=show_or_exit)
loop.screen.set_terminal_properties(colors=256)
try:
    loop.run()
except Exception as e:
    print(log)
    raise e
