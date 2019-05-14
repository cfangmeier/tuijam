from itertools import zip_longest
import logging
import json

import urwid

from .utility import sec_to_min_sec


class MusicObject:
    @staticmethod
    def to_ui(*txts, weights=()):
        first, *rest = [
            (weight, str(txt))
            for weight, txt in zip_longest(weights, txts, fillvalue=1)
        ]
        items = [("weight", first[0], urwid.SelectableIcon(first[1], 0))]

        for weight, line in rest:
            items.append(("weight", weight, urwid.Text(line)))

        line = urwid.Columns(items)
        line = urwid.AttrMap(line, "search normal", "search select")

        return line

    @staticmethod
    def header_ui(*txts, weights=()):
        header = urwid.Columns(
            [
                ("weight", weight, urwid.Text(("header", txt)))
                for weight, txt in zip_longest(weights, txts, fillvalue=1)
            ]
        )
        return urwid.AttrMap(header, "header_bg")


class Song(MusicObject):
    ui_weights = (1, 2, 1, 0.2, 0.2)

    def __init__(
        self,
        title,
        album,
        albumId,
        albumArtRef,
        artist,
        artistId,
        id_,
        type_,
        trackType,
        length,
        rating,
    ):
        self.title = title
        self.album = album
        self.albumId = albumId
        self.albumArtRef = albumArtRef
        self.artist = artist
        self.artistId = artistId
        self.id = id_
        self.type = type_
        self.trackType = trackType
        self.length = length
        self.rating = rating
        self.stream_url = ""

    def __repr__(self):
        return f"<Song title:{self.title}, album:{self.album}, artist:{self.artist}>"

    def __str__(self):
        return f"{self.title} by {self.artist}"

    def fmt_str(self):
        return [("np_song", f"{self.title} "), "by ", ("np_artist", f"{self.artist}")]

    def ui(self):
        from .ui import RATE_UI

        return self.to_ui(
            self.title,
            self.album,
            self.artist,
            "{:d}:{:02d}".format(*self.length),
            RATE_UI[self.rating],
            weights=self.ui_weights,
        )

    @classmethod
    def header(cls):
        return MusicObject.header_ui(
            "Title", "Album", "Artist", "Length", "Rating", weights=cls.ui_weights
        )

    @staticmethod
    def from_dict(d):

        try:
            title = d["title"]
            album = d["album"]
            albumId = d["albumId"]
            albumArtRef = d["albumArtRef"][0]["url"]
            artist = d["artist"]
            artistId = d["artistId"][0]

            try:
                id_ = d["id"]
                type_ = "library"

            except KeyError:
                id_ = d["storeId"]
                type_ = "store"

            trackType = d.get("trackType", None)
            length = sec_to_min_sec(int(d["durationMillis"]) / 1000)

            # rating scheme
            #  0 - No Rating
            #  1 - Thumbs down
            #  5 - Thumbs up

            rating = int(d.get("rating", 0))
            return Song(
                title,
                album,
                albumId,
                albumArtRef,
                artist,
                artistId,
                id_,
                type_,
                trackType,
                length,
                rating,
            )

        except KeyError as e:
            logging.exception(f"Missing Key {e} in dict \n{d}")


class YTVideo(MusicObject):
    ui_weights = (4, 1)

    def __init__(self, title, channel, thumbnail, id_):

        self.title = title
        self.channel = channel
        self.thumbnail = thumbnail
        self.id = id_
        self.stream_url = ""

    def __repr__(self):
        return f"<YTVideo title:{self.title}, channel:{self.artist}>"

    def __str__(self):
        return f"{self.title} by {self.channel}"

    def fmt_str(self):
        return [("np_song", f"{self.title} "), "by ", ("np_artist", f"{self.channel}")]

    def ui(self):
        return self.to_ui(self.title, self.channel, weights=self.ui_weights)

    @classmethod
    def header(cls):
        return MusicObject.header_ui("Youtube", "Channel", weights=cls.ui_weights)

    @staticmethod
    def from_dict(d):

        try:
            title = d["snippet"]["title"]
            thumbnail = d["snippet"]["thumbnails"]["medium"]["url"]
            channel = d["snippet"]["channelTitle"]
            id_ = d["id"]["videoId"]

            return YTVideo(title, channel, thumbnail, id_)

        except KeyError as e:
            logging.exception(f"Missing Key {e} in dict \n{d}")


