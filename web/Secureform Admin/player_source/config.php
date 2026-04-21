<?php
session_start();

define('DB_HOST', getenv('DB_HOST') ?: 'db');
define('DB_NAME', getenv('DB_NAME') ?: 'ctf_challenge');
define('DB_USER', getenv('DB_USER') ?: 'ctf_user');
define('DB_PASS', getenv('DB_PASS') ?: 'ctf_password');
define('SECRET_PIN', getenv('SECRET_PIN') ?: '0000');

function getDB() {
    static $db = null;
    if ($db === null) {
        $dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=utf8mb4";
        $db = new PDO($dsn, DB_USER, DB_PASS);
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    }
    return $db;
}

function initDatabase() {
    $db = getDB();
    
    $db->exec("CREATE TABLE IF NOT EXISTS entries (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        message TEXT,
        language VARCHAR(10) DEFAULT 'en',
        submission_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )");
    
    $db->exec("CREATE TABLE IF NOT EXISTS secrets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        flag VARCHAR(255) NOT NULL
    )");
    
    $stmt = $db->query("SELECT COUNT(*) FROM secrets");
    if ($stmt->fetchColumn() == 0) {
        $flag = getenv('FLAG') ?: 'FLAG{PLACEHOLDER}';
        $stmt = $db->prepare("INSERT INTO secrets (flag) VALUES (?)");
        $stmt->execute([$flag]);
    }
    
    return $db;
}

function sanitize_text_field($str) {
    $str = trim($str);
    $str = str_replace(chr(0), '', $str);
    $str = preg_replace('/\r/', '', $str);
    $str = preg_replace('/\n/', ' ', $str);
    $str = strip_tags($str);
    $str = preg_replace('/\b(SLEEP|BENCHMARK|WAIT\s+FOR\s+DELAY|PG_SLEEP)\s*\(/i', 'BLOCKED(', $str);
    $str = substr($str, 0, 1000);
    return $str;
}

function isAuthenticated() {
    return isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true;
}

function requireAuth() {
    if (!isAuthenticated()) {
        header('Location: index.php');
        exit;
    }
}

$retries = 10;
while ($retries > 0) {
    try {
        initDatabase();
        break;
    } catch (PDOException $e) {
        $retries--;
        if ($retries === 0) {
            die("Database connection failed");
        }
        sleep(2);
    }
}
?>
