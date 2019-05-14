import logging

from .music_objects import Song, YTVideo


def setup_mpris(app):
    from pydbus import SessionBus, Variant
    from pydbus.generic import signal

    class MPRIS:
        """
<node>
<interface name="org.mpris.MediaPlayer2">
<property name="CanQuit" type="b" access="read" />
<property name="CanRaise" type="b" access="read" />
<property name="HasTrackList" type="b" access="read" />
<property name="Identity" type="s" access="read" />
<property name="SupportedMimeTypes" type="as" access="read" />
<property name="SupportedUriSchemes" type="as" access="read" />
<method name="Quit" />
<method name="Raise" />
</interface>
<interface name="org.mpris.MediaPlayer2.Player">
<property name="PlaybackStatus" type="s" access="read" />
<property name="Rate" type="d" access="readwrite" />
<property name="Metadata" type="a{sv}" access="read"/>
<property name="Volume" type="d" access="readwrite" />
<property name="Position" type="x" access="read" />
<property name="MinimumRate" type="d" access="readwrite" />
<property name="MaximumRate" type="d" access="readwrite" />
<property name="CanGoNext" type="b" access="read" />

<property name="CanGoPrevious" type="b" access="read" />
<property name="CanPlay" type="b" access="read" />
<property name="CanPause" type="b" access="read" />
<property name="CanSeek" type="b" access="read" />
<property name="CanControl" type="b" access="read" />

<method name="Next" />
<method name="Previous" />
<method name="Pause" />
<method name="PlayPause" />
<method name="Stop" />
<method name="Play" />
<method name="Seek">
  <arg type="x" direction="in" />
</method>
<method name="SetPosition">
  <arg type="o" direction="in" />
  <arg type="x" direction="in" />
</method>
<method name="OpenUri">
  <arg type="s" direction="in" />
</method>
</interface>
</node>
        """

        PropertiesChanged = signal()

        def __init__(self, app):
            self.app = app

        def emit_property_changed(self, attr):
            self.PropertiesChanged(
                "org.mpris.MediaPlayer2.Player", {attr: getattr(self, attr)}, []
            )

        @property
        def CanQuit(self):
            return False

        @property
        def CanRaise(self):
            return False

        @property
        def HasTrackList(self):
            return False

        @property
        def Identity(self):
            return "TUIJam"

        @property
        def SupportedMimeTypes(self):
            return []

        @property
        def SupportedUriSchemes(self):
            return []

        def Raise(self):
            pass

        def Quit(self):
            pass

        @property
        def PlaybackStatus(self):
            return {"play": "Playing", "pause": "Paused", "stop": "Stopped"}[
                self.app.play_state
            ]

        @property
        def Rate(self):
            return 1.0

        @Rate.setter
        def Rate(self, rate):
            pass

        @property
        def Metadata(self):
            song = self.app.current_song

            if type(song) == Song:

                logging.info("New song ID: " + str(song.id))

                return {
                    "mpris:trackid": Variant(
                        "o", "/org/tuijam/GM_" + str(song.id).replace("-", "_")
                    ),
                    "mpris:artUrl": Variant("s", song.albumArtRef),
                    "xesam:title": Variant("s", song.title),
                    "xesam:artist": Variant("as", [song.artist]),
                    "xesam:album": Variant("s", song.album),
                    "xesam:url": Variant("s", song.stream_url),
                }

            elif type(song) == YTVideo:

                return {
                    "mpris:trackid": Variant(
                        "o", "/org/tuijam/YT_" + str(song.id).replace("-", "_")
                    ),
                    "mpris:artUrl": Variant("s", song.thumbnail),
                    "xesam:title": Variant("s", song.title),
                    "xesam:artist": Variant("as", [song.channel]),
                    "xesam:album": Variant("s", ""),
                    "xesam:url": Variant("s", song.stream_url),
                }

            else:
                return {}

        @property
        def Volume(self):
            return self.app.volume / 8.0

        @Volume.setter
        def Volume(self, volume):
            volume = max(0, min(volume, 1))
            self.app.volume = int(volume * 8)
            self.app.player.volume = volume * 100
            self.emit_property_changed("Volume")

        @property
        def Position(self):
            try:
                return int(1000000 * self.app.player.time_pos)

            except TypeError:
                return 0

        @property
        def MinimumRate(self):
            return 1.0

        @property
        def MaximumRate(self):
            return 1.0

        @property
        def CanGoNext(self):
            return len(self.app.queue_panel.queue) > 0

        @property
        def CanGoPrevious(self):
            return False

        @property
        def CanPlay(self):
            return (
                len(self.app.queue_panel.queue) > 0 or self.app.current_song is not None
            )

        @property
        def CanPause(self):
            return self.app.current_song is not None

        @property
        def CanSeek(self):
            return self.app.current_song is not None

        @property
        def CanControl(self):
            return True

        def Next(self):
            self.app.queue_panel.play_next()

        def Previous(self):
            pass

        def Pause(self):
            if self.app.play_state == "play":
                self.app.toggle_play()

        def PlayPause(self):
            self.app.toggle_play()

        def Stop(self):
            self.app.stop()

        def Play(self, song_id):
            self.app.toggle_play()

        def Seek(self, offset):
            pass

        def SetPosition(self, track_id, position):
            pass

        def OpenUri(self, uri):
            pass

    mpris = MPRIS(app)
    bus = SessionBus()
    try:
        bus.publish("org.mpris.MediaPlayer2.tuijam", ("/org/mpris/MediaPlayer2", mpris))
        return mpris
    except RuntimeError as e:
        logging.exception(e)
        return None
