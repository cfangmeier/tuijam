<p align="center">
<img src="https://raw.githubusercontent.com/cfangmeier/tuijam/master/tuijam.png"></img>
</p>

---

TUIJam seeks to make a simple, attractive, terminal-based interface to
listening to music for Google Play Music All-Access subscribers.

[![asciicast](https://asciinema.org/a/bhsWdt4M2CQwfWSjWNXBiTcqs.svg)](https://asciinema.org/a/bhsWdt4M2CQwfWSjWNXBiTcqs)

# Dependencies
* [Python >= 3.7](https://www.python.org/downloads)
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

You can customize the visual theme of TUIJam by specifying the foreground/background colors of many of the UI elements in your configuration file. You can specify named colors to use your [terminal colorscheme](http://urwid.org/manual/displayattributes.html#standard-foreground-colors) or use `#RGB` for custom colors. The default values are listed below.

```yaml
palette:
  header: ["white,underline", "default"]
  search-normal: ["white", "default"]
  search-select: ["white", "dark red"]
  region_bg-normal: ["light gray", "default"]
  region_bg-select: ["white", "default"]
  progress: ["white", "dark red"]
  progress_remaining: ["white", "dark gray"]
```

# MPRIS Support
TUIJam supports a subset of the [MPRIS](https://specifications.freedesktop.org/mpris-spec/latest/) spec to allow for external control via clients such as [playerctl](https://github.com/acrisci/playerctl). Currently, the following behavior is supported:

  - Get current song metadata (Title/Album/Artist)
  - Get player status (Playing/Paused/Stopped)
  - Play/Pause current song
  - Next/Previous Song
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
tuijam configure_last_fm
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

# Controls

The default control keys are listed below with short descriptions. However, many of these can be overridden by specifying alternative keys in the configuration file.

  - `ctrl-c` quit
  - `ctrl-p` toggle play/pause
  - `ctrl-k` stop
  - `ctrl-q` add all songs in search result to queue
  - `ctrl-n`/`right` move to next song
  - `ctrl-b`/`left` move to previous song
  - `ctrl-r` view recently played songs
  - `ctrl-w` Clear the current queue
  - `ctrl-s` shuffle queued songs (Note: If this hangs, try running `stty -ixon` in your terminal and restarting `tuijam`)
  - `ctrl-u` Thumbs up the currently playing song
  - `ctrl-d` Thumbs down the currently playing song
  - `>`/`shift-right` seek forward 10 seconds
  - `<`/`shift-left` seek backwards 10 seconds
  - `+` volume up
  - `-` volume down
  - `tab`/`shift-tab` cycle focus through search/queue/input windows
  - `\`/`ctrl-f` move to search bar
  - In search window,
    - `q` Add selected song/album to queue
    - `shift-q` Add selected song/album to the top of queue (play next)
    - `r` Create radio station around selected song/album/artist and add 50 songs from it to queue
    - `e` view information about selected song/album/artist
    - `backspace` go back in search/expand history
  - In queue window,
    - `u`/`shift-up` move selected song up in queue
    - `d`/`shift-down` move selected song down in queue
    - `shift-u`/`v`/`ctrl-up` move selected song to the top in queue
    - `shift-d`/`ctrl-down` move selected song to the bottom in queue
    - `delete`/`x` remove selected song from queue
  - In input window,
    - Type search query and press enter. Results are shown in search window.
    - Enter an empty query to view the suggested "Listen Now" stations and albums.

To customize these keys, add as many of the following entries into your config file as you want. A list indicates that multiple keys are assigned to that action.

```yaml
controls:
    queue: "q"
    queue_next: "Q"
    expand: ["e", "enter"]
    back: "backspace",
    radio: "r",
    # queue panel
    swap_up: ["u", "shift up"],
    swap_down: ["d", "shift down"],
    to_top: ["U", "ctrl up"],
    to_bottom: ["D", "ctrl down"],
    remove: ["delete", "x"],
    play_pause: " ",
    # search and queue panel
    down: "j",
    up: "k",
    expand: ["e", "enter"],
    seek_pos: [">", "shift right"],
    seek_neg: ["<", "shift left"],
    vol_up: ["+", "="],
    vol_down: ["-", "_"],
    focus_search: ["ctrl f", "/"],
    # global inputs
    # Avoid single letter/number/symb keys to work with search input focused, unless vim-mode is active.
    g_focus_next: "tab",
    g_focus_prev: "shift tab",
    g_play_pause: "ctrl p",
    g_stop: "ctrl k",
    g_play_next: ["ctrl n", "right"],
    g_play_previous: ["ctrl b", "left"],
    g_recent: "ctrl r",
    g_shuffle: "ctrl s",
    g_rate_good: "ctrl u",
    g_rate_bad: "ctrl d",
    g_clear_queue: "ctrl w",
    g_queue_all: "ctrl q",
```

There is an experimental "vim mode" which can be enabled by adding `vim_mode: true` to your config file. With this mode enabled, pressing escape will mask keys from being typed into the search bar (press `i` to re-enable typing). This makes it more convenient to have single key commands for controlling playback (e.g. instead of `ctrl-n` for next song, simply `n`).

# Translations
TUIJam supports translations! It has only English and Russian for now, but you can make your own ones.

You can grab .pot file from the repo (`tuijam/lang` folder) and work with it or:

1. Clone the repo
2. Run `python setup.py extract_messages` to generate .pot file
3. Run `python setup.py init_catalog -l <LOCALE_CODE>` to generate a new locale.
4. Update the locale with `python setup.py update_catalog -l <LOCALE_CODE> -o <LOCALE_PATH>`
5. Compile your locale with `python setup.py compile_catalog`.

`<LOCALE_CODE>` is [ICU locale ID](https://www.localeplanet.com/icu/)

User locales are supported. Copy generated .mo files to $HOME/.config/tuijam/lang/<LOCALE_CODE>/LC_MESSAGES folder. 
Notice that .po files are not supported for now.

The player's locale can be overridden by launching with LC_ALL environment variables. (`LC_ALL="en_US.UTF-8" tuijam`)

TUIJam uses Babel for locale generation. You can look [its docs](http://babel.pocoo.org/en/latest/index.html) for further information.

# Thanks
TUIJam was heavily inspired by the
[gpymusic](https://github.com/christopher-dG/gpymusic) project, and, of course,
could not exists without the great
[gmusicapi](https://github.com/simon-weber/gmusicapi).

This project is neither affiliated with nor endorsed by Google.
