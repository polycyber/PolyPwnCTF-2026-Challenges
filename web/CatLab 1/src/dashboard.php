<?php
include 'db.php';
include 'header.php';
?>

<div class="page-header">
    <h1>Experiment Gallery</h1>
    <p>Logged in as <strong><?php echo htmlspecialchars($currentUser['username']); ?></strong> &mdash; Viewing successful trash-to-feline conversions</p>
</div>

<div class="lab-card" style="margin-bottom: 1.5rem;">
    <h2 style="margin-bottom: 0.75rem;">About CatLab</h2>
    <p style="margin: 0 0 0.75rem 0; line-height: 1.7;">
        Founded in 2021 under a classified research grant, <strong>CatLab</strong> is the world's only
        operational Trash-to-Feline Transmogrification facility. Our proprietary <em>BioSynth-9</em>
        process breaks down discarded industrial and domestic waste at the molecular level and
        reassembles the organic substrate into fully functional feline lifeforms — complete with
        autonomous motor function, cognitive response patterns, and an attitude problem.
    </p>
    <p style="margin: 0 0 0.75rem 0; line-height: 1.7;">
        Each subject undergoes a rigorous 72-hour post-synthesis evaluation covering structural
        integrity, behavioural stability, hazard classification, and dietary compatibility before
        being admitted to the Experiment Gallery. Subjects that fail evaluation are returned to the
        waste stream for reprocessing.
    </p>
    <p style="margin: 0; line-height: 1.7; color: #8b949e; font-size: 0.85rem;">
        <strong style="color: #f0883e;">WARNING:</strong> CatLab personnel are reminded that subjects
        rated <em>ELEVATED</em> hazard must not be approached without insulated gloves and a Faraday
        cage. The lab accepts no liability for data loss, electrical fires, or existential crises
        caused by prolonged eye contact with Gen-2 subjects.
    </p>
</div>

<div class="cat-grid">

    <!-- Subject #001 — Rusty -->
    <div class="cat-card">
        <img src="static/images/cat1.jpg" alt="Subject: Rusty">
        <div class="cat-card-body">
            <p class="cat-subject-label">Subject #001 &mdash; 2023-09-04</p>
            <p class="cat-name">Rusty</p>

            <div class="cat-badges">
                <span class="badge badge-success">TRANSMOGRIFIED</span>
                <span class="badge badge-info">Gen-1</span>
                <span class="badge badge-warn">HAZARD: MODERATE</span>
            </div>

            <hr class="cat-divider">

            <div class="cat-stats">
                <span class="cat-stat-key">Material</span>
                <span class="cat-stat-val">Oxidised scrap metal &amp; copper wire</span>

                <span class="cat-stat-key">Age</span>
                <span class="cat-stat-val">16 months (post-transmogrification)</span>

                <span class="cat-stat-key">Weight</span>
                <span class="cat-stat-val">5.1 kg</span>

                <span class="cat-stat-key">Personality</span>
                <span class="cat-stat-val">Aloof, territorial, hisses at magnets</span>

                <span class="cat-stat-key">Stability</span>
                <span class="cat-stat-val">
                    <span class="stability-bar">
                        <span class="stability-fill" style="width:73%; background:#f0883e;"></span>
                    </span>
                    73%
                </span>

                <span class="cat-stat-key">Scientist</span>
                <span class="cat-stat-val">Dr. Furrenstein</span>
            </div>
        </div>
    </div>

    <!-- Subject #002 — Scraps -->
    <div class="cat-card">
        <img src="static/images/cat2.jpg" alt="Subject: Scraps">
        <div class="cat-card-body">
            <p class="cat-subject-label">Subject #002 &mdash; 2023-11-17</p>
            <p class="cat-name">Scraps</p>

            <div class="cat-badges">
                <span class="badge badge-success">TRANSMOGRIFIED</span>
                <span class="badge badge-info">Gen-1</span>
                <span class="badge badge-success">HAZARD: LOW</span>
            </div>

            <hr class="cat-divider">

            <div class="cat-stats">
                <span class="cat-stat-key">Material</span>
                <span class="cat-stat-val">Torn fabric &amp; discarded buttons</span>

                <span class="cat-stat-key">Age</span>
                <span class="cat-stat-val">14 months (post-transmogrification)</span>

                <span class="cat-stat-key">Weight</span>
                <span class="cat-stat-val">3.8 kg</span>

                <span class="cat-stat-key">Personality</span>
                <span class="cat-stat-val">Clingy, anxious, sheds synthetic fibres</span>

                <span class="cat-stat-key">Stability</span>
                <span class="cat-stat-val">
                    <span class="stability-bar">
                        <span class="stability-fill" style="width:91%; background:#238636;"></span>
                    </span>
                    91%
                </span>

                <span class="cat-stat-key">Scientist</span>
                <span class="cat-stat-val">Dr. Furrenstein</span>
            </div>
        </div>
    </div>

    <!-- Subject #003 — Gizmo -->
    <div class="cat-card">
        <img src="static/images/cat3.jpg" alt="Subject: Gizmo">
        <div class="cat-card-body">
            <p class="cat-subject-label">Subject #003 &mdash; 2024-04-02</p>
            <p class="cat-name">Gizmo</p>

            <div class="cat-badges">
                <span class="badge badge-success">TRANSMOGRIFIED</span>
                <span class="badge badge-info">Gen-2</span>
                <span class="badge badge-danger">HAZARD: ELEVATED</span>
            </div>

            <hr class="cat-divider">

            <div class="cat-stats">
                <span class="cat-stat-key">Material</span>
                <span class="cat-stat-val">Broken circuit boards &amp; spare capacitors</span>

                <span class="cat-stat-key">Age</span>
                <span class="cat-stat-val">7 months (post-transmogrification)</span>

                <span class="cat-stat-key">Weight</span>
                <span class="cat-stat-val">4.4 kg</span>

                <span class="cat-stat-key">Personality</span>
                <span class="cat-stat-val">Hyperactive, chews cables, emits RF interference</span>

                <span class="cat-stat-key">Stability</span>
                <span class="cat-stat-val">
                    <span class="stability-bar">
                        <span class="stability-fill" style="width:58%; background:#f85149;"></span>
                    </span>
                    58%
                </span>

                <span class="cat-stat-key">Scientist</span>
                <span class="cat-stat-val">Dr. Meowski</span>
            </div>
        </div>
    </div>

</div>

</div><!-- .container -->
</body>
</html>
