# install the latest LLM-VM and some of it's deps

pip3 install torch torchvision torchaudio
pip install "weaviate-client==3.*"
pip3 install pinecone-client
pip install python-dotenv
pip install hnswlib

git clone https://github.com/anarchy-ai/LLM-VM.git
cd LLM-VM
pip3 install .
cd ..

