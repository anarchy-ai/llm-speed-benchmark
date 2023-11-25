import json
import os
import util

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

SUPPORTED_FRAMEWORKS = [
    "huggingface",
    "llm-vm"
]

# NOTE: are of 11-24-2023 these are the current models supported in LLM-VM
llmvm_supported_models = {
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

def execute_llm(framework, model_name=None, prompt=None, device=None, dtype=None, model_params={}): 
    if framework not in SUPPORTED_FRAMEWORKS:
        raise Exception(f"framework {framework} is not supported!")
    
    if framework == "huggingface":
        import hf
        return hf.run_llm(model_name=model_name, input=prompt, device=device, dtype=dtype, model_params=model_params)
    
    if framework == "llm-vm":
        import llmvm
        return llmvm.run_llm(model_name=model_name, prompt=prompt, model_params={}, supported_models=llmvm_supported_models)
    
    raise Exception(f"the logic is off in {execute_llm.__name__}()")
