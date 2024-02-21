ARG GITHUB_TOKEN
# Use the official PyTorch image with GPU support
FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

# Set the working directory
WORKDIR /app

# Django environment
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install channels["daphne"]
RUN pip install pillow==10.2.0


COPY . /app
# Install git
RUN apt-get update && \
    apt-get install -y git
# Set up Git credentials with the personal access token
RUN git config --global credential.helper store && \
    echo "https://${GITHUB_TOKEN}@github.com" > ~/.git-credentials


# pytorch project requirements
RUN pip install --no-cache-dir -r /app/apps/surgery/libs/oad/requirements.txt
RUN pip install 'git+https://github.com/facebookresearch/fairscale'
RUN pip install "git+https://github.com/facebookresearch/pytorchvideo.git"
# Install necessary build tools
RUN apt-get update && \
    apt-get install -y build-essential
RUN pip install 'git+https://github.com/facebookresearch/fvcore.git' 'git+https://github.com/cocodataset/cocoapi.git#subdirectory=PythonAPI'
RUN pip install --no-cache-dir -r /app/apps/surgery/libs/seg/requirements.txt
RUN pip install -e /app/apps/surgery/libs/external/detectron2_repo
RUN pip install -e /app/apps/surgery/libs/external/slowfast
RUN conda install ffmpeg=4.3
# buiid slowfast    
ENV PYTHONPATH=/app/apps/surgery/libs/external/slowfast/slowfast:$PYTHONPATH
RUN python /app/apps/surgery/libs/external/slowfast/setup.py build develop

# Install git-lfs
RUN apt-get update && \
    apt-get install -y git-lfs && \
    git lfs install
RUN git lfs pull
# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run additional commands within the Conda environment
RUN python manage.py collectstatic --noinput --settings=EasyShare.settings.test
RUN python manage.py makemigrations --empty access --settings=EasyShare.settings.test
RUN python manage.py makemigrations access sharefiles --settings=EasyShare.settings.test
