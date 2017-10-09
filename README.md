# TUIJam
A fancy TUI client for Google Play Music. 

TUIJam seeks to make a simple, attractive, terminal-based interface to
listening to music for Google Play Music All-Access subscribers.

<a href="http://www.youtube.com/watch?feature=player_embedded&v=WIkk7PLCTb4
" target="_blank"><img src="http://img.youtube.com/vi/WIkk7PLCTb4/0.jpg" 
alt="Demonstration" width="240" height="180" border="10" /></a>

# Dependencies
* [Python >= 3.6](https://www.python.org/downloads)
* [mpv](https://mpv.io)

# Installation
```bash
git clone git@github.com:cfangmeier/tuijam.git`
cd tuijam
python setup.py install --user
```

# Configuration
Login credentials are stored in `$HOME/.config/tuijam/config.yaml`. An example config file might look like:
```yaml
email: you@your-email.com
password: your-password
device_id: yourdeviceid
```
Note that if you have 2-factor setup on your Google account, you need to make
an app-password for TUIJam. To find your device ID, first put your email and
password in the config file, then run `gpymusic-get-dev-id`. If your login
works, you will get a list of acceptable device ids, place any one of them into
the config file.

# Controls
  - `ctrl-c` quit
  - `ctrl-p` toggle play/pause
  - `ctrl-n` move to next song
  - `>` seek forward 10 seconds
  - `<` seek backwards 10 seconds
  - `tab`/`shift-tab` cycle focus through search/queue/input windows
  - In search window, 
    - `q` add selected song/album to queue
    - `e` view information about selected song/album/artist
  - In queue window,
    - `u` move selected song up in queue
    - `d` move selected song down in queue
    - `delete` remove selected song from queue
  - In input window,
    - Type search query and press enter. Results are shown in search window.


# Thanks
TUIJam was heavily inspired by the
[gpymusic](https://github.com/christopher-dG/gpymusic) project, and, of course,
could not exists without the great
[gmusicapi](https://github.com/simon-weber/gmusicapi).
