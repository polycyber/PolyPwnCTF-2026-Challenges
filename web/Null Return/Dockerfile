FROM python:3.12-alpine

WORKDIR /app

# Install grep/coreutils (already in alpine, but explicit)
RUN apk add --no-cache coreutils

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY app.py .
COPY templates/ templates/

# Lab record files (readable by the "search" and "read" commands)
COPY records/ records/

# Restricted shell environment: only cat, ls, grep available
RUN mkdir -p /usr/local/restricted && \
    ln -s /bin/cat   /usr/local/restricted/cat && \
    ln -s /bin/ls    /usr/local/restricted/ls && \
    ln -s /bin/grep  /usr/local/restricted/grep && \
    ln -s /bin/sh    /usr/local/restricted/sh

# Remove dangerous binaries so injected commands can't modify anything
RUN rm -f /bin/rm /bin/mv /bin/cp /bin/chmod /bin/chown \
    /bin/ln /bin/mkdir /bin/rmdir /bin/touch \
    /bin/sed /bin/dd /usr/bin/find /usr/bin/xargs \
    /usr/bin/wget /usr/bin/curl 2>/dev/null || true

EXPOSE 5000

CMD ["python", "app.py"]