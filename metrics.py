import time
import os
import sys
import json
import signal
import argparse
import uuid

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
import hw
import logger

# config arguments
parser = argparse.ArgumentParser(description='run hardware performance/metrics collector')
parser.add_argument('--time-delay', type=int, default=1, help='the time dely, in seconds, for each collection interation')
parser.add_argument('--uuid', type=str, default=str(uuid.uuid4()), help='the UUID for the collection')

# global variable to determine when the collection loop should stop
running = True

# signal handler
def signal_handler(signum, frame):
    global running
    running = False

if __name__ == "__main__":
    args = parser.parse_args()

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    logger.info(f"{args.uuid} - metrics collection has started...")

    metrics = {}
    counter = 0
    while running:
        timestamp = str(time.time())
        metrics[timestamp] = hw.get_all()
        logger.info(f"{args.uuid} - metrics collector - Collected metrics for the {counter+1} time, now waiting for {args.time_delay} sec")
        counter += 1
        time.sleep(args.time_delay)

    logger.info(f"{args.uuid} - metrics collecton has concluded!")

    filepath = f"{args.uuid}_metrics.json"
    with open(str(filepath), "w") as file:
        json.dump(metrics, file, indent=4)

    logger.info(f"{args.uuid} - metrics collector - Saved {len(metrics.keys())} data points to file {filepath}")

