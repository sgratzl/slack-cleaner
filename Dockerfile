FROM alpine:3.5

MAINTAINER kfei <kfei@kfei.net>

RUN apk add --no-cache python2 py-pip && pip install slack-cleaner

VOLUME ["/backup"]

WORKDIR /backup

ENTRYPOINT ["/bin/sh"]
