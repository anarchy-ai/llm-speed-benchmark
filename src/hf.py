from transformers import AutoTokenizer, AutoModelForCausalLM
from huggingface_hub import snapshot_download
from huggingface_hub import HfApi
import os

"""
NAME:
    get_hf_model()

ABOUT:
    Check if hf model exists and download hf model to local disk if needed

PARAMS:
    - options.fast : not use snapshot_download() and instead use Auto model classes for minimal downloads

OUTPUTS:
    - return True if hf model was downloaded successfully
    - return True if hf model is already downloaded on the disk
    - return False if function failed to download model or an error occurred
"""
def get_hf_model(hf_repo_path, options={}):
    # quick & dirty way to check if a hf model/repo exists
    api = HfApi()
    try:
        api.list_repo_files(hf_repo_path)
    except Exception as err:
        print(f"failed to check if model {hf_repo_path} exists on HuggingFace due to error: {err}")
        return False
    
    # quick & dirty way to check if hf model/repo has been downloaded, saved to cache directory
    cache_dir = os.path.join(os.path.expanduser('~'), ".cache/huggingface/hub/")
    model_cache_dir = os.path.join(cache_dir, "models--{}".format(hf_repo_path.replace("/", "--")))
    if os.path.isdir(model_cache_dir):
        print(f"model {hf_repo_path} already exists in directory {model_cache_dir}")
        return True
    
    # download hf model/repo if it's not downloaded
    try:
        if options.get("fast") == True:
            print(f"FAST mode is enabled, utilizing Auto model classes to minimal downloads")
            tokenizer = AutoTokenizer.from_pretrained(hf_repo_path)
            model = AutoModelForCausalLM.from_pretrained(hf_repo_path)
            del tokenizer
            del model
            return True
        snapshot_download(repo_id=hf_repo_path, repo_type="model", token=True)
        return True
    except:
        return False

