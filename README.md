# BenchLLM

<p align="center">
  <img width="300" src="./assets/docs/logo.png">
</p>

🚧 BenchLLM is currently in beta (v0). Please do not use this in production, or use it at your own risk. We're still ironing out some kinks and improving functionality. If you encounter any bugs or have suggestions, kindly report them under ISSUES. Your feedback is invaluable!

## About

BenchLLM is a benchmarking tool for assessing LLM models' performance across different hardware platforms. Its ultimate goal is to compile a comprehensive dataset detailing LLM models' performance on various systems, enabling users to more effectively choose the right LLM model(s) for their projects.

## Limtations

BenchLLM is on v0, so it has limitations:
- Only designed to run on debian based operating systems, aka it's not designed to run on Windows. This is because BenchLLM uses neofetch and nvidia-smi to gather metrics under the hood and the filepath logic is based on unix operating systems.
- Due to how metrics are recorded, it can take the metrics collector up to 1 second to do a collection. This means that, at the fast, we can collect hardware metrics every 1 second.
- BenchLLM only uses HuggingFace to load and run models. This works for now, but the goal is to have BenchLLM support muliple frameworks, not just HuggingFace.
- Currently, all models are ran though the logic presented in the run_llm() function, located in src/hf.py, where the functions AutoTokenizer() and AutoModelForCausalLM() are used to load and run a model. This works but it limits how we can config/optmize specific models. Knowing this, the goal is to create seperate classes for each popular model and utilize HuggingFace's model specifc classes, like LlamaTokenizer & LlamaForCausalLM, instead.
- BenchLLM only gathers general, high level, metrics. In the future, we would like to gather lower level metrics. We think this can partly be done using Pytorch's [porfiler wrapper](https://pytorch.org/tutorials/recipes/recipes/profiler_recipe.html).

## Setup

1. Create and activate python environment:
    ```
    python3 -m venv env
    source env/bin/activate
    ```

2. Install package dependencies (using APT):
    ```
    apt -y update
    apt install -y vim
    apt install -y neofetch
    ```

3. Install python dependencies:
    ```
    pip3 install transformers
    pip3 install psutil
    pip3 install gputil
    pip3 install tabulate
    pip3 install sentencepiece
    pip3 install protobuf
    ```

4. Install Pytorch (to determine how to install Pytorch for your system, checkout their tool on: https://pytorch.org/):
    ```
    # install pytorch stable build, for linux, using CUDA 12.1:
    pip3 install torch torchvision torchaudio
    ```

5. (optional) If you are using models like LLAMA, you will need a HuggingFace access token. Setup your access token [HERE](https://huggingface.co/settings/tokens) then save your token to your console by running the following command:
    ```
    huggingface-cli login
    ```

## How To Run

1. Complete the steps listed in the __Setup__ section.

2. Set your parameters for the run in the config.json file. An example config.json file is provided, these are what the parameters mean:
    ```
    {
      "model": "bigscience/bloom-560m",   # the model's path/repo on HuggingFace (https://huggingface.co/models)
      "prompt": "Hello World!",           # the prompt you want to input into the LLM model
      "device": "cuda:0",                 # the device you want to run the LLM model on (GPU/CPU)
      "max_length": 50,                   # the maximun length of the generated tokens
      "temperature": 0.9,                 # temperatue value for the LLM model
      "top_k": 50,                        # top-k value for the LLM model
      "top_p": 0.9,                       # top-p value for the LLM model
      "num_return_sequences": 1,          # the number of independently ran instances of the model
      "time_delay": 0,                    # the time delay (seconds) the metrics-collecter will wait per interation
      "model_start_pause": 1,             # the time (seconds) the test will wait BEFORE running the LLM model
      "model_end_pause": 1                # the time (seconds) the test will wait AFTER the LLM model is done running
    } 
    ```

3. Run the script (pick one option)
    ```
    # run one benchmark
    python3 run.py

    # run more then one benchmark (in this case 3)
    python3 run.py --loops 3
    ```

4. After the benchmark is done running, check out the final results in a file that should look something like this:
    ```
    report_8b7ada70-96d9-484a-93fb-c5c9ca92d15d.json
    ```

## Great Sources:
- Great datasets of prompts (if you can't come up with any):
  - https://github.com/f/awesome-chatgpt-prompts/tree/main
  - https://huggingface.co/datasets/bigscience/P3
  - https://www.kaggle.com/datasets/ratthachat/writing-prompts
- Learn more about LLM parameters: https://huggingface.co/docs/transformers/main_classes/text_generation#transformers.GenerationConfig
- Great benchmark to benchmark cloud-based LLM models: https://github.com/ray-project/llmperf
- Cool LLM intelligence leadboards:
    - https://fasteval.github.io/FastEval/
    - https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard
