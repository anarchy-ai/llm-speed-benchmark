from datetime import datetime, timezone
import logging
import time
import os

colors = {
    'black': '\033[30m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'magenta': '\033[35m',
    'cyan': '\033[36m',
    'white': '\033[37m',
    'bright_black': '\033[90m',
    'bright_red': '\033[91m',
    'bright_green': '\033[92m',
    'bright_yellow': '\033[93m',
    'bright_blue': '\033[94m',
    'bright_magenta': '\033[95m',
    'bright_cyan': '\033[96m',
    'bright_white': '\033[97m',
    'reset': '\033[0m',
}

# determine and set the path for the log file
filepath = os.path.dirname(os.path.abspath(__file__))
filepath = "/".join(filepath.split("/")[:-1])
filepath = os.path.join(filepath, "events.log")

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s:%(funcName)s:%(lineno)d [%(levelname)s] %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S %z',
                    filename=filepath,
                    filemode='a')

logging.Formatter.converter = time.gmtime

def logger_printer(msg, sev=None):
    sev = str(sev).lower()

    timestamp = datetime.now(timezone.utc).strftime("%m-%d-%Y %H:%M:%S.%f UTC")
    timestamp = f"{timestamp} ({datetime.utcnow().timestamp()})"

    sev_val = ""
    color_val = ""
    end_val = colors.get("reset", "")
    if sev == "info" or sev == "1":
        color_val = colors.get("green", "")
        sev_val = "INFO"
    elif sev == "warning" or sev == "2":
        color_val = colors.get("yellow", "")
        sev_val = "WARNING"
    elif sev == "error" or sev == "3":
        color_val = colors.get("magenta", "")
        sev_val = "ERROR"
    elif sev == "critical" or sev == "4":
        color_val = colors.get("red", "")
        sev_val = "CRITICAL"
    else:
        color_val = None
        sev_val = "NOTSET"

    if color_val == None:
        color_val = ""
        end_val = ""
     
    print(f"{color_val}{timestamp} [{sev_val}] - {msg}{end_val}" )

def info(msg, print_it=False):
    logging.info(msg)
    if print_it:
        logger_printer(msg, 1)

def warning(msg, print_it=False):
    logging.warning(msg)
    if print_it:
        logger_printer(msg, 2)

def error(msg, print_it=False):
    logging.error(msg)
    if print_it:
        logger_printer(msg, 3)

def critical(msg, print_it=False):
    logging.critical(msg)
    if print_it:
        logger_printer(msg, 4)

