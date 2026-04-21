<?php
$host = 'db';
$db   = getenv('DB_DATABASE');
$user = getenv('DB_USER');
$pass = getenv('DB_PASSWORD');

// Use mysqli with error reporting for easier debugging during CTF creation
mysqli_report(MYSQLI_REPORT_ERROR | MYSQLI_REPORT_STRICT);

try {
    $conn = new mysqli($host, $user, $pass, $db);
    $conn->set_charset("utf8mb4");
} catch (mysqli_sql_exception $e) {
    die("The Lab Database is currently offline. Please contact the Chief Scientist.");
}

/**
 * Helper function for your registration/login logic
 */
function verify_user($username, $password, $conn) {
    $stmt = $conn->prepare("SELECT id, password, is_admin FROM users WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $result = $stmt->get_result();
    
    if ($user = $result->fetch_assoc()) {
        if (password_verify($password, $user['password'])) {
            return $user;
        }
    }
    return false;
}

/**
 * Registers a new non-admin user. Returns the new user ID on success,
 * or an error string on failure.
 */
function register_user($username, $password, $conn) {
    // Check whether the username is already taken
    $stmt = $conn->prepare("SELECT id FROM users WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    if ($stmt->get_result()->fetch_assoc()) {
        return "Username already registered. Choose a different Scientist ID.";
    }

    $hash = password_hash($password, PASSWORD_BCRYPT);
    $stmt = $conn->prepare("INSERT INTO users (username, password, is_admin) VALUES (?, ?, 0)");
    $stmt->bind_param("ss", $username, $hash);
    $stmt->execute();
    return $conn->insert_id;
}

function generateToken($length = 16) {
    return bin2hex(random_bytes($length));
}

function createTokens($userId, $username, $conn) {
    $accessToken = generateToken();
    $refreshToken = md5($username);
    
    // Set expirations
    $accessExpiry = date('Y-m-d H:i:s', strtotime('+1 minute'));
    $refreshExpiry = date('Y-m-d H:i:s', strtotime('+15 minutes'));

    $stmt = $conn->prepare("INSERT INTO user_tokens (user_id, access_token, refresh_token, access_expires_at, refresh_expires_at) VALUES (?, ?, ?, ?, ?)");
    $stmt->bind_param("issss", $userId, $accessToken, $refreshToken, $accessExpiry, $refreshExpiry);
    $stmt->execute();

    return ['access' => $accessToken, 'refresh' => $refreshToken];
}

function getUserFromAccessToken($token, $conn) {
    $stmt = $conn->prepare(
        "SELECT u.id, u.username, u.is_admin, t.access_expires_at
         FROM user_tokens t
         JOIN users u ON t.user_id = u.id
         WHERE t.access_token = ?"
    );
    $stmt->bind_param("s", $token);
    $stmt->execute();
    return $stmt->get_result()->fetch_assoc();
}

function purgeExpiredTokens($conn) {
    $stmt = $conn->prepare("DELETE FROM user_tokens WHERE refresh_expires_at <= NOW()");
    $stmt->execute();
}

function getUserFromRefreshToken($token, $conn) {
    $stmt = $conn->prepare(
        "SELECT u.id, u.username, u.is_admin, t.refresh_expires_at
         FROM user_tokens t
         JOIN users u ON t.user_id = u.id
         WHERE t.refresh_token = ?
         ORDER BY t.refresh_expires_at DESC
         LIMIT 1"
    );
    $stmt->bind_param("s", $token);
    $stmt->execute();
    return $stmt->get_result()->fetch_assoc();
}

/**
 * Validates the access_token cookie only.
 *
 * Returns one of:
 *   ['status' => 'ok',              'user' => <row>]  — valid token
 *   ['status' => 'expired']                           — token in DB but past expiry
 *   ['status' => 'unauthenticated']                   — no cookie or token not in DB
 *
 * Refreshing is now the client's responsibility via POST /refresh.php.
 */
function authenticateFromCookies($conn) {
    $accessToken = $_COOKIE['access_token'] ?? null;

    if (!$accessToken) {
        return ['status' => 'unauthenticated'];
    }

    $row = getUserFromAccessToken($accessToken, $conn);

    if (!$row) {
        return ['status' => 'unauthenticated'];
    }

    if (strtotime($row['access_expires_at']) <= time()) {
        return ['status' => 'expired'];
    }

    return ['status' => 'ok', 'user' => $row];
}

/**
 * Outputs a self-contained 401 page that automatically calls refresh.php,
 * then reloads on success or redirects to login on failure. Never returns.
 */
function outputTokenExpiredPage() {
    http_response_code(401);
    echo <<<'HTML'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CatLab | Session Expired</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body class="login-body">
<div class="login-card" style="text-align:center;">
    <div class="login-logo">CATLAB</div>
    <div class="login-tagline">Session Management</div>

    <div id="state-refreshing">
        <div class="status-badge">
            <span class="status-dot"></span>
            REFRESHING CREDENTIALS
        </div>
        <p style="color:#8b949e; font-size:0.82rem; margin:0;">
            Your access token has expired.<br>Obtaining a fresh one&hellip;
        </p>
    </div>

    <div id="state-failed" style="display:none;">
        <div class="alert alert-error" style="text-align:left;">
            Token refresh failed. Your session may have expired entirely.
        </div>
        <a href="index.php" class="btn btn-full">Return to Login</a>
    </div>
</div>

<script>
fetch('refresh.php', { method: 'POST' })
    .then(function(r) {
        if (r.ok) {
            window.location.reload();
        } else {
            document.getElementById('state-refreshing').style.display = 'none';
            document.getElementById('state-failed').style.display = 'block';
        }
    })
    .catch(function() {
        window.location.href = 'index.php';
    });
</script>
</body>
</html>
HTML;
    exit;
}