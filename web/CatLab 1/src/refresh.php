<?php
include 'db.php';

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Method not allowed']);
    exit;
}

$refreshToken = $_COOKIE['refresh_token'] ?? null;

if (!$refreshToken) {
    http_response_code(401);
    echo json_encode(['error' => 'No refresh token provided']);
    exit;
}

if (rand(1, 10) === 1) {
    purgeExpiredTokens($conn);
}

$row = getUserFromRefreshToken($refreshToken, $conn);

if (!$row || strtotime($row['refresh_expires_at']) <= time()) {
    http_response_code(401);
    echo json_encode(['error' => 'Refresh token expired or invalid']);
    exit;
}

$newTokens = createTokens($row['id'], $row['username'], $conn);
setcookie('access_token',  $newTokens['access'],  time() + 900, '/', '', false, true);
setcookie('refresh_token', $newTokens['refresh'], time() + 900, '/refresh.php', '', false, true);

http_response_code(200);
echo json_encode(['status' => 'ok']);
