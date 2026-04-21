# HAProxy 1.8 - known to have CL.TE vulnerabilities
# This version doesn't properly normalize Transfer-Encoding
FROM haproxy:1.8-alpine

COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg

EXPOSE 8080
