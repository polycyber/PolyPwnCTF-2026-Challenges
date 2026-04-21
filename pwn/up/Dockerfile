FROM ubuntu:latest

RUN apt update
RUN apt install -y socat libc6-dev gcc-multilib

RUN useradd -d /home/ctf/ -m -p ctf -s /bin/bash ctf

WORKDIR /home/ctf

COPY source .
RUN chown -R ctf:ctf /home/ctf
RUN chmod +x ./pmj

USER ctf
EXPOSE 1001

ENTRYPOINT socat TCP-LISTEN:1001,reuseaddr,fork EXEC:"stdbuf -i0 -o0 -e0 ./pmj && /bin/bash"
