import json
import os
import util

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
SETTING = util.read_json(os.path.join(ROOT_DIR, "config.json"))["supported_frameworks"]

def execute_llm(framework, model_name=None, prompt=None, device=None, dtype=None, model_params={}): 
    if framework not in SETTING.keys():
        raise Exception(f"framework {framework} is not supported!")
    
    if framework == "huggingface":
        import hf
        return hf.run_llm(model_name=model_name, input=prompt, device=device, dtype=dtype, model_params=model_params)
    
    if framework == "llm-vm":
        import llmvm
        return llmvm.run_llm(model_name=model_params, prompt=prompt, model_params={})
    
    raise Exception(f"the logic is off in {execute_llm.__name__}()")
