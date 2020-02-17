FROM python:3.6

LABEL maintainer="Benjamin Bray <benrbray@gmail.com>"

#TODO: what is correct working directory to use?
WORKDIR /opt/yaraku_test

# install dependencies for python (done first for docker caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY . .

# run application (overridden by docker-compose)
#CMD pytest