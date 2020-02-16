FROM python:3.6

LABEL maintainer="Benjamin Bray <benrbray@gmail.com>"

#TODO: what is correct working directory to use?
WORKDIR /opt/yaraku_ml

# install dependencies for python (done first for docker caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy application code
COPY . .

# expose ports
EXPOSE 5000

# run application (overridden by docker-compose)
#ENV FLASK_APP "yaraku_web:create_app()"
#ENV FLASK_ENV "development"
CMD sh -c "python home.py"
#CMD #sh -c "flask #run --host 0.0.0.0"