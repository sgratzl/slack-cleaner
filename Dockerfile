FROM python:2.7-alpine

MAINTAINER Samuel Gratzl <samuel_gratzl@gmx.at>

VOLUME ["/backup"]

ADD . /data
RUN pip install /data

WORKDIR /backup

ENTRYPOINT ["/bin/sh"]

