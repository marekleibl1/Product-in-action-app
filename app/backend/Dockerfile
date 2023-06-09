
FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

RUN apt update -y && apt-get install -y git
RUN apt install nano 

RUN pip install accelerate 
RUN pip install git+https://github.com/cloneofsimo/lora.git 

COPY . /workspace/app
RUN  pip install -r /workspace/app/backend/requirements.txt


# docker login -u marekleibl
# docker build -t vast-image .
# docker tag vast-image:latest marekleibl/vast-repo:latest
# docker push marekleibl/vast-repo:latest