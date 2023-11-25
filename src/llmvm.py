from transformers import AutoTokenizer
from llm_vm.client import Client
import torch
import time
import sys
import os
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
sys.path.extend([ROOT_DIR, os.path.join(ROOT_DIR, "src")])
import util

SETTING = util.read_json(os.path.join(ROOT_DIR, "config.json"))

# NOTE: are of 11-24-2023 these are the current models supported in LLM-VM
SUPPORTED_MODELS = SETTING["supported_frameworks"]["llm-vm"]["supported_models"]


def get_current_llmvm_commit():
    try:
        path = os.path.join(ROOT_DIR, "src/LLM-VM/.git")
        output = subprocess.check_output("git log | head -n 1 | awk '{print $2}'", shell=True, cwd=path, universal_newlines=True)
        output = str(output).replace("\n", "").replace(" ", "")
        return output
    except:
        return ""

"""
ABOUT:
    This function contains the official logic used by LLM-VM to pick a device (GPUs or CPUs)
NOTES:
    Update this function as need be, LLM-VM is constantly changing
LAST-DATE:
    November 15, 2023
SOURCE:
    https://github.com/anarchy-ai/LLM-VM/blob/main/src/llm_vm/onsite_llm.py
    ~lines 45 - 49
"""
def llmvm_device_picker():
    device = None
    if torch.cuda.device_count() > 1:
        device = [f"cuda:{i}" for i in range(torch.cuda.device_count())]  # List of available GPUs
    else:  # If only one GPU is available, use cuda:0, else use CPU
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
    return device

def count_tokens(model_name, text):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    encoded_input = tokenizer(text)
    num_tokens = len(encoded_input['input_ids'])
    return num_tokens

def run_llm(model_name, prompt, model_params={}):
    global SUPPORTED_MODELS

    if model_name not in SUPPORTED_MODELS:
        raise Exception("model {} is NOT supported in LLM-VM".format(model_name))
    if type(SUPPORTED_MODELS[model_name]) != str:
        raise Exception("model {} is a close-sourced, API based, model".format(model_name))
    if type(prompt) != str or len(prompt) == 0:
        raise Exception("prompt MOST be type str and have a length greater then 0")
    
    temp = model_params.get("temperature")
    if temp == None:
        """
        ABOUT:
            This is the default value for temperature in LLM-VM at the moment
        LAST-DATE:
            November 24, 2023
        SOURCE:
            https://github.com/anarchy-ai/LLM-VM/blob/main/src/llm_vm/client.py
            ~lines 109
        """
        temp = 0

    client = Client(big_model=str(model_name))
    
    start_time = time.time()
    
    # NOTE: we only accept temperatuer for now
    response=client.complete(prompt=prompt, temperature=temp)
    
    runtime = time.time() - start_time

    device = llmvm_device_picker()
    huggingface_path = SUPPORTED_MODELS[model_name]
    tokens_in = count_tokens(huggingface_path, prompt)
    tokens_out = count_tokens(huggingface_path, response["completion"])
    llmvm_commit = get_current_llmvm_commit()

    return {
        "model_name": model_name,
        "model_path": huggingface_path,
        "runtime_secs": runtime,
        "prompt": prompt,
        "response": response,
        "tokens": {
            "input": tokens_in,
            "output": tokens_out
        },
        "tokens_out/sec": tokens_out / runtime,
        "device": str(device),
        "llm_vm_commit": llmvm_commit,
        "model_params": {
            "temperature": temp
        }
    }
