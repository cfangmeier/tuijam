from os.path import join, expanduser

__version__ = "0.5.1"
CONFIG_DIR = join(expanduser("~"), ".config", "tuijam")
CONFIG_FILE = join(CONFIG_DIR, "config.yaml")
LOG_FILE = join(CONFIG_DIR, "log.txt")
HISTORY_FILE = join(CONFIG_DIR, "hist.json")
QUEUE_FILE = join(CONFIG_DIR, "queue.json")
