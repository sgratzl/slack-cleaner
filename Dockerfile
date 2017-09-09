FROM python:2.7-alpine

MAINTAINER Samuel Gratzl <samuel_gratzl@gmx.at>

VOLUME ["/backup"]
WORKDIR /backup
ENTRYPOINT ["/bin/sh"]

ADD . /data
RUN pip install /data