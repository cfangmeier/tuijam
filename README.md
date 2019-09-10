# TUIJam
A fancy TUI client for Google Play Music.

TUIJam seeks to make a simple, attractive, terminal-based interface to
listening to music for Google Play Music All-Access subscribers.

[![asciicast](https://asciinema.org/a/155875.png)](https://asciinema.org/a/155875)

# Dependencies
* [Python >= 3.6](https://www.python.org/downloads)
* [mpv](https://mpv.io)
* [youtube-dl](https://rg3.github.io/youtube-dl/)

# Installation
To install from source
```bash
git clone git@github.com:cfangmeier/tuijam.git
cd tuijam
python setup.py install --user
```

or from pypi
```bash
pip install --user tuijam
```

or from the AUR
```bash
yay -S tuijam  # mainline
yay -S tuijam-git # dev build
```

# First Time Setup

The first time TUIJam runs, it will perform an OAuth handshake with Google. Tokens are then stored locally and subsequent logins should be automatic.

# Configuration

Local configuration is stored in `$HOME/.config/tuijam/config.yaml`.

  - `persist_queue`: (Default: `True`) Saves the current queue and reloads it when the app resumes
  - `reverse_scrolling`: (Default: `False`) Switches the direction of mouse scrolling

# MPRIS Support
TUIJam supports a subset of the [MPRIS](https://specifications.freedesktop.org/mpris-spec/latest/) spec to allow for external control via clients such as [playerctl](https://github.com/acrisci/playerctl). Currently, the following behavior is supported:

  - Get current song metadata (Title/Album/Artist)
  - Get player status (Playing/Paused/Stopped)
  - Play/Pause current song
  - Next Song
  - Stop

If this causes problems for you, please feel free to create an issue, but this feature can also be disabled by placing the following line in your config file:

```yaml
mpris_enabled: false
```
# Youtube
From version 0.3.0, Youtube videos are included in search results. By default, no video is shown during playback, but this can be changed by adding the following line to the config file:

```yaml
video: true
```

# Last.fm Support
The player supports Last.fm scrobbling. To enable it, you need to run: 
```bash
tuijam get_lastfm_token
```

# API Key Management

Youtube and Last.fm integration uses api keys that are supplied by me. TUIJam queries them at runtime from a server that I maintain. If the server goes down, of if you would just prefer not to rely on it, you can specify your own keys in the config file. Keys are only queried if they are not present in the config file.

```yaml
GOOGLE_DEVELOPER_KEY: "yourdeveloperkeyhere"
LASTFM_API_KEY: "yourapikeyhere"
LASTFM_API_SECRET: "yoursecrethere"
```

You can also run your own server using or adapting `key_server_example.py` and setting your config file to point to your server.

```yaml
key_server: "https://my-tuijam-key-server.io"
```

# VIM-Mode
Enables vim style controls. By default, this mode is disabled, but this can be changed by adding the following line to the config file:

```yaml
vim: true
```

# Controls
  - `ctrl-c` Quit
  - `ctrl-p` Toggle play/pause
  - `ctrl-k` Stop
  - `ctrl-q` Add all songs in search result to queue
  - `ctrl-n` Move to next song
  - `ctrl-r` View recently played songs
  - `ctrl-w` Clear the current queue
  - `ctrl-s` Shuffle queued songs (Note: If this hangs, try running `stty -ixon` in your terminal and restarting `tuijam`)
  - `ctrl-u` Thumbs up the currently playing song
  - `ctrl-d` Thumbs down the currently playing song
  - `>` Seek forward 10 seconds
  - `<` Seek backwards 10 seconds
  - `+` Volume up
  - `-` Volume down
  - `tab`/`shift-tab` cycle focus through search/queue/input windows
  - `\`/`ctrl-f` move to search bar
  - In search window,
    - `q` Add selected song/album to queue
    - `shift-q` Add selected song/album to the top of queue (play next)
    - `r` Create radio station around selected song/album/artist and add 50 songs from it to queue
    - `e` view information about selected song/album/artist
    - `backspace` go back in search/expand history
  - In queue window,
    - `u`/`shift-up` Move selected song up in queue
    - `d`/`shift-down` Move selected song down in queue
    - `shift-u`/`v`/`ctrl-up` Move selected song to the top in queue
    - `shift-d`/`ctrl-down` Move selected song to the bottom in queue
    - `delete`/`x` Remove selected song from queue
  - In input window,
    - Type search query and press enter. Results are shown in search window.
    - Enter an empty query to view the suggested "Listen Now" stations and albums.
  - In VIM-mode, these controls will change to
    - `i` Insert mode
    - `esc` Leave insert mode
    - `p` Toggle play/pause
    - `k` Stop
    - `q` Add all songs in search result to queue
    - `n` Move to next song
    - `w` Clear the current queue
    - `s` Shuffle queued songs (Note: If this hangs, try running `stty -ixon` in your terminal and restarting `tuijam`)
    - `t` Thumbs down the currently playing song
    - `shift-t` Thumbs up the currently playing song
    - `shift-r` View recently played songs



# Thanks
TUIJam was heavily inspired by the
[gpymusic](https://github.com/christopher-dG/gpymusic) project, and, of course,
could not exists without the great
[gmusicapi](https://github.com/simon-weber/gmusicapi).

This project is neither affiliated with nor endorsed by Google.
