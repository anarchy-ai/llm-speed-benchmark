# anarchy-benchmarks

## Prompt Datasets To Checkout:

- https://huggingface.co/datasets/bigscience/P3
- https://www.kaggle.com/datasets/ratthachat/writing-prompts
- https://github.com/f/awesome-chatgpt-prompts/tree/main

## Setup (MacOS):

```
# create local python environment
python3 -m venv env

# activate local python environment
source env/bin/activate

# install other packages
pip3 install torch torchvision torchaudio
pip install "weaviate-client==3.*"
pip3 install pinecone-client
pip install python-dotenv

# install LLM-VM
git clone https://github.com/anarchy-ai/LLM-VM.git
cd LLM-VM
git checkout ff8ca553625e7de0c6778e721e0629ce7caf72e9
pip3 install .
cd ..
```

