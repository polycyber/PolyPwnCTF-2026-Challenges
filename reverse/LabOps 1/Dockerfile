FROM debian:forky

RUN apt update

# setup zig. we need debian because of glibc
ENV ZIG_VERSION=0.15.2
RUN apt install -y curl xz-utils python3
RUN \
    curl -LO https://ziglang.org/download/${ZIG_VERSION}/zig-`uname -m`-linux-${ZIG_VERSION}.tar.xz && \
    tar xf ./zig-*.tar.xz && \
    rm *.tar.xz && \
    mv ./zig-* /zig

COPY . /app
WORKDIR /app

# just in case
RUN rm -rf zig-out .zig-cache

# first run will fail
RUN /zig/zig build -Doptimize=ReleaseFast || true
RUN /zig/zig build -Doptimize=ReleaseFast

FROM alpine:edge
RUN apk add libc6-compat
COPY --from=0 /app/zig-out/bin/server /server
EXPOSE 80
CMD ["/server"]
