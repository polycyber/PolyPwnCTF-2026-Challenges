FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir mercurial

RUN git config --global user.email "ops@nexuslabs.internal" \
    && git config --global user.name "Nexus Ops"

WORKDIR /app
COPY build.py .

RUN python3 build.py /srv/www/challenge

WORKDIR /srv/www/challenge

EXPOSE 8080

CMD ["python3", "-m", "http.server", "8080", "--bind", "0.0.0.0"]
