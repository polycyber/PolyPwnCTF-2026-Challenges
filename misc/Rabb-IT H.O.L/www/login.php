<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);
?>
<!DOCTYPE html>
<html>
<head>
    <title>Login - Rabb-IT H.O.L.</title>
    <link rel="icon" type="image/png" href="favicon.png">
    <link rel="stylesheet" href="style.css">
    <style>
        body {
            display: flex;
            justify-content: center;
            align-items: center;
        }
    </style>
    <script>
        window.addEventListener('DOMContentLoaded', function() {
            var analyticsData = {
                page: 'login',
                timestamp: new Date().getTime(),
                session_id: 'sess_' + Math.random().toString(36).substr(2, 9),
                metadata: 'TmV0d29yayByZXF1ZXN0cyB3b3VsZCBiZSBhIGdvb2QgcGxhY2UgdG8gaGlkZSBhIGZsYWcgcmlnaHQ/'
            };
            
            fetch('/api/analytics', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Client-Version': '2.1.4',
                    'X-Session-Token': btoa('user_session_' + Date.now())
                },
                body: JSON.stringify(analyticsData)
            }).catch(function(err) {
                console.log('Analytics tracking initialized');
            });
            
            setTimeout(function() {
                fetch('/api/telemetry?data=' + encodeURIComponent(analyticsData.metadata), {
                    method: 'GET',
                    mode: 'no-cors'
                }).catch(function() {});
            }, 1000);
        });
    </script>
</head>
<body>
    <div class="login-container">
        <h2>🔒 Rabb-IT H.O.L. Login</h2>
        
        <?php
        $db_host = 'localhost';
        $db_user = 'ctf_user';
        $db_pass = 'ctf_password_2026';
        $db_name = 'ctf_db';
        
        $conn = @new mysqli($db_host, $db_user, $db_pass, $db_name);
        
        if ($conn->connect_error) {
            echo "<div class='error'>Database connection failed. Please try again later.</div>";
            echo "<!-- Debug: " . htmlspecialchars($conn->connect_error) . " -->";
        } elseif ($_SERVER['REQUEST_METHOD'] == 'POST') {
            $username = $_POST['username'] ?? '';
            $password = $_POST['password'] ?? '';
            
            $query = "SELECT * FROM users WHERE username = '" . $username . "' AND password = MD5('" . $password . "')";
            
            if (isset($_GET['debug'])) {
                echo "<div class='debug'><strong>Debug Query:</strong><br>" . htmlspecialchars($query) . "</div>";
            }
            
            $result = $conn->query($query);
            
            if ($result && $result->num_rows > 0) {
                $user = $result->fetch_assoc();
                echo "<div class='success'>Welcome back, " . htmlspecialchars($user['username']) . "!</div>";
                echo "<p>Role: " . htmlspecialchars($user['role']) . "</p>";
                echo "<p>Email: " . htmlspecialchars($user['email']) . "</p>";
                
                $user_id = $user['id'];
                $secret_query = "SELECT secret_data FROM secrets WHERE user_id = " . $user_id;
                $secret_result = $conn->query($secret_query);
                
                if ($secret_result && $secret_result->num_rows > 0) {
                    $secret = $secret_result->fetch_assoc();
                    echo "<div class='success'>" . htmlspecialchars($secret['secret_data']) . "</div>";
                }
            } else {
                echo "<div class='error'>Invalid username or password!</div>";
                if ($conn->error) {
                    echo "<div class='debug'><strong>SQL Error:</strong><br>" . htmlspecialchars($conn->error) . "</div>";
                }
            }
        }
        ?>
        
        <form method="POST" action="login.php<?php echo isset($_GET['debug']) ? '?debug=1' : ''; ?>">
            <div class="form-group">
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            
            <input type="submit" value="Login">
        </form>
        
        <div class="back-link">
            <a href="index.php">← Back to Home</a>
        </div>
        
        <!-- Remove development mode before pushing to production. Access it with ?debug=1 -->
    </div>
</body>
</html>