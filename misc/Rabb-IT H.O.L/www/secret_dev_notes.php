<!DOCTYPE html>
<html>
<head>
    <title>Secret Developer Notes - Rabb-IT H.O.L.</title>
    <link rel="icon" type="image/png" href="favicon.png">
    <style>
        body {
            font-family: 'Courier New', monospace;
            margin: 0;
            padding: 0;
            background: #0a0a0a;
            color: #00ff00;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .terminal {
            background: #1a1a1a;
            border: 2px solid #00ff00;
            border-radius: 5px;
            padding: 30px;
            max-width: 800px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }
        .prompt {
            color: #00ff00;
            margin-bottom: 10px;
        }
        .output {
            color: #ffffff;
            line-height: 1.6;
            margin-bottom: 20px;
        }
        .ascii-art {
            color: #00ff00;
            font-size: 10px;
            line-height: 1.2;
            margin: 20px 0;
            text-align: center;
        }
        .blink {
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0%, 50% { opacity: 1; }
            51%, 100% { opacity: 0; }
        }
        .hidden {
            color: #0a0a0a;
            font-size: 1px;
        }
        .warning {
            color: #ff6b6b;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="terminal">
        <div class="prompt">root@rabb-it.hol:~# cat secret_dev_notes.php</div>
        
        <div class="output">
            <p><span class="warning">╔═══════════════════════════════════════╗</span></p>
            <p><span class="warning">║   DEVELOPER NOTES - CONFIDENTIAL      ║</span></p>
            <p><span class="warning">╚═══════════════════════════════════════╝</span></p>
            <br>
            <p><strong>Date:</strong> 2025-03-15</p>
            <p><strong>Developer:</strong> Alice Williams</p>
            <p><strong>Subject:</strong> Security Audit Findings</p>
            <br>
            <p>TODO List:</p>
            <p>- [X] Fix SQL injection in login form (URGENT!)</p>
            <p>- [X] Patch LFI vulnerability in page parameter</p>
            <p>- [ ] Review all file upload handlers</p>
            <p>- [X] Update password hashing algorithm</p>
            <p>- [ ] Remove debug endpoints before production</p>
            <p>- [ ] Change admin password, too weak (URGENT!)</p>
            <p>- [ ] Disable SSH access</p>
            <br>
            <p><strong>IMPORTANT SECURITY NOTE:</strong></p>
            <p>Found multiple security issues during penetration testing.</p>
            <p>If you're reading this, you probably found the robots.txt file.</p>
            <p>Good job on following the standard enumeration process, but...</p>
            <br>
            <p class="warning">🚩 You thought it would be that easy? 🚩</p>
            <br>
            <p>The real treasure isn't always where you expect it to be.</p>
            <p>Sometimes the most obvious things are the most overlooked.</p>
            <p>Think smaller.</p>
            <br>
            <p>Not all valuable data is in files or databases.</p>
            <p>Sometimes it's the little details.</p>
            <br>
            <p class="warning">Keep digging, you're on the right path.</p>
            <p class="warning">But wrong direction. 😈</p>
            <br>
            <p>-- Alice</p>
        </div>
        
        <div class="prompt">root@rabb-it.hol:~# <span class="blink">█</span></div>
        
        <!-- Yeah, that's a comment alright. But still not a flag -->
        
        <div class="hidden">
            Note: change the admin password from "admin123" to something stronger ASAP!
        </div>
    </div>
</body>
</html>
