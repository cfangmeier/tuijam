from os.path import join, expanduser

__version__ = "0.6.3"
CONFIG_DIR = join(expanduser("~"), ".config", "tuijam")
CONFIG_FILE = join(CONFIG_DIR, "config.yaml")
LOG_FILE = join(CONFIG_DIR, "log.txt")
HISTORY_FILE = join(CONFIG_DIR, "hist.json")
QUEUE_FILE = join(CONFIG_DIR, "queue.json")
CRED_FILE = join(CONFIG_DIR, "google_oauth.cred")
