<?php
session_start();

// Database configuration - MySQL
define('DB_HOST', getenv('DB_HOST') ?: 'db');
define('DB_NAME', getenv('DB_NAME') ?: 'ctf_challenge');
define('DB_USER', getenv('DB_USER') ?: 'ctf_user');
define('DB_PASS', getenv('DB_PASS') ?: 'ctf_password');

// The secret PIN (4 digits) - bruteforceable
define('SECRET_PIN', '7392');

// Initialize database connection
function getDB() {
    static $db = null;
    if ($db === null) {
        $dsn = "mysql:host=" . DB_HOST . ";dbname=" . DB_NAME . ";charset=utf8mb4";
        $db = new PDO($dsn, DB_USER, DB_PASS);
        $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    }
    return $db;
}

// Initialize database schema
function initDatabase() {
    $db = getDB();
    
    // Create entries table (for user submissions - like CF7 entries)
    $db->exec("CREATE TABLE IF NOT EXISTS entries (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        email VARCHAR(255),
        message TEXT,
        language VARCHAR(10) DEFAULT 'en',
        submission_time DATETIME DEFAULT CURRENT_TIMESTAMP
    )");
    
    // Create secrets table (contains the flag)
    $db->exec("CREATE TABLE IF NOT EXISTS secrets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        flag VARCHAR(255) NOT NULL
    )");
    
    // Insert flag if not exists
    $stmt = $db->query("SELECT COUNT(*) FROM secrets");
    if ($stmt->fetchColumn() == 0) {
        $db->exec("INSERT INTO secrets (flag) VALUES ('FLAG{bl1nd_sqli_0rd3r_by}')");
    }
    
    return $db;
}

// Mimic WordPress's sanitize_text_field
// Removes some things but NOT enough to prevent ORDER BY injection!
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

// Check if user is authenticated
function isAuthenticated() {
    return isset($_SESSION['authenticated']) && $_SESSION['authenticated'] === true;
}

// Require authentication
function requireAuth() {
    if (!isAuthenticated()) {
        header('Location: index.php');
        exit;
    }
}

// Initialize the database on include (with retry for docker startup)
$retries = 10;
while ($retries > 0) {
    try {
        initDatabase();
        break;
    } catch (PDOException $e) {
        $retries--;
        if ($retries === 0) {
            die("Database connection failed: " . $e->getMessage());
        }
        sleep(2);
    }
}
?>
