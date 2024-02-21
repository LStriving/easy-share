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

# Install git-lfs
RUN apt-get update && \
    apt-get install -y git-lfs && \
    git lfs install
RUN git lfs pull

# pytorch project requirements
RUN pip install --no-cache-dir apps/surgery/libs/oad/requirements.txt
RUN pip install --no-cache-dir apps/surgery/libs/seg/requirements.txt
RUN pip install -e apps/surgery/libs/external/slowfast
RUN pip install -e apps/surgery/libs/external/detectron2_repo
RUN conda install ffmpeg=4.3

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run additional commands within the Conda environment
RUN python manage.py collectstatic --noinput --settings=EasyShare.settings.test
RUN python manage.py makemigrations --empty access --settings=EasyShare.settings.test
RUN python manage.py makemigrations access sharefiles --settings=EasyShare.settings.test
