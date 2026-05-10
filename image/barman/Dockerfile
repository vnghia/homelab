FROM base

ARG BARMAN_VERSION

RUN apk add --update --no-cache \
    file zstd tar \
    py3-setuptools py3-zstandard \
    postgresql16-client \
    postgresql17-client

RUN apk add --update --no-cache \
    --repository=http://dl-cdn.alpinelinux.org/alpine/edge/testing/ \
    barman=${BARMAN_VERSION}

# postgres uid:gid
RUN deluser --remove-home barman \
    && addgroup -S barman -g 1000 \
    && adduser -S -G barman -u 1000 barman

COPY ./barman.conf /etc/barman.conf
COPY --chmod=0755 ./restore /usr/bin/restore
