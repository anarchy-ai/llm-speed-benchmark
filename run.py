import subprocess
import time
import os
import signal
import uuid
import sys

config = {
    "time_delay": 2,
    "model": "bigscience/bloom-560m",
    "prompt": "Hello World!",
    "device": "cuda:0",
    "max_length": 50,
    "temperature": 0.9,
    "top_k": 50,
    "top_p": 0.9,
    "num_return_sequences": 1
}

ID = str(uuid.uuid4())

# Get the current script path
current_script_path = os.path.dirname(os.path.abspath(__file__))

################################################################################################

# Path to the virtual environment's Python executable
env_path = os.path.join(current_script_path, "env/bin/python3")

# Time delay parameter (in seconds)
time_delay = 2

# Start the metrics.py script using the Python executable from the virtual environment with the time delay argument
collecting_process = subprocess.Popen([env_path, os.path.join(current_script_path, "metrics.py"), 
                                       '--time-delay', str(config["time_delay"]),
                                       "--uuid", str(ID)
                                    ])

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

# # Allow the subprocess to run for a certain amount of time
# time.sleep(10)

# Now signal the subprocess to terminate
collecting_process.send_signal(signal.SIGTERM)

# Wait for the process to terminate
collecting_process.wait()

# Output the PID and the termination status
print(f"PID of the process: {collecting_process.pid}")
print(f"Process terminated with exit code: {collecting_process.returncode}")
