<?php
require_once 'config.php';

$error = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $pin = isset($_POST['pin']) ? $_POST['pin'] : '';
    
    if ($pin === SECRET_PIN) {
        $_SESSION['authenticated'] = true;
        header('Location: dashboard.php');
        exit;
    } else {
        $error = 'Invalid PIN. Try again.';
    }
}

if (isAuthenticated()) {
    header('Location: dashboard.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SecureForm Admin</title>
    <link rel="stylesheet" href="style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
</head>
<body class="login-page">
    <div class="login-container">
        <div class="login-header">
            <div class="logo">
                <span class="logo-icon">◈</span>
                <span class="logo-text">SecureForm</span>
            </div>
            <p class="login-subtitle">Admin Panel Access</p>
        </div>
        
        <form method="POST" class="login-form" autocomplete="off">
            <div class="form-group">
                <label for="pin">Enter 4-Digit PIN</label>
                <div class="pin-input-container">
                    <input 
                        type="text" 
                        id="pin" 
                        name="pin" 
                        maxlength="4" 
                        pattern="[0-9]{4}"
                        placeholder="••••"
                        autocomplete="off"
                        required
                    >
                </div>
                <?php if ($error): ?>
                    <div class="error-message"><?php echo htmlspecialchars($error); ?></div>
                <?php endif; ?>
            </div>
            
            <button type="submit" class="login-btn">
                <span>Access Panel</span>
                <span class="btn-arrow">→</span>
            </button>
        </form>
        
        <div class="login-footer">
            <p>Authorized personnel only</p>
        </div>
    </div>
    
    <div class="background-grid"></div>
</body>
</html>
