FROM base

RUN addgroup -S logrotate -g 1000 \
    && adduser -S -G logrotate -u 1000 logrotate

RUN apk add --update --no-cache \
    logrotate
