<?php
include 'db.php';

$error = "";

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = $_POST['username'] ?? '';
    $password = $_POST['password'] ?? '';

    if (!empty($username) && !empty($password)) {
        $user = verify_user($username, $password, $conn);

        if ($user) {
            $tokens = createTokens($user['id'], $username, $conn);
            setcookie('access_token',  $tokens['access'],  time() + 60, '/', '', false, true);
            setcookie('refresh_token', $tokens['refresh'], time() + 900, '/refresh.php', '', false, true);

            header("Location: dashboard.php");
            exit;
        } else {
            $error = "Access Denied: Invalid credentials for CatLab clearance.";
        }
    } else {
        $error = "Please provide both ID and Passcode.";
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CatLab | Internal Portal</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body class="login-body">

<div class="login-card">
    <div class="login-logo">CATLAB</div>
    <div class="login-tagline">Trash-to-Feline Transmogrification Lab</div>

    <div class="status-badge">
        <span class="status-dot"></span>
        SYSTEM ONLINE &mdash; v2.0
    </div>

    <?php if ($error): ?>
        <div class="alert alert-error"><?php echo htmlspecialchars($error); ?></div>
    <?php endif; ?>

    <form method="POST">
        <div class="form-group">
            <label for="username">Scientist ID</label>
            <input type="text" id="username" name="username" placeholder="Enter your username" required autofocus>
        </div>
        <div class="form-group">
            <label for="password">Access Passcode</label>
            <input type="password" id="password" name="password" placeholder="Enter your passcode" required>
        </div>
        <button type="submit" class="btn btn-full">AUTHENTICATE</button>
    </form>

    <div class="login-footer-link">
        New researcher? <a href="register.php">Apply for Lab Access</a>
    </div>
</div>

</body>
</html>
