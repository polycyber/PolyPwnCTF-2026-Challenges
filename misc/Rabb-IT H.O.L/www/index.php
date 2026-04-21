<!DOCTYPE html>
<html>
<head>
    <title>Rabb-IT H.O.L. - Enterprise Portal</title>
    <link rel="icon" type="image/png" href="favicon.png">
    <link rel="stylesheet" href="style.css">
    <script>
        (function() {
            var payload = 'TmV0d29yayByZXF1ZXN0cyB3b3VsZCBiZSBhIGdvb2QgcGxhY2UgdG8gaGlkZSBhIGZsYWcgcmlnaHQ/';
            
            if (navigator.sendBeacon) {
                navigator.sendBeacon('/api/analytics', JSON.stringify({
                    event: 'page_view',
                    page: window.location.pathname,
                    referrer: document.referrer,
                    data: payload
                }));
            }
            
            fetch('/api/track', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    timestamp: Date.now(),
                    secret_payload: payload,
                    user_agent: navigator.userAgent
                })
            }).catch(function() {});
        })();
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 Rabb-IT H.O.L. Enterprise Portal</h1>
            <p>Welcome to our secure business platform</p>
            <div class="nav">
                <a href="index.php">Home</a>
                <a href="login.php">Login</a>
                <a href="index.php?page=about">About</a>
                <a href="index.php?page=docs">Documentation</a>
            </div>
        </div>
        
        <div class="content">
<?php
if (isset($_GET['page'])) {
    $page = $_GET['page'];
    $file = $page . '.php';
    
    if (file_exists($file)) {
        include($file);
    } else {
        if (file_exists($page)) {
            include($page);
        } else {
            echo "<div class='alert'>Page not found: " . htmlspecialchars($page) . "</div>";
            echo "<p>Available pages: about, docs</p>";
        }
    }
} else {
    ?>
    <h2>Welcome to Rabb-IT H.O.L.</h2>
    <p>Your trusted partner for enterprise solutions since 2024.</p>
    
    <h3>Our Services</h3>
    <ul>
        <li>Cloud Infrastructure Management</li>
        <li>Security Consulting</li>
        <li>Data Analytics</li>
        <li>Custom Software Development</li>
    </ul>
    
    <h3>Quick Links</h3>
    <p>Please <a href="login.php">login</a> to access your dashboard.</p>
    
    <hr>
    <p style="color: #888; font-size: 12px;">
        <em>Debug mode: Enabled | Server: Apache/2.4 | PHP: <?php echo phpversion(); ?></em>
    </p>
    <?php
}
?>
        </div>
    </div>
</body>
</html>