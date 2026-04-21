<?php
// polycyber{s0m37hing_is_wr0ng_wi7h_my_c47}

include 'db.php';

$authResult = authenticateFromCookies($conn);

if ($authResult['status'] === 'unauthenticated') {
    header("Location: index.php");
    exit;
}

if ($authResult['status'] === 'expired') {
    outputTokenExpiredPage();
}

$currentUser = $authResult['user'];

// Run the transmogrification (SSRF) if admin submitted a URL
$curlResponse = null;
$curlError    = null;

if ($currentUser['is_admin'] && $_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['url'])) {
    $url = $_POST['url'];
    $ch  = curl_init();
    curl_setopt($ch, CURLOPT_URL, $url);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
    curl_setopt($ch, CURLOPT_CONNECTTIMEOUT, 3);
    curl_setopt($ch, CURLOPT_TIMEOUT, 5);
    $curlResponse = curl_exec($ch);
    if (curl_errno($ch)) {
        $curlError = curl_error($ch);
    }
}

// Generate random cat result if we got a response
$catResult = null;
if ($curlResponse !== null || $curlError !== null) {
    $names = ['Pixel', 'Glitch', 'Weld', 'Smudge', 'Bolt', 'Cinder', 'Flux', 'Gravel', 'Splint', 'Soot'];
    $materials = [
        'Crumpled aluminium cans &amp; bottle caps',
        'Shredded newspaper &amp; cardboard pulp',
        'Broken glass &amp; PVC insulation',
        'Discarded circuit boards &amp; solder debris',
        'Torn denim &amp; zip fasteners',
        'Corroded battery cells &amp; copper shavings',
        'Crushed plastic bottles &amp; nylon rope',
        'Old rubber tyres &amp; engine grease',
    ];
    $personalities = [
        'Brooding, stares at walls, ignores commands',
        'Compulsively knocks things off surfaces',
        'Purrs in binary, dislikes prime numbers',
        'Aggressive to printers, gentle with houseplants',
        'Nocturnal, photosensitive, hides in server racks',
        'Clingy, produces static discharge when stroked',
        'Eats only triangular food, judges everyone',
        'Silent for hours, then screams at 3 AM',
    ];
    $scientists = ['Dr. Furrenstein', 'Dr. Meowski', 'Dr. Clawson', 'Prof. Tabitha'];

    $stability  = rand(30, 98);
    $imgNum     = rand(1, 3);
    $subjectNum = rand(4, 999);
    $weight     = number_format(rand(28, 72) / 10, 1);
    $ageMonths  = rand(1, 3);
    $gen        = rand(0, 1) ? 'Gen-2' : 'Gen-1';

    if ($stability >= 80)      { $stabColor = '#238636'; $hazard = 'LOW';      $hazardClass = 'badge-success'; }
    elseif ($stability >= 55)  { $stabColor = '#f0883e'; $hazard = 'MODERATE'; $hazardClass = 'badge-warn'; }
    else                       { $stabColor = '#f85149'; $hazard = 'ELEVATED'; $hazardClass = 'badge-danger'; }

    $catResult = [
        'name'        => $names[array_rand($names)],
        'subject'     => str_pad($subjectNum, 3, '0', STR_PAD_LEFT),
        'date'        => date('Y-m-d'),
        'img'         => $imgNum,
        'material'    => $materials[array_rand($materials)],
        'age'         => "$ageMonths month" . ($ageMonths > 1 ? 's' : '') . ' (post-transmogrification)',
        'weight'      => "$weight kg",
        'personality' => $personalities[array_rand($personalities)],
        'stability'   => $stability,
        'stabColor'   => $stabColor,
        'hazard'      => $hazard,
        'hazardClass' => $hazardClass,
        'gen'         => $gen,
        'scientist'   => $scientists[array_rand($scientists)],
    ];
}

include 'header.php';
?>

<div class="page-header">
    <h1>Transmogrification Chamber</h1>
    <p>Submit a trash photo URL to initiate the BioSynth-9 conversion pipeline</p>
</div>

<?php if (!$currentUser['is_admin']): ?>

<div class="lab-card" style="text-align:center;">
    <p style="font-size:2.5rem; margin:0 0 0.5rem 0;">🔒</p>
    <h2 style="margin-bottom:0.5rem;">Clearance Insufficient</h2>
    <p style="color:#8b949e; margin:0 0 1.5rem 0; max-width:480px; margin-inline:auto;">
        The Transmogrification Chamber is restricted to <strong style="color:#f0883e;">Chief Scientists</strong> only.
        Your current clearance level does not permit access to this module.
        Contact lab administration if you believe this is an error.
    </p>
    <a href="dashboard.php" class="btn">Return to Gallery</a>
</div>

<?php else: ?>

