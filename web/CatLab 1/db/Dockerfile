FROM mariadb:10.11

# Load schema and seed data at first container initialization.
COPY init.sql /docker-entrypoint-initdb.d/init.sql