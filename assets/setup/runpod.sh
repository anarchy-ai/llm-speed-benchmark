# Website: https://www.runpod.io/console/pods
# Service: RunPod

apt -y update
apt install -y vim
apt install -y neofetch

pip3 install transformers
pip3 install psutil
pip3 install gputil
pip3 install tabulate
pip3 install torch torchvision torchaudio
pip3 install matplotlib
pip3 install sentencepiece
pip3 install protobuf


pip install llm-vm

huggingface-cli login

