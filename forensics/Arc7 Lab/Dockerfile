# From repo root:
#   docker build -f ctf-arc7-lab/Dockerfile -t arc7-terminal ctf-arc7-lab
# From ctf-arc7-lab/:
#   docker build -t arc7-terminal .
#
# Run: docker run --rm -p 8080:80 arc7-terminal
# Open: http://localhost:8080/
FROM nginx:1.27-alpine

COPY player/terminal.html /usr/share/nginx/html/index.html

EXPOSE 80
