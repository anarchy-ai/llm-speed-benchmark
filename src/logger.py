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

def info(msg, print_it=False):
    logging.info(msg)
    if print_it:
        print(msg)

def warning(msg, print_it=False):
    logging.warning(msg)
    if print_it:
        print(msg)

def error(msg, print_it=False):
    logging.error(msg)
    if print_it:
        print(msg)

def critical(msg, print_it=False):
    logging.critical(msg)
    if print_it:
        print(msg)
