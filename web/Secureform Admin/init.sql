-- Additional privileges for the CTF user
-- MySQL users can already read information_schema for databases they have access to
-- Just ensure the user has all privileges on the ctf_challenge database
GRANT ALL PRIVILEGES ON ctf_challenge.* TO 'ctf_user'@'%';
FLUSH PRIVILEGES;
