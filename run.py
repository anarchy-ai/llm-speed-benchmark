import subprocess
import argparse
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

# config arguments
parser = argparse.ArgumentParser(description='Run performance benchmark for an LLM model')
parser.add_argument('--name', type=str, default=None, help='name of this performance benchmark run')
parser.add_argument('--config_path', type=str, default=None, help='path to config file that will be used for the performance benchmark')
parser.add_argument('--loops', type=int, default=1, help='number of times the performance benchmark will be ran (default=1)')

def main(name=None, config_path=None):
    ID = str(uuid.uuid4())

    logger.info(f"This performance run's ID is {ID} with name={name}", True)

    # Get the current script path
    current_script_path = os.path.dirname(os.path.abspath(__file__))

    if config_path == None:
        config_path = os.path.join(current_script_path, "config.json")
    elif os.path.isfile(str(config_path)) == False:
        logger.error(f"[{ID}] Config path {config_path} does not exist! Existing...", True)
        sys.exit(1)

    config = util.read_json(config_path)
    logger.info(f"[{ID}] Loaded config file {config_path} for this benchmark run, with the following configuration: {config}", True)

    env_path = os.path.join(current_script_path, "env/bin/python3")
    if os.path.isfile(env_path) == False:
        logger.critical(f"[{ID}] python environment {env_path} does not exist, please create it!", True)
        sys.exit(1)

    logger.info(f"[{ID}] checking if model exists and is downloaded locally...", True)
    local_hf_exists = hf.get_hf_model(str(config["model"]))
    if local_hf_exists == False:
        logger.critical(f"[{ID}] failed to download model {config['model']}, please look into this, existing...", True)
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

    logger.info(f"[{ID}] Initiated {config['model_start_pause']} second pre model start to gather hardware metrics BEFORE the model is activated", True)
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
                                                "--device", str(config["device"]),
                                                "--dtype", str(config["dtype"])
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

    logger.info(f"[{ID}] Initiated {config['model_start_pause']} second post model end to gather hardware metrics AFTER the model has completed it's run time", True)
    time.sleep(config["model_end_pause"])

    logger.info(f"[{ID}] Kill signal has been sent to metrics collector, is should finish running soon...", True)
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
            logger.critical(f"[{ID}] Of the expected data output files, this file has an unexpected file 'extension': {file}", True)
            sys.exit(1)

    final_data_path = f"report_{ID}.json"
    if name != None:
        final_data_path = f"{name}_{final_data_path}"

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
    logger.info(f"[{ID}] ==> Created final report from this performance benchmark to file: {final_data_path}", True)

    # TODO: returning the final output data's filepath for now
    return final_data_path

if __name__ == "__main__":
    args = parser.parse_args()

    loops = int(args.loops)
    if loops < 1:
        raise Exception(f"loops MOST be greater then or equal to 1!")

    if loops <= 1:
        main(name=args.name, config_path=args.config_path)
        sys.exit(0)

    all_filepaths = []
    for i in range(int(args.loops)):
        i_name = f"run_{i}"
        if args.name != None:
            i_name = f"{args.name}_{i_name}"
        logger.info(f"Run {i+1}/{args.loops} for performance benchmark", True)
        filepath = main(name=i_name, config_path=args.config_path)
        all_filepaths.append(filepath)
    
    logger.info(f"==> Muli-Run completed for performance benchmark. A total of {args.loops} runs we done and the following data was exported: {all_filepaths}", True)
    sys.exit(0)
