FROM debian:stable-slim
ENV DEBIAN_FRONTEND=noninteractive

# Use minimal install + no recommends for smallest footprint
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    apache2 \
    php \
    php-mysql \
    php-cli \
    libapache2-mod-php \
    mariadb-server \
    openssh-server \
    sudo \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && find /usr/share/doc -depth -name "*.gz" -delete \
    && find /usr/share/man -depth -type f -delete \
    && find /usr/share/locale -mindepth 1 -maxdepth 1 ! -name 'en*' -exec rm -rf {} +

# All config in one layer
RUN a2enmod rewrite && \
    sed -i 's/DirectoryIndex.*/DirectoryIndex index.php index.html/' /etc/apache2/mods-enabled/dir.conf && \
    mkdir -p /var/run/mysqld /var/run/sshd && \
    chown mysql:mysql /var/run/mysqld && \
    chmod 755 /var/run/mysqld && \
    sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config && \
    sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config && \
    useradd -m -s /bin/bash admin && \
    echo 'admin:admin123' | chpasswd && \
    usermod -aG sudo admin && \
    echo 'admin ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

COPY www/ /var/www/html/
COPY init.sql /tmp/init.sql
COPY start.sh /start.sh

RUN mkdir -p /home/admin/Documents && \
    echo '==wL6ACanV3boRHIlJXZoBSbvJnZgwGbh12cgknclZHIn5War92bsBycpBCdpJmYhJHI0FGaUBSI0lGIy9mZgcmbpt2bvxGIwVWZrBCd1JEIu4iLnFGbmBSZoRHIzF2dgQXYoRHIoNXa3BSS' > /home/admin/Documents/txt.galf && \
    echo 'Keep digging, my little rabbit...' > /home/admin/Documents/.flag.txt && \
    chown -R admin:admin /home/admin/Documents && \
    rm -f /var/www/html/index.html && \
    chown -R www-data:www-data /var/www/html && \
    chmod -R 755 /var/www/html && \
    usermod -a -G mysql www-data && \
    chmod +x /start.sh && \
    service mariadb start && \
    mysql -u root < /tmp/init.sql && \
    mysql -u root -e "CREATE USER IF NOT EXISTS 'ctf_user'@'localhost' IDENTIFIED BY 'ctf_password_2026';" && \
    mysql -u root -e "GRANT ALL PRIVILEGES ON ctf_db.* TO 'ctf_user'@'localhost';" && \
    mysql -u root -e "GRANT ALL PRIVILEGES ON *.* TO 'ctf_user'@'localhost' WITH GRANT OPTION;" && \
    mysql -u root -e "FLUSH PRIVILEGES;" && \
    service mariadb stop && \
    rm -f /tmp/init.sql

EXPOSE 80 22
CMD ["/start.sh"]
