# Website: https://www.runpod.io/console/pods
# Service: RunPod

apt update
apt install vim
pip3 install transformers
pip3 install --ignore-installed llm-vm
pip3 install "weaviate-client==3.*"
pip3 install pinecone-client
pip3 install python-dotenv
pip3 install protobuf
echo
huggingface-cli login

# pip3 install psutil
# pip3 install gputil
# pip3 install tabulate
