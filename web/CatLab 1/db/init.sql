CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    is_admin TINYINT(1) DEFAULT 0
);

INSERT INTO users (username, password, is_admin) 
VALUES ('admin', '$2y$10$.v3rXxSPkKr5AfdZB5NGnOG..oAUolAaggpSXF.t7CSQyesj5GLmm', 1);

CREATE TABLE user_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    access_token VARCHAR(64) NOT NULL,
    refresh_token VARCHAR(64) NOT NULL,
    access_expires_at DATETIME NOT NULL,
    refresh_expires_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

INSERT INTO user_tokens (user_id, access_token, refresh_token, access_expires_at, refresh_expires_at)
VALUES (1, '', '21232f297a57a5a743894a0e4a801fc3', '2000-01-01 00:00:00', '9999-12-31 23:59:59');

