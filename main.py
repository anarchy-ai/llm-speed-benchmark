import threading
from concurrent.futures import ThreadPoolExecutor
import torch
import time
import json
import os
import sys
import copy
import gc

current_script_path = os.path.dirname(os.path.abspath(__file__))
subdir_path = os.path.join(current_script_path, "src")
sys.path.append(subdir_path)

import hw
import hf

def gather_metrics(stop_event):
    metrics = {}
    while not stop_event.is_set():
        timestamp = str(time.time())
        print(f"logging {timestamp}")
        metrics[timestamp] = hw.get_all()
    print("COMPLETED METRICS GATHERING")
    return {
        "static": hw.get_all(True),
        "history": metrics
    }

def run_llm():
    print(f"starting running LLM model...")
    gc.disable()
    start_time = time.time()
    result = hf.run_llm("bigscience/bloom-560m", "Hello World!", "", {
        "max_length": 50,
        "temperature": 0.9,
        "top_k": 50,
        "top_p": 0.9,
        "num_return_sequences": 1
    })
    end_time = time.time()
    
    # delete cachue and variables to free up resources for better metrics collecting
    final_result = copy.deepcopy(result)
    gc.collect()
    gc.enable()
    del result
    torch.cuda.empty_cache()

    print(f"...completed running LLM model")
    return {
        "model_output": final_result,
        "start_time": start_time,
        "end_time": end_time
    }

# event object used to signal when to stop gathering metrics
stop_event = threading.Event()

if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=2) as executor:
        metrics_future = executor.submit(gather_metrics, stop_event)
        
        # pre-model run pause for performace gathering
        time.sleep(5)
        
        llm_future = executor.submit(run_llm)

        # get results from model run
        llm_results = llm_future.result()
        
        # post-model run pause for performace gathering
        time.sleep(20)

        # tell metrics collector to stop
        stop_event.set()

        # get results from metrics collector
        metrics_results = metrics_future.result()

        # print results
        x = {
            "llm": llm_results,
            "metrics": metrics_results
        }
        print(json.dumps(x, indent=4, ensure_ascii=False))
