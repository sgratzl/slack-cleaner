FROM python:2.7-alpine

MAINTAINER Samuel Gratzl <samuel_gratzl@gmx.at>

VOLUME ["/backup"]
WORKDIR /backup
ENTRYPOINT ["/bin/bash"]

RUN apk add bash
# for better layers
RUN pip install slacker

ADD . /data
RUN pip install /data
