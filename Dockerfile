ARG GITHUB_TOKEN
# Use the official PyTorch image with GPU support
FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime



# Django environment
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install channels["daphne"]
RUN pip install pillow==10.2.0


# Install git
RUN apt-get update && \
    apt-get install -y git
# Set up Git credentials with the personal access token
RUN git config --global credential.helper store && \
    echo "https://${GITHUB_TOKEN}@github.com" > ~/.git-credentials
RUN pip install 'git+https://github.com/facebookresearch/fairscale'
RUN pip install "git+https://github.com/facebookresearch/pytorchvideo.git"
# Install necessary build tools
RUN apt-get update && \
    apt-get install -y build-essential
RUN pip install 'git+https://github.com/facebookresearch/fvcore.git' 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'
RUN conda install ffmpeg=4.3

# Install git-lfs
RUN apt-get update && \
    apt-get install -y git-lfs && \
    git lfs install
RUN git lfs pull
COPY ./apps/surgery/libs/oad/requirements.txt oad.txt
COPY ./apps/surgery/libs/seg/requirements.txt seg.txt
RUN pip install --no-cache-dir -r oad.txt
RUN pip install --no-cache-dir -r seg.txt

RUN git clone https://github.com/facebookresearch/detectron2
RUN pip install -e /detectron2


RUN git clone https://github.com/LStriving/slowfast.git
RUN pip install -e /slowfast
ENV PYTHONPATH=/slowfast/slowfast:$PYTHONPATH
RUN python /slowfast/setup.py build develop

# Set the working directory
WORKDIR /app
COPY . /app

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run additional commands within the Conda environment
RUN python manage.py collectstatic --noinput --settings=EasyShare.settings.test
RUN python manage.py makemigrations --empty access --settings=EasyShare.settings.test
RUN python manage.py makemigrations access sharefiles --settings=EasyShare.settings.test
