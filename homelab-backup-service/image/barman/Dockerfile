FROM base

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates postgresql-common \
    && echo '\n' | /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh \
    && apt-get install -y --no-install-recommends \
    barman \
    postgresql-client-16 \
    postgresql-client-17 \
    && rm -rf /var/lib/apt/lists/*
