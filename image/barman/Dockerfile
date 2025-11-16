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

COPY ./barman.conf /etc/barman.conf
COPY ./crontab /var/spool/cron/crontabs/root
COPY --chmod=0755 ./restore /usr/bin/restore

CMD [ "crond", "-f", "-l", "2" ]
