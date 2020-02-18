# Dockerfile
FROM python:3

WORKDIR /opt/yaraku-worker 

# install dependencies for python (done first for docker caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY . .