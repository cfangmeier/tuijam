from os.path import join, expanduser
import gettext
_ = gettext.gettext

__version__ = "0.7.1"
CONFIG_DIR = join(expanduser("~"), ".config", "tuijam")
CONFIG_FILE = join(CONFIG_DIR, "config.yaml")
LOG_FILE = join(CONFIG_DIR, "log.txt")
HISTORY_FILE = join(CONFIG_DIR, "hist.json")
QUEUE_FILE = join(CONFIG_DIR, "queue.json")
CRED_FILE = join(CONFIG_DIR, "google_oauth.cred")
LOCALE_DIR = join(CONFIG_DIR, "lang")