class Album(MusicObject):
    def __init__(self, title, artist, artistId, year, id_):

        self.title = title
        self.artist = artist
        self.artistId = artistId
        self.year = year
        self.id = id_

    def __repr__(self):
        return f"<Album title:{self.title}, artist:{self.artist}, year:{self.year}>"

    def ui(self):
        return self.to_ui(self.title, self.artist, self.year)

    @staticmethod
    def header():
        return MusicObject.header_ui("Album", "Artist", "Year")

    @staticmethod
    def from_dict(d):
        try:
            try:
                title = d["name"]
            except KeyError:
                title = d["title"]

            try:
                artist = d["albumArtist"]
                artistId = d["artistId"][0]
            except KeyError:
                artist = d["artist_name"]
                artistId = d["artist_metajam_id"]

            try:
                year = d["year"]
            except KeyError:
                year = ""

            try:
                id_ = d["albumId"]
            except KeyError:
                id_ = d["id"]["metajamCompactKey"]

            return Album(title, artist, artistId, year, id_)

        except KeyError as e:
            logging.exception(f"Missing Key {e} in dict \n{d}")


class Artist(MusicObject):
    def __init__(self, name, id_):
        self.name = name
        self.id = id_

    def __repr__(self):
        return f"<Artist name:{self.name}>"

    def ui(self):
        return self.to_ui(self.name)

    @staticmethod
    def header():
        return MusicObject.header_ui("Artist")

    @staticmethod
    def from_dict(d):
        try:
            name = d["name"]
            id_ = d["artistId"]

            return Artist(name, id_)

        except KeyError as e:

            logging.exception(f"Missing Key {e} in dict \n{d}")


class Situation(MusicObject):
    ui_weights = (0.2, 1)

    def __init__(self, title, description, id_, stations):
        self.title = title
        self.description = description
        self.id = id_
        self.stations = stations

    def __repr__(self):
        return f"<Situation title:{self.title}>"

    def ui(self):
        return self.to_ui(self.title, self.description)

    @staticmethod
    def header():
        return MusicObject.header_ui("Situation", "Description")

    @staticmethod
    def from_dict(d):

        try:

            title = d["title"]
            description = d["description"]
            id_ = d["id"]
            situations = [d]
            stations = []

            while situations:

                situation = situations.pop()

                if "situations" in situation:
                    situations.extend(situation["situations"])
                else:
                    stations.extend(
                        [
                            RadioStation(
                                station["name"],
                                [],
                                id_=station["seed"]["curatedStationId"],
                            )
                            for station in situation["stations"]
                        ]
                    )

            return Situation(title, description, id_, stations)

        except KeyError as e:
            logging.exception(f"Missing Key {e} in dict \n{d}")


class RadioStation(MusicObject):
    def __init__(self, title, seeds, id_=None):
        self.title = title
        self.seeds = seeds
        self.id = id_

    def __repr__(self):
        return f"<RadioStation title:{self.title}>"

    def ui(self):
        return self.to_ui(self.title)

    def get_station_id(self, api):
        if self.id:
            return api.create_station(self.title, curated_station_id=self.id)
        else:
            seed = self.seeds[0]
            return api.create_station(self.title, artist_id=seed["artistId"])

    @staticmethod
    def header():
        return MusicObject.header_ui("Station Name")

    @staticmethod
    def from_dict(d):

        try:
            title = d["title"]
            seeds = d["id"]["seeds"]

            return RadioStation(title, seeds)

        except KeyError as e:
            logging.exception(f"Missing Key {e} in dict \n{d}")


class Playlist(MusicObject):
    ui_weights = (0.4, 1)

    def __init__(self, name, songs=None, id_=None):
        self.name = name
        self.songs = songs
        self.id = id_

    def __repr__(self):
        return f"<Playlist name:{self.name}>"

    def ui(self):
        return self.to_ui(self.name, str(len(self.songs)), weights=self.ui_weights)

    @classmethod
    def header(cls):
        return MusicObject.header_ui("Playlist Name", "# Songs", weights=cls.ui_weights)

    @staticmethod
    def from_dict(d):

        try:
            name = d["name"]
            id_ = d["id"]
            songs = [
                Song.from_dict(song["track"]) for song in d["tracks"] if "track" in song
            ]

            if songs:
                return Playlist(name, songs, id_)

        except KeyError as e:
            logging.exception(f"Missing Key {e} in dict \n{d}")


def serialize(music_objects: list) -> str:
    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (Song, YTVideo)):
                key = "__%s__" % obj.__class__.__name__
                return {key: obj.__dict__}
            return json.JSONEncoder.default(self, obj)

    return json.dumps(music_objects, cls=CustomEncoder)


def deserialize(music_object_json: str) -> list:
    def decode(dct):
        for type_name, value in dct.items():
            cls = globals()[type_name.strip("_")]
            obj = cls.__new__(cls)
            for key, val in value.items():
                setattr(obj, key, val)
            return obj

    return [decode(dct) for dct in json.loads(music_object_json)]
