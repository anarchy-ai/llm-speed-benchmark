from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import snapshot_download
from huggingface_hub import HfApi
import torch
import time
import os

import logger

def count_tokens(model_name, text):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    encoded_input = tokenizer(text)
    num_tokens = len(encoded_input['input_ids'])
    return num_tokens

def validate_options(options, valid_keys):
    user_keys = set(options.keys())
    return user_keys.issubset(valid_keys)

def run_llm(model_name, input, device="", model_params={}):
    valid_model_params = {"max_length", "temperature", "top_k", "top_p", "num_return_sequences"}
    if model_params != {} and validate_options(model_params, valid_model_params) == False:
        raise Exception(f"model_params only accepts the following keys: {model_params.keys()}")
    
    # TODO: currently this function only supports one GPU, the goal will be to update this to support muliple GPU(s)
    if "cuda:" not in device and device != "cpu" and device != "":
        raise Exception(f"device can only be type cuda:N, cpu, or auto")
    
    """
    November 21, 2023
    Default model_params for generate() function
    https://huggingface.co/docs/transformers/main_classes/text_generation#transformers.GenerationConfig
    """
    default_model_params = {
        "max_length": 20,
        "temperature": 1.0,
        "top_k": 50,
        "top_p": 1.0,
        "num_return_sequences": 1
    }
    
    if device == "":
        device = "cuda:0" if torch.cuda.is_available() else "cpu"
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name).to(device)

    model_dtype = next(model.parameters()).dtype

    inputs = tokenizer(str(input), return_tensors="pt").to(device)

    for key in model_params:
        if model_params[key] != None:
            default_model_params[key] = model_params[key]

    start_time = time.time()

    generated_sequences = model.generate(
        inputs["input_ids"],
        max_length=default_model_params["max_length"],
        temperature=default_model_params["temperature"],
        top_k=default_model_params["top_k"],
        top_p=default_model_params["top_p"],
        num_return_sequences=default_model_params["num_return_sequences"]
    )

    runtime = time.time() - start_time

    response = tokenizer.decode(generated_sequences[0])
    device = generated_sequences.device

    tokens_in = inputs["input_ids"].size(1) * default_model_params["num_return_sequences"]
    tokens_out = generated_sequences.size(1) * default_model_params["num_return_sequences"]

    return {
        "model_name": model_name,
        "runtime_secs": runtime,
        "prompt": input,
        "response": response,
        "tokens": {
            "input": tokens_in,
            "output": tokens_out
        },
        "tokens_out/sec": tokens_out / runtime,
        "device": str(generated_sequences.device),
        "model_params": {
            "dtype": str(model_dtype),
            "max_length": default_model_params["max_length"],
            "temperature": default_model_params["temperature"],
            "top_k": default_model_params["top_k"],
            "top_p": default_model_params["top_p"],
            "num_return_sequences": default_model_params["num_return_sequences"]
        }
    }

# Check if hf model exists and download hf model to local disk if needed
def get_hf_model(hf_repo_path):
    # quick & dirty way to check if a hf model/repo exists
    api = HfApi()
    try:
        api.list_repo_files(hf_repo_path)
    except Exception as err:
        logger.error(f"failed to check if model {hf_repo_path} exists on HuggingFace due to error: {err}")
        return False
    
    # quick & dirty way to check if hf model/repo has been downloaded, saved to cache directory
    cache_dir = os.path.join(os.path.expanduser('~'), ".cache/huggingface/hub/")
    model_cache_dir = os.path.join(cache_dir, "models--{}".format(hf_repo_path.replace("/", "--")))
    if os.path.isdir(model_cache_dir):
        logger.info(f"model {hf_repo_path} already exists in directory {model_cache_dir}")
        return True
    
    # download hf model/repo if it's not downloaded
    try:
        snapshot_download(repo_id=hf_repo_path, repo_type="model", token=True)
        logger.info(f"downloaded model {hf_repo_path}")
        return True
    except Exception as err:
        logger.error(f"{err}")
        return False
