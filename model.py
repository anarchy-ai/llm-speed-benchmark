import torch
import time
import json
import os
import sys
import copy
import gc
import signal
import argparse
import uuid

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))
import hf

parser = argparse.ArgumentParser(description='run hardware performance/metrics collector')

"""
November 21, 2023
The default values and help values for most of these parameters were taken directly from huggingface documentation:
https://huggingface.co/docs/transformers/main_classes/text_generation#transformers.GenerationConfig
"""
parser.add_argument('--max_length', type=int, default=20, help='The maximum length the generated tokens can have. Corresponds to the length of the input prompt + max_new_tokens. Its effect is overridden by max_new_tokens, if also set.')
parser.add_argument('--temperature', type=float, default=1.0, help='The value used to modulate the next token probabilities.')
parser.add_argument('--top_k', type=int, default=50, help='The number of highest probability vocabulary tokens to keep for top-k-filtering.')
parser.add_argument('--top_p', type=float, default=1.0, help='If set to float < 1, only the smallest set of most probable tokens with probabilities that add up to top_p or higher are kept for generation.')
parser.add_argument('--num_return_sequences', type=int, default=1, help='The number of independently computed returned sequences for each element in the batch.')

parser.add_argument('--uuid', type=str, default=str(uuid.uuid4()), help='The UUID for the collection')
parser.add_argument('--prompt', type=str, default="Hello World", help='Text prompt for the LLM model to respond too')
parser.add_argument('--model', type=str, default="", help='Huggingface repo/path to LLM model')
parser.add_argument('--device', type=str, default="", help='Device to run the model on, this can be "cpu" or "cuda:N"')

# signal handler
def signal_handler(signum, frame):
    sys.exit(1)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    args = parser.parse_args()

    print(f"{args.uuid} - model running - running model with following parameters {str(args)}")

    if args.model == "":
        sys.exit(1)

    # local_hf_exists = hf.get_hf_model(args.model)
    # if local_hf_exists == False:
    #     sys.exit(1)

    start_time = time.time()
    
    output = hf.run_llm(args.model, args.prompt, args.device, {
        "max_length": args.max_length,
        "temperature": args.temperature,
        "top_k": args.top_k,
        "top_p": args.top_p,
        "num_return_sequences": args.num_return_sequences
    })

    end_time = time.time()

    output["run_period"] = {
        "started": start_time,
        "ended": end_time
    }

    # delete cachue and variables to free up resources for better metrics collecting
    final_result = copy.deepcopy(output)
    gc.collect()
    gc.enable()
    del output
    if "cuda" in args.model:
        torch.cuda.empty_cache()

    filepath = f"{args.uuid}_model.json"
    with open(str(filepath), "w") as file:
        json.dump(final_result, file, indent=4)
    
    print(f"{args.uuid} - model running - saved output for model run to file {filepath}")
