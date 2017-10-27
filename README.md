# TUIJam
A fancy TUI client for Google Play Music. 

TUIJam seeks to make a simple, attractive, terminal-based interface to
listening to music for Google Play Music All-Access subscribers.

[![asciicast](https://asciinema.org/a/rXcb2Ga0RG9JYNWtYH6fDRvmx.png)](https://asciinema.org/a/rXcb2Ga0RG9JYNWtYH6fDRvmx)

# Dependencies
* [Python >= 3.6](https://www.python.org/downloads)
* [mpv](https://mpv.io)

# Installation
```bash
git clone git@github.com:cfangmeier/tuijam.git
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
  - `ctrl-r` view recently played songs
  - `ctrl-s` shuffle queued songs (Note: If this hangs, try running `stty -ixon` in your terminal and restarting `tuijam`)
  - `>` seek forward 10 seconds
  - `<` seek backwards 10 seconds
  - `+` volume up
  - `-` volume down
  - `tab`/`shift-tab` cycle focus through search/queue/input windows
  - In search window, 
    - `q` Add selected song/album to queue
    - `r` Create radio station around selected song/album/artist and add 50 songs from it to queue
    - `e` view information about selected song/album/artist
    - `backspace` go back in search/expand history
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
