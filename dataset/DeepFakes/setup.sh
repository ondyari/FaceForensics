#!/usr/bin/env bash

# Regular installs
sudo apt update
sudo apt install bzip2 -y
sudo apt install cmake -y
sudo apt install tmux -y

# Cuda 9 for Tensorflow 1.10.1
wget http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_9.0.176-1_amd64.deb
wget http://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1604/x86_64/libcudnn7_7.0.5.15-1+cuda9.0_amd64.deb
wget http://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1604/x86_64/libcudnn7-dev_7.0.5.15-1+cuda9.0_amd64.deb
wget http://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1604/x86_64/libnccl2_2.1.4-1+cuda9.0_amd64.deb
wget http://developer.download.nvidia.com/compute/machine-learning/repos/ubuntu1604/x86_64/libnccl-dev_2.1.4-1+cuda9.0_amd64.deb
sudo dpkg -i cuda-repo-ubuntu1604_9.0.176-1_amd64.deb
sudo dpkg -i libcudnn7_7.0.5.15-1+cuda9.0_amd64.deb
sudo dpkg -i libcudnn7-dev_7.0.5.15-1+cuda9.0_amd64.deb
sudo dpkg -i libnccl2_2.1.4-1+cuda9.0_amd64.deb
sudo dpkg -i libnccl-dev_2.1.4-1+cuda9.0_amd64.deb
sudo apt-get update
sudo apt-get install cuda=9.0.176-1 -y --allow-unauthenticated
sudo apt-get install libcudnn7-dev -y --allow-unauthenticated
sudo apt-get install libnccl-dev -y --allow-unauthenticated
echo 'export PATH=/usr/local/cuda-9.0/bin${PATH:+:${PATH}}' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-9.0/lib64${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}' >> ~/.bashrc

# Python
wget https://repo.anaconda.com/archive/Anaconda3-5.2.0-Linux-x86_64.sh
bash Anaconda3-5.2.0-Linux-x86_64.sh -b
# Add to path
echo 'export PATH="~/anaconda3/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
# source does not update path edits so we add the path manually for now
export PATH="~/anaconda3/bin:$PATH"
# Python libraries
pip install -r faceswap-master/requirements.txt
conda install -c conda-forge opencv -y
pip install --ignore-installed --upgrade https://storage.googleapis.com/tensorflow/linux/gpu/tensorflow_gpu-1.10.1-cp36-cp36m-linux_x86_64.whl

# We need to reboot once it is finished to enable cuda
sudo reboot
