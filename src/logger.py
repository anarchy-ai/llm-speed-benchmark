from datetime import datetime
import logging
import time
import os

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

def logger_printer(msg):
    utc_timestamp = datetime.utcnow().timestamp()
    print(f"{utc_timestamp} - {msg}")

def info(msg, print_it=False):
    logging.info(msg)
    if print_it:
        logger_printer(msg)

def warning(msg, print_it=False):
    logging.warning(msg)
    if print_it:
        logger_printer(msg)

def error(msg, print_it=False):
    logging.error(msg)
    if print_it:
        logger_printer(msg)

def critical(msg, print_it=False):
    logging.critical(msg)
    if print_it:
        logger_printer(msg)
