import subprocess
import time
import os
import signal
import uuid
import sys
import json

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
import logger
import util
import hf
import hw

ID = str(uuid.uuid4())

logger.info(f"This performance run's ID is {ID}")

# Get the current script path
current_script_path = os.path.dirname(os.path.abspath(__file__))

config_path = os.path.join(current_script_path, "config.json")
config = util.read_json(config_path)
logger.info(f"Loaded config file {config_path} for this benchmark run, with the following configuration: {config}")

env_path = os.path.join(current_script_path, "env/bin/python3")
if os.path.isfile(env_path) == False:
    msg = f"[{ID}] python environment {env_path} does not exist, please create it!"
    logger.critical(msg, True)
    sys.exit(1)

logger.info(f"[{ID}] checking if model exists and is downloaded locally...")
local_hf_exists = hf.get_hf_model(str(config["model"]))
if local_hf_exists == False:
    logger.critical(f"[{ID}] failed to download model {config['model']}, please look into this, existing...")
    sys.exit(1)

################################################################################################

logger.info(f"[{ID}] Starting metrics collector...", True)
try:
    collecting_process = subprocess.Popen([env_path, os.path.join(current_script_path, "metrics.py"), 
                                        '--time-delay', str(config["time_delay"]),
                                        "--uuid", str(ID)
                                        ])
    logger.info(f"[{ID}] the metrics collector is running with a PID of {collecting_process.pid}", True)
except Exception as err:
    logger.error(f"[{ID}] failed to run metric collector due to error: {err}, so existing...", True)
    sys.exit(1)

################################################################################################

logger.info(f"[{ID}] Initiated {config['model_start_pause']} pre model start to gather hardware metrics BEFORE the model is activated", True)
time.sleep(config["model_start_pause"])

################################################################################################

logger.info(f"[{ID}] Activating model {config['model']} with following parameters: {str(config)}", True)
try:
    model_running_process = subprocess.Popen([env_path, os.path.join(current_script_path, "model.py"), 
                                            "--max_length", str(config["max_length"]),
                                            "--temperature", str(config["temperature"]),
                                            "--top_k", str(config["top_k"]),
                                            "--top_p", str(config["top_p"]),
                                            "--num_return_sequences", str(config["num_return_sequences"]),
                                            "--uuid", str(ID),
                                            "--prompt", str(config["prompt"]),
                                            "--model", str(config["model"]),
                                            "--device", str(config["device"])
                                            ])
    logger.info(f"[{ID}] model {config['model']} is running with a PID of {model_running_process.pid}", True)
except Exception as err:
    logger.error(f"[{ID}] failed to run model {config['model']} due to error: {err}", True)
    logger.error(f"[{ID}] attempting to kill metrics collector due to model failing to run", True)
    collecting_process.send_signal(signal.SIGTERM)
    collecting_process.wait()
    sys.exit(1)

################################################################################################

logger.info(f"[{ID}] waiting for model {config['model']} to finish running...", True)
model_running_process.wait()
logger.info(f"[{ID}] model {config['model']} finished running! no longer waiting!", True)

logger.info(f"[{ID}] Initiated {config['model_start_pause']} post model end to gather hardware metrics AFTER the model has completed it's run time", True)
time.sleep(config["model_end_pause"])

logger.info(f"[{ID}] Kill signal has been sent to metrics collector, is should finish running soon...")
collecting_process.send_signal(signal.SIGTERM)
collecting_process.wait()

exported_files_paths = util.get_id_files(ID, current_script_path)
if len(exported_files_paths) != 2:
    logger.critical(f"[{ID}] The metrics-collector and model have completed their runs BUT there are only {len(exported_files_paths)} exported data files NOT 2, look into this, existing...", True)
    sys.exit(1)

# get full file paths for metrics data file & model data file
metrics_data = None
model_data = None
for file in exported_files_paths:
    if "_metrics.json" in file:
        metrics_data = file
    elif "_model.json" in file:
        model_data = file
    else:
        logger.critical(f"[{ID}] Of the expected data output files, this file has an unexpected file 'extension': {file}")
        sys.exit(1)

final_data_path = f"report_{ID}.json"
final_dataset = {
    "hardware": hw.get_all(static_only=True),
    "model": util.read_json(model_data),
    "metric": util.read_json(metrics_data)
}

# export file data/results
util.write_json(final_data_path, final_dataset)

# delete exported data files from metrics-collector and model-runner
# NOTE: we have to be careful here
util.delete_file(model_data)
util.delete_file(metrics_data)

logger.warning(f"[{ID}] Deleted exported sub-data files: {model_data} & {metrics_data}", True)
logger.info(f"[{ID}] Created final report from this performance benchmark to file: {final_data_path}", True)

