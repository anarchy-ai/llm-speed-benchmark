from transformers import AutoTokenizer
from llm_vm.client import Client
import json
import time

models = {
    "pythia": "EleutherAI/pythia-70m-deduped",
    "opt": "facebook/opt-350m",
    "bloom": "bigscience/bloom-560m",
    "neo": "EleutherAI/gpt-neo-1.3B",
    "smallorca": "Open-Orca/LlongOrca-7B-16k",
    "orca": "Open-Orca/LlongOrca-13B-16k",
    "mistral": "Open-Orca/Mistral-7B-OpenOrca",
    "platypus": "Open-Orca/OpenOrca-Platypus2-13B",
    "llama": "openlm-research/open_llama_3b_v2",
    "llama2": "meta-llama/Llama-2-7b-hf",
    "codellama-7b": "codellama/CodeLlama-7b-hf",
    "codellama-13b": "codellama/CodeLlama-13b-hf",
    "codellama-34b": "codellama/CodeLlama-34b-hf",
    "flan": "google/flan-t5-small",
    "bert": None,
    "gpt": None,
    "gpt4": None,
    "chat_gpt": None,
    "quantized-llama2-7b-base": "TheBloke/Llama-2-7B-GGML",
    "quantized-llama2-13b-base": "TheBloke/Llama-2-13B-GGML",
    "llama2-7b-chat-Q4": "TheBloke/Llama-2-7B-Chat-GGML",
    "llama2-7b-chat-Q6": "TheBloke/Llama-2-7B-Chat-GGML",
    "llama2-13b-chat-Q4": "TheBloke/Llama-2-13B-Chat-GGML",
    "llama2-13b-chat-Q6": "TheBloke/Llama-2-13B-Chat-GGML",
    "llama2-7b-32k-Q4": "TheBloke/Llama-2-7B-32K-Instruct-GGML"
}

def count_tokens(model_name, text):
    # Load the tokenizer for the specified model
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    # Encode the text using the loaded tokenizer
    encoded_input = tokenizer(text)

    # Calculate the number of tokens by counting the input IDs
    num_tokens = len(encoded_input['input_ids'])

    return num_tokens

def run(model_name, prompt):
    if model_name not in models:
        raise Exception("model {} is NOT supported in LLM-VM".format(model_name))
    if type(models[model_name]) != str:
        raise Exception("model {} is a close-sourced, API based, model".format(model_name))
    if type(prompt) != str or len(prompt) == 0:
        raise Exception("prompt MOST be type str and have a length greater then 0")
    
    huggingface_path = models[model_name]
    tokens = count_tokens(huggingface_path, prompt)

    client = Client(big_model=str(model_name))
    start_time = time.time()
    response=client.complete(prompt=prompt)
    runtime = time.time() - start_time

    return {
        "model_name": model_name,
        "model_path": huggingface_path,
        "runtime": runtime,
        "response": response,
        "prompt": prompt,
        "tokens": tokens,
        "tokens/sec": tokens / runtime
    }

# main function calls
output = run("bloom", "hello world")
print(json.dumps(output, indent=4))
