FROM ubuntu:24.04 AS builder

RUN echo 'APT::Get::AllowUnauthenticated "true";' > /etc/apt/apt.conf.d/99allow-unauthenticated && \
    echo 'Acquire::AllowInsecureRepositories "true";' >> /etc/apt/apt.conf.d/99allow-unauthenticated && \
    echo 'Acquire::AllowDowngradeToInsecureRepositories "true";' >> /etc/apt/apt.conf.d/99allow-unauthenticated && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    qt6-base-dev \
    qt6-tools-dev \
    libssl-dev \
    && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /build

COPY src/server.cpp .
COPY src/client.cpp .
COPY src/CMakeLists.txt .

RUN mkdir build && \
    cd build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release && \
    make -j$(nproc) && \
    cp SolutionMixer /build/SolutionMixer && \
    cp SolutionMixerServer /build/SolutionMixerServer

FROM ubuntu:24.04

RUN echo 'APT::Get::AllowUnauthenticated "true";' > /etc/apt/apt.conf.d/99allow-unauthenticated && \
    echo 'Acquire::AllowInsecureRepositories "true";' >> /etc/apt/apt.conf.d/99allow-unauthenticated && \
    echo 'Acquire::AllowDowngradeToInsecureRepositories "true";' >> /etc/apt/apt.conf.d/99allow-unauthenticated && \
    export DEBIAN_FRONTEND=noninteractive && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    libqt6core6 \
    libqt6network6 \
    libssl3 \
    ca-certificates \
    && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /build/SolutionMixerServer /app/SolutionMixerServer
COPY files/flag.txt /app/flag.txt
COPY src/docker-entrypoint.sh /app/docker-entrypoint.sh
COPY files/exceptional_solutions.enc /app/exceptional_solutions.enc

RUN chmod +x /app/SolutionMixerServer && \
    chmod +x /app/docker-entrypoint.sh

EXPOSE 34512

ENTRYPOINT ["/app/docker-entrypoint.sh"]
