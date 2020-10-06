FROM python:3.6-slim-buster

COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
RUN pip3 install gunicorn
ENV GUNICORN_BIN /usr/local/bin/gunicorn

WORKDIR /app

COPY src ./src
COPY httpInterface.py ./

ENV GENDER_IDENTIFICATION_CONFIG_ENV DEFAULT
ENV CONF_FILE=/app/conf/config.ini 
COPY conf/config.ini $CONF_FILE

RUN chgrp -R 0 /app \
 && chmod -R g+rwX /app

ENV GUNICORN_WORKER_AMOUNT 4
ENV GUNICORN_TIMEOUT 300
ENV GUNICORN_RELOAD ""

EXPOSE 5000

USER 9008

COPY run /run.sh

ENTRYPOINT [ "/run.sh" ]