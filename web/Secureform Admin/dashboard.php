<?php
require_once 'config.php';
requireAuth();

$db = getDB();
$message = '';
$messageType = '';

// Handle new entry submission
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'add_entry') {
    $name = isset($_POST['name']) ? trim($_POST['name']) : '';
    $email = isset($_POST['email']) ? trim($_POST['email']) : '';
    $msg = isset($_POST['message']) ? trim($_POST['message']) : '';
    
    if (!empty($name)) {
        $stmt = $db->prepare("INSERT INTO entries (name, email, message, language, submission_time) VALUES (?, ?, ?, 'en', NOW())");
        $stmt->execute([$name, $email, $msg]);
        $message = 'Entry added successfully!';
        $messageType = 'success';
        
        // Small delay to ensure different timestamps
        usleep(100000);
    } else {
        $message = 'Name is required.';
        $messageType = 'error';
    }
}

// Handle entry deletion
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'delete_entry') {
    $id = isset($_POST['id']) ? intval($_POST['id']) : 0;
    if ($id > 0) {
        $stmt = $db->prepare("DELETE FROM entries WHERE id = ?");
        $stmt->execute([$id]);
        $message = 'Entry deleted.';
        $messageType = 'success';
    }
}

// Handle clear all
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['action']) && $_POST['action'] === 'clear_all') {
    $db->exec("DELETE FROM entries");
    $message = 'All entries cleared.';
    $messageType = 'success';
}

// THE VULNERABLE QUERY - ORDER BY injection
// sanitize_text_field doesn't properly sanitize for SQL context!
$order = isset($_GET['order']) ? sanitize_text_field($_GET['order']) : 'DESC';
$orderby = isset($_GET['orderby']) ? sanitize_text_field($_GET['orderby']) : 'submission_time';
$language = 'en';

// Build the vulnerable query (mimics WordPress CF7 style)
$table_name = 'entries';
try {
    $query = sprintf("SELECT * FROM %s WHERE language = :lang ORDER BY %s %s", $table_name, $orderby, $order);
    $stmt = $db->prepare($query);
    $stmt->execute([':lang' => $language]);
    $entries = $stmt->fetchAll(PDO::FETCH_ASSOC);
} catch (PDOException $e) {
    $entries = [];
    $message = 'An error occurred while fetching entries.';
    $messageType = 'error';
}

// Logout handling
if (isset($_GET['logout'])) {
    session_destroy();
    header('Location: index.php');
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Form Entries - SecureForm Admin</title>
    <link rel="stylesheet" href="style.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&family=Outfit:wght@300;400;500;600&display=swap" rel="stylesheet">
</head>
<body class="dashboard-page">
    <nav class="navbar">
        <div class="nav-brand">
            <span class="logo-icon">◈</span>
            <span>SecureForm Admin</span>
        </div>
        <div class="nav-links">
            <a href="?logout=1" class="nav-link logout-link">Logout</a>
        </div>
    </nav>

    <main class="dashboard-content">
        <div class="dashboard-header">
            <h1>Contact Form Entries</h1>
            <p class="subtitle">Manage submitted form entries</p>
        </div>

        <?php if ($message): ?>
            <div class="alert alert-<?php echo $messageType; ?>">
                <?php echo htmlspecialchars($message); ?>
            </div>
        <?php endif; ?>

        <div class="dashboard-grid">
            <!-- Add Entry Form -->
            <section class="card add-entry-card">
                <h2>Add New Entry</h2>
                <form method="POST" class="entry-form">
                    <input type="hidden" name="action" value="add_entry">
                    
                    <div class="form-group">
                        <label for="name">Name *</label>
                        <input type="text" id="name" name="name" required placeholder="John Doe">
                    </div>
                    
                    <div class="form-group">
                        <label for="email">Email</label>
                        <input type="email" id="email" name="email" placeholder="john@example.com">
                    </div>
                    
                    <div class="form-group">
                        <label for="message">Message</label>
                        <textarea id="message" name="message" rows="3" placeholder="Your message..."></textarea>
                    </div>
                    
                    <button type="submit" class="btn btn-primary">Add Entry</button>
                </form>
            </section>

            <!-- Entries List -->
            <section class="card entries-card">
                <div class="entries-header">
                    <h2>Entries <span class="entry-count">(<?php echo count($entries); ?>)</span></h2>
                    <div class="entries-actions">
                        <form method="POST" style="display:inline;">
                            <input type="hidden" name="action" value="clear_all">
                            <button type="submit" class="btn btn-danger btn-sm" onclick="return confirm('Clear all entries?')">Clear All</button>
                        </form>
                    </div>
                </div>

                <!-- Sort Controls -->
                <div class="sort-controls">
                    <span class="sort-label">Sort by:</span>
                    <a href="?orderby=id&order=ASC" class="sort-btn <?php echo ($orderby === 'id' && $order === 'ASC') ? 'active' : ''; ?>">ID ↑</a>
                    <a href="?orderby=id&order=DESC" class="sort-btn <?php echo ($orderby === 'id' && $order === 'DESC') ? 'active' : ''; ?>">ID ↓</a>
                    <a href="?orderby=submission_time&order=ASC" class="sort-btn <?php echo ($orderby === 'submission_time' && $order === 'ASC') ? 'active' : ''; ?>">Time ↑</a>
                    <a href="?orderby=submission_time&order=DESC" class="sort-btn <?php echo ($orderby === 'submission_time' && $order === 'DESC') ? 'active' : ''; ?>">Time ↓</a>
                    <a href="?orderby=name&order=ASC" class="sort-btn <?php echo ($orderby === 'name' && $order === 'ASC') ? 'active' : ''; ?>">Name ↑</a>
                </div>

                <?php if (empty($entries)): ?>
                    <div class="empty-state">
                        <div class="empty-icon">📭</div>
                        <p>No entries yet.</p>
                        <p class="hint">Add some entries using the form on the left.</p>
                    </div>
                <?php else: ?>
                    <div class="entries-list">
                        <?php foreach ($entries as $index => $entry): ?>
                            <div class="entry-item">
                                <div class="entry-meta">
                                    <span class="entry-id">#<?php echo htmlspecialchars($entry['id']); ?></span>
                                    <span class="entry-position">Position: <?php echo $index + 1; ?></span>
                                </div>
                                <div class="entry-content">
                                    <div class="entry-name"><?php echo htmlspecialchars($entry['name']); ?></div>
                                    <?php if ($entry['email']): ?>
                                        <div class="entry-email"><?php echo htmlspecialchars($entry['email']); ?></div>
                                    <?php endif; ?>
                                    <?php if ($entry['message']): ?>
                                        <div class="entry-message"><?php echo htmlspecialchars($entry['message']); ?></div>
                                    <?php endif; ?>
                                    <div class="entry-time"><?php echo htmlspecialchars($entry['submission_time']); ?></div>
                                </div>
                                <form method="POST" class="entry-delete">
                                    <input type="hidden" name="action" value="delete_entry">
                                    <input type="hidden" name="id" value="<?php echo $entry['id']; ?>">
                                    <button type="submit" class="btn-delete" title="Delete">×</button>
                                </form>
                            </div>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>
            </section>
        </div>
    </main>

    <footer class="footer">
        <p>SecureForm Admin Panel v2.1.4</p>
    </footer>
</body>
</html>
