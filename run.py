import subprocess
import time
import os
import signal
import uuid
import sys
import json

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
import util
import hf

ID = str(uuid.uuid4())

# Get the current script path
current_script_path = os.path.dirname(os.path.abspath(__file__))

config = util.read_json(os.path.join(current_script_path, "config.json"))

################################################################################################

# Path to the virtual environment's Python executable
env_path = os.path.join(current_script_path, "env/bin/python3")

# TODO: only continue if model is installed!
local_hf_exists = hf.get_hf_model(str(config["model"]))
if local_hf_exists == False:
    print(f"FAILED TO DOWNLOAD MODEL, EXISTING...")
    sys.exit(1)

# Start the metrics.py script using the Python executable from the virtual environment with the time delay argument
collecting_process = subprocess.Popen([env_path, os.path.join(current_script_path, "metrics.py"), 
                                       '--time-delay', str(config["time_delay"]),
                                       "--uuid", str(ID)
                                    ])

################################################################################################

time.sleep(config["model_start_pause"])

################################################################################################

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

################################################################################################

print("Waiting......")
model_running_process.wait()
print(".....Waiting Done!!!")

time.sleep(config["model_end_pause"])

# # Allow the subprocess to run for a certain amount of time
# time.sleep(10)

# Now signal the subprocess to terminate
collecting_process.send_signal(signal.SIGTERM)

# Wait for the process to terminate
collecting_process.wait()

# # # Output the PID and the termination status
# # print(f"PID of the process: {collecting_process.pid}")
# # print(f"Process terminated with exit code: {collecting_process.returncode}")

exported_files_paths = util.get_id_files(ID, current_script_path)
if len(exported_files_paths) != 2:
    sys.exit(1)

metrics_data = None
model_data = None
for file in exported_files_paths:
    if "_metrics.json" in file:
        metrics_data = file
    elif "_model.json" in file:
        model_data = file
    else:
        sys.exit(1)

final_data_path = f"report_{ID}.json"
final_dataset = {
    "model": util.read_json(model_data),
    "metric": util.read_json(metrics_data)
}

util.write_json(final_data_path, final_dataset)

print(f"Created final report: {final_data_path}")

# TODO: this might now be safe...
util.delete_file(model_data)
util.delete_file(metrics_data)


