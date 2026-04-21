<?php
// If the calling page already validated the token (e.g. experiment.php), reuse $currentUser.
if (!isset($currentUser)) {
    $authResult = authenticateFromCookies($conn);

    if ($authResult['status'] === 'unauthenticated') {
        header("Location: index.php");
        exit;
    }

    if ($authResult['status'] === 'expired') {
        outputTokenExpiredPage(); // outputs a full page and exits
    }

    $currentUser = $authResult['user'];
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CatLab | Internal System</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body>

<nav>
    <div class="nav-logo">
        CATLAB v2.0
        <?php if ($currentUser['is_admin']): ?>
            <span class="admin-tag">Chief Scientist</span>
        <?php endif; ?>
    </div>
    <div class="nav-links">
        <a href="dashboard.php">Dashboard</a>
        <a href="experiment.php" class="link-experiment">[New Experiment]</a>
        <a href="logout.php" class="link-logout">Logout</a>
    </div>
</nav>

<div class="container">
