<?php
include 'db.php';

$accessToken = $_COOKIE['access_token'] ?? null;
if ($accessToken) {
    $row = getUserFromAccessToken($accessToken, $conn);
    if ($row && !$row['is_admin']) {
        $stmt = $conn->prepare("DELETE FROM user_tokens WHERE access_token = ?");
        $stmt->bind_param("s", $accessToken);
        $stmt->execute();
    }
}

// Expire both cookies immediately
setcookie('access_token',  '', time() - 3600, '/', '', false, true);
setcookie('refresh_token', '', time() - 3600, '/', '', false, true);

header("Location: index.php");
exit;
