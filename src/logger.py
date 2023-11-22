import logging
import time
import os

# determine and set the path for the log file
filepath = os.path.dirname(os.path.abspath(__file__))
filepath = "/".join(filepath.split("/")[:-1])
filepath = os.path.join(filepath, "events.log")

class CustomFormatter(logging.Formatter):
    converter = time.gmtime

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            s = time.strftime("%Y-%m-%d %H:%M:%S", ct)
        return "{},{}".format(s, record.created)

logging.basicConfig(level=logging.DEBUG,
                    format='[ %(asctime)s ] [ %(name)s ] [ %(levelname)s ] %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S %z',
                    filename=filepath,
                    filemode='a')

logging.Formatter.converter = time.gmtime

logger = logging.getLogger(__name__)
