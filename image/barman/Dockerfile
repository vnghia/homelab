FROM base AS supercronic-downloader

ARG TARGETARCH
ARG SUPERCRONIC_VERSION

RUN wget https://github.com/aptible/supercronic/releases/download/v${SUPERCRONIC_VERSION}/supercronic-linux-${TARGETARCH} -O /usr/bin/supercronic \
    && chmod +x /usr/bin/supercronic
RUN /usr/bin/supercronic -version

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
    && delgroup ping \
    && addgroup -S barman -g 999 \
    && adduser -S -G barman -u 999 barman

COPY --from=supercronic-downloader /usr/bin/supercronic /usr/bin/supercronic
COPY ./barman.conf /etc/barman.conf
COPY ./crontab /etc/crontabs/barman
COPY --chmod=0755 ./restore /usr/bin/restore

CMD [ "supercronic", "-split-logs", "-passthrough-logs", "/etc/crontabs/barman" ]
