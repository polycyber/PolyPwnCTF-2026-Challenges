<?php
include 'db.php';

$error = "";

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username'] ?? '');
    $password = $_POST['password'] ?? '';

    if (empty($username) || empty($password)) {
        $error = "Please provide both a Scientist ID and Passcode.";
    } elseif (strlen($username) < 3 || strlen($username) > 32) {
        $error = "Scientist ID must be between 3 and 32 characters.";
    } elseif (strlen($password) < 8) {
        $error = "Passcode must be at least 8 characters.";
    } else {
        $result = register_user($username, $password, $conn);

        if (is_string($result)) {
            // register_user returned an error message
            $error = $result;
        } else {
            // $result is the new user ID — issue tokens and drop into the lab
            $tokens = createTokens($result, $username, $conn);
            setcookie('access_token',  $tokens['access'],  time() + 60,  '/', '', false, true);
            setcookie('refresh_token', $tokens['refresh'], time() + 900, '/refresh.php', '', false, true);

            header("Location: dashboard.php");
            exit;
        }
    }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CatLab | Apply for Lab Access</title>
    <link rel="stylesheet" href="static/css/style.css">
</head>
<body class="login-body">

<div class="login-card">
    <div class="login-logo">CATLAB</div>
    <div class="login-tagline">New Researcher Enrollment</div>

    <div class="status-badge">
        <span class="status-dot"></span>
        RECRUITMENT OPEN
    </div>

    <?php if ($error): ?>
        <div class="alert alert-error"><?php echo htmlspecialchars($error); ?></div>
    <?php endif; ?>

    <form method="POST">
        <div class="form-group">
            <label for="username">Scientist ID</label>
            <input type="text" id="username" name="username"
                   placeholder="Choose a username (3–32 chars)"
                   value="<?php echo htmlspecialchars($_POST['username'] ?? ''); ?>"
                   required autofocus>
        </div>
        <div class="form-group">
            <label for="password">Access Passcode</label>
            <input type="password" id="password" name="password"
                   placeholder="Choose a passcode (min. 8 chars)"
                   required>
        </div>
        <button type="submit" class="btn btn-full">ENROLL</button>
    </form>

    <div class="login-footer-link">
        Already have clearance? <a href="index.php">Sign in</a>
    </div>
</div>

</body>
</html>
