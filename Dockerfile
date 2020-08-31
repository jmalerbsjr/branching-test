FROM python:3-alpine

# Create virtual environment
RUN python3 -m venv venv

# Set Python3 in PATH
ENV PATH="/venv/bin:${PATH}"

# Copy to Docker image
COPY entrypoint.py /entrypoint.py
COPY requirements.txt /requirements.txt

# Configure virtual environment
RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "/entrypoint.py"]


#FROM ubuntu:20.04
#
#RUN apt-get update -y \
#    && apt install python3 -y \
#    && apt install python3-pip -y \
#    && apt install python3-venv -y \
#    && python3 -m venv venv
#
## Set Python3 in PATH
#ENV PATH="/venv/bin:${PATH}"
#
## Copy to Docker image
#COPY entrypoint.py /entrypoint.py
#COPY requirements.txt /requirements.txt
#
## Configure virtual environment
#RUN pip install wheel
#RUN pip install -r requirements.txt
#ENTRYPOINT ["python3", "/entrypoint.py"]