<!-- Loading overlay (shown while form submits) -->
<div id="loading-overlay" style="display:none; position:fixed; inset:0; background:rgba(13,17,23,0.93);
     z-index:9999; flex-direction:column; align-items:center; justify-content:center; gap:1.5rem;">
    <div class="loader-ring"></div>
    <div style="color:#58a6ff; font-family:monospace; font-size:1rem; letter-spacing:.1em; text-align:center;">
        TRANSMOGRIFICATION IN PROGRESS<span id="loader-dots"></span><br>
        <span style="color:#8b949e; font-size:0.8rem;">BioSynth-9 pipeline active — do not close this tab</span>
    </div>
</div>

<div class="lab-card">
    <form id="transmogrify-form" method="POST" class="ssrf-form">
        <div class="form-group">
            <label for="url">Trash Photo URL</label>
            <input type="text" id="url" name="url"
                   placeholder="http://internal-archive/trash/sample.jpg"
                   value="<?php echo isset($_POST['url']) ? htmlspecialchars($_POST['url']) : ''; ?>">
        </div>
        <button type="submit" class="btn">TRANSMOGRIFY</button>
    </form>
</div>

<?php if ($catResult): ?>

<!-- Cat result card -->
<div class="lab-card" style="margin-top:1.5rem;">
    <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:1.25rem;">
        <span class="status-dot" style="background:#238636;"></span>
        <span style="color:#238636; font-family:monospace; font-size:0.85rem; letter-spacing:.08em;">
            TRANSMOGRIFICATION COMPLETE — NEW SUBJECT REGISTERED
        </span>
    </div>

    <div style="max-width:320px; margin:0 auto;">
        <div class="cat-card">
            <img src="static/images/cat<?php echo $catResult['img']; ?>.jpg"
                 alt="Subject: <?php echo htmlspecialchars($catResult['name']); ?>">
            <div class="cat-card-body">
                <p class="cat-subject-label">
                    Subject #<?php echo $catResult['subject']; ?> &mdash; <?php echo $catResult['date']; ?>
                </p>
                <p class="cat-name"><?php echo htmlspecialchars($catResult['name']); ?></p>

                <div class="cat-badges">
                    <span class="badge badge-success">TRANSMOGRIFIED</span>
                    <span class="badge badge-info"><?php echo $catResult['gen']; ?></span>
                    <span class="badge <?php echo $catResult['hazardClass']; ?>">
                        HAZARD: <?php echo $catResult['hazard']; ?>
                    </span>
                </div>

                <hr class="cat-divider">

                <div class="cat-stats">
                    <span class="cat-stat-key">Material</span>
                    <span class="cat-stat-val"><?php echo $catResult['material']; ?></span>

                    <span class="cat-stat-key">Age</span>
                    <span class="cat-stat-val"><?php echo $catResult['age']; ?></span>

                    <span class="cat-stat-key">Weight</span>
                    <span class="cat-stat-val"><?php echo $catResult['weight']; ?></span>

                    <span class="cat-stat-key">Personality</span>
                    <span class="cat-stat-val"><?php echo $catResult['personality']; ?></span>

                    <span class="cat-stat-key">Stability</span>
                    <span class="cat-stat-val">
                        <span class="stability-bar">
                            <span class="stability-fill"
                                  style="width:<?php echo $catResult['stability']; ?>%;
                                         background:<?php echo $catResult['stabColor']; ?>;"></span>
                        </span>
                        <?php echo $catResult['stability']; ?>%
                    </span>

                    <span class="cat-stat-key">Scientist</span>
                    <span class="cat-stat-val"><?php echo htmlspecialchars($catResult['scientist']); ?></span>
                </div>
            </div>
        </div>
    </div>
</div>

<!-- Raw synthesis log (curl output) -->
<div class="lab-card result-block">
    <h3>// RAW SYNTHESIS LOG</h3>
    <?php if ($curlError): ?>
        <pre class="result-pre" style="color:#f85149;"><?php echo htmlspecialchars($curlError); ?></pre>
    <?php else: ?>
        <pre class="result-pre"><?php echo base64_encode($curlResponse); ?></pre>
    <?php endif; ?>
</div>

<?php endif; ?>

<?php endif; ?>

</div><!-- .container -->

<style>
.loader-ring {
    width: 56px; height: 56px;
    border: 4px solid #21262d;
    border-top-color: #58a6ff;
    border-radius: 50%;
    animation: spin 0.9s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>

<script>
document.getElementById('transmogrify-form').addEventListener('submit', function (e) {
    var urlVal = document.getElementById('url').value.trim();
    if (!urlVal) return; // let browser handle empty validation

    e.preventDefault();
    var overlay = document.getElementById('loading-overlay');
    overlay.style.display = 'flex';

    // Animate the trailing dots
    var dots = document.getElementById('loader-dots');
    var count = 0;
    setInterval(function () {
        dots.textContent = '.'.repeat((count++ % 3) + 1);
    }, 400);

    var form = this;
    setTimeout(function () { form.submit(); }, 1800);
});
</script>

</body>
</html>
