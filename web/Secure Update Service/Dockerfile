# check=skip=SecretsUsedInArgOrEnv
FROM dunglas/frankenphp:alpine

ENV SERVER_NAME=:80
ENV KEY=76820ab89076766b7a1bc86d84e846a77331198043665456b969f9b6ec5b3c5a

WORKDIR /app

EXPOSE 80

COPY ./src/flag.txt /flag.txt
COPY ./src/index.php /app/public
COPY ./src/update.sh /app/public
