FROM alpine:3.8

ENV GUNICORN_WORKER_AMOUNT 4
ENV GUNICORN_TIMEOUT 300
ENV GUNICORN_RELOAD ""

RUN apk add python3 && rm -rf /var/cache/apk/*

COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt

RUN pip3 install gunicorn

WORKDIR /app

COPY src ./src

RUN chgrp -R 0 /app \
 && chmod -R g+rwX /app

EXPOSE 5000

USER 9008

COPY run /run.sh

ENTRYPOINT [ "/run.sh" ]