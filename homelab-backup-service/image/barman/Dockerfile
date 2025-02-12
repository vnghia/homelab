FROM base

ENV DEBIAN_FRONTEND=noninteractive
RUN install_packages ca-certificates postgresql-common \
    && echo "\n" | /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh \
    && install_packages \
    barman \
    postgresql-client-16 \
    postgresql-client-17
COPY ./barman.conf /etc/barman.conf

ENTRYPOINT [ "/usr/bin/barman" ]
