CREATE DATABASE IF NOT EXISTS ctf_db;
USE ctf_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, password, email, role) VALUES
('admin', MD5('admin123'), 'admin@rabb-it.hol.local', 'admin'),
('user1', MD5('password'), 'user1@rabb-it.hol.local', 'user'),
('guest', MD5('guest'), 'guest@rabb-it.hol.local', 'user'),
('testuser', MD5('test123'), 'test@rabb-it.hol.local', 'user');

CREATE TABLE secrets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    secret_data TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

INSERT INTO secrets (user_id, secret_data) VALUES
(1, 'The real treasure is in the details'),
(2, 'Check the small things'),
(3, 'Sometimes the answer is right in front of you');

CREATE TABLE configuration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value TEXT,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO configuration (config_key, config_value, description) VALUES
('app_name', 'Rabb-IT H.O.L. Portal', 'Application name'),
('version', '2.1.4', 'Current application version'),
('debug_mode', 'false', 'Enable debug logging'),
('max_login_attempts', '5', 'Maximum failed login attempts'),
('session_timeout', '3600', 'Session timeout in seconds'),
('flag', 'You really thought the flag would be in the database? Come on...', 'Feature flag for new UI'),
('api_endpoint', 'https://api.securecorp.local/v1', 'API endpoint URL'),
('maintenance_mode', 'false', 'Enable maintenance mode');
