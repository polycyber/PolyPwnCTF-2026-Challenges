#!/bin/bash
set -e

echo "=== Starting Rabb-IT H.O.L. ==="

echo "Starting MariaDB..."
service mariadb start

# Fix MariaDB socket permissions
chmod 777 /var/run/mysqld/mysqld.sock 2>/dev/null || true
chown mysql:mysql /var/run/mysqld/mysqld.sock 2>/dev/null || true

# Wait for MariaDB to be ready
echo "Waiting for MariaDB to start..."
for i in {1..30}; do
    if mysqladmin ping -h localhost --silent; then
        echo "MariaDB is ready!"
        break
    fi
    echo "Waiting for MariaDB... ($i/30)"
    sleep 1
done

# Ensure socket is accessible
chmod 777 /var/run/mysqld/mysqld.sock
ls -la /var/run/mysqld/

# Verify database exists
echo "Verifying database setup..."
mysql -u ctf_user -pctf_password_2026 -e "USE ctf_db; SHOW TABLES;" || echo "Warning: Database verification failed"

echo "Starting SSH..."
service ssh start

# Configure PHP error logging
echo "Configuring PHP..."
PHP_INI=$(php --ini | grep "Loaded Configuration" | awk '{print $NF}')
if [ -z "$PHP_INI" ] || [ "$PHP_INI" = "(none)" ]; then
    PHP_INI=$(find /etc/php -name "php.ini" -path "*/apache2/*" | head -1)
fi

if [ -n "$PHP_INI" ]; then
    echo "error_reporting = E_ALL"                        >> "$PHP_INI"
    echo "display_errors = On"                            >> "$PHP_INI"
    echo "log_errors = On"                                >> "$PHP_INI"
    echo "error_log = /var/log/apache2/php_error.log"     >> "$PHP_INI"
    echo "PHP configured at: $PHP_INI"
else
    echo "Warning: Could not find php.ini"
fi

echo "Starting Apache..."
apache2ctl -D FOREGROUND 2>&1 | tee /var/log/apache2/startup.log &

echo "=== All services started ==="
echo "Apache access log: /var/log/apache2/access.log"
echo "Apache error log:  /var/log/apache2/error.log"
echo "PHP error log:     /var/log/apache2/php_error.log"
echo ""
echo "Tailing logs..."
tail -f /var/log/apache2/access.log \
        /var/log/apache2/error.log \
        /var/log/apache2/php_error.log 2>/dev/null || tail -f /dev/null
