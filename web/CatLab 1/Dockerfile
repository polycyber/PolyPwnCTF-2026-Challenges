# Use the official PHP Apache image
FROM php:8.2-apache

# Install system dependencies: MariaDB, build tools, socat
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    gcc \
    make \
    socat \
    && rm -rf /var/lib/apt/lists/*

# Install and enable the mysqli extension
RUN docker-php-ext-install mysqli && docker-php-ext-enable mysqli

# ── Dedicated service user ───────────────────────────────────────────────────
RUN useradd -m -s /bin/sh -r biosynth

# ── Build biosynthd ──────────────────────────────────────────────────────────
COPY service/service.c  /tmp/service/service.c
COPY service/Makefile   /tmp/service/Makefile

RUN cd /tmp/service && make && \
    mkdir -p /opt/biosynth && \
    mv biosynthd /opt/biosynth/biosynthd && \
    chmod 755 /opt/biosynth/biosynthd && \
    chown root:root /opt/biosynth/biosynthd && \
    rm -rf /tmp/service

# ── Flag — random filename, biosynth can read but not delete ────────────────
COPY service/flag2.txt /tmp/flag2.txt
RUN fname="$(openssl rand -hex 16).txt" && \
    mv /tmp/flag2.txt "/home/biosynth/${fname}" && \
    chown root:biosynth "/home/biosynth/${fname}" && \
    chmod 040 "/home/biosynth/${fname}" && \
    chown root:biosynth /home/biosynth && \
    chmod 750 /home/biosynth

# ── Web application ──────────────────────────────────────────────────────────
WORKDIR /var/www/html

# Bake web sources into the image so deployment does not require bind mounts.
COPY src/ /var/www/html/

# Adjust permissions so Apache can read the source files
RUN chown -R www-data:www-data /var/www/html

# Entrypoint: starts the internal service then hands off to Apache
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]