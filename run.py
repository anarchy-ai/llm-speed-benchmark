import subprocess
import time
import os
import signal
import uuid
import sys
import json

def get_id_files(id, dir_path):
    if os.path.exists(dir_path) == False or os.path.isdir(dir_path) == False:
        raise Exception(f"dir path {dir_path} does not exist!")
    files = []
    for f in os.listdir(dir_path):
        full_path = os.path.join(dir_path, f)
        if os.path.isfile(full_path) and (str(id) in f) and (".json" in full_path):
            files.append(full_path)
    return files

def delete_file(file_path):
    if os.path.isfile(file_path):
        try:
            os.remove(file_path)
            print(f"deleted file {file_path}")
        except Exception as e:
            print(f"error! failed to delete file {file_path}")
    else:
        print(f"file {file_path} does not exist")

def read_json(path):
    with open(str(path)) as file:
        content = json.load(file)
    return content

def write_json(path, data):
    with open(str(path), "w") as file:
        json.dump(data, file, indent=4)

config = {
    "model": "bigscience/bloom-560m",
    "prompt": "Hello World!",
    "device": "cuda:0",
    "max_length": 50,
    "temperature": 0.9,
    "top_k": 50,
    "top_p": 0.9,
    "num_return_sequences": 1,

    "time_delay": 0,
    "model_start_pause": 5,
    "model_end_pause": 5
}

ID = str(uuid.uuid4())

# Get the current script path
current_script_path = os.path.dirname(os.path.abspath(__file__))

################################################################################################

# Path to the virtual environment's Python executable
env_path = os.path.join(current_script_path, "env/bin/python3")

# Start the metrics.py script using the Python executable from the virtual environment with the time delay argument
collecting_process = subprocess.Popen([env_path, os.path.join(current_script_path, "metrics.py"), 
                                       '--time-delay', str(config["time_delay"]),
                                       "--uuid", str(ID)
                                    ])

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

exported_files_paths = get_id_files(ID, current_script_path)
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
    "model": read_json(model_data),
    "metric": read_json(metrics_data)
}

write_json(final_data_path, final_dataset)

print(f"Created final report: {final_data_path}")

# TODO: this might now be safe...
delete_file(model_data)
delete_file(metrics_data)


