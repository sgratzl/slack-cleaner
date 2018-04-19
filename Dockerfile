FROM python:2.7-alpine

LABEL maintainer="Samuel Gratzl <samuel_gratzl@gmx.at>"

VOLUME "/backup"
WORKDIR /backup
CMD ["python", "-i", "-c", "\"from slack_cleaner2 import *\""]

RUN apk add --update bash && rm -rf /var/cache/apk/*
# for better layers
ADD ./requirements* /data/
RUN pip --no-cache-dir install -r /data/requirements.txt && \
    pip --no-cache-dir install -r /data/requirements_dev.txt

ADD . /data
RUN pip --no-cache-dir install /data
