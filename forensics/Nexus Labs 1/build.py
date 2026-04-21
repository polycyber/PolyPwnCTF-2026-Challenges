#!/usr/bin/env python3
"""
Nexus Labs CTF — Combined VCS Challenge Builder
================================================
One site directory. Both .git and .hg initialised in the same root.
Same content files, independent VCS histories, independent flags.

Git track  (3 flags):
  Flag 1 — deleted file in git history
  Flag 2 — orphan commit under refs/experiments/archived/experiment-7
  Flag 3 — git note on a non-HEAD commit (refs/notes/deployment)

Mercurial track (1 flag, hard):
  Flag 4 — split across commit extras on rev 1 and rev 3

Usage:
  python3 build.py [output-dir]
  output-dir defaults to ./challenge
"""

import os, sys, shutil, subprocess, base64, textwrap

CHALLENGE_DIR = sys.argv[1] if len(sys.argv) > 1 else "./challenge"

# Git flags
GIT_FLAG1 = "polycyber{exp0sed_g1t_1s_a_cl4ssic_m1stake}"
GIT_FLAG2 = "polycyber{d3ad_c0mm1ts_t3ll_t4les_f0rgott3n}"
GIT_FLAG3 = "polycyber{g1t_n0t3s_4r3_th3_h1dd3n_d1mens10n}"

# Mercurial flag — split at build time, joined at solve time
HG_FLAG_A = "polycyber{hg_extr"
HG_FLAG_B = "as_r3v34l_4ll}"

# ── Helpers ───────────────────────────────────────────────────────────────────

def run(*args, cwd=CHALLENGE_DIR, check=True, capture=False, extra_env=None):
    env = {**os.environ}
    if extra_env:
        env.update(extra_env)
    result = subprocess.run(
        list(args), cwd=cwd, check=False,
        capture_output=True, text=True, env=env,
    )
    if not capture and result.stdout:
        pass  # suppress normal output
    if check and result.returncode != 0:
        print(f"[!] Command failed: {list(args)}")
        print(result.stdout[-2000:] if result.stdout else "")
        print(result.stderr[-2000:] if result.stderr else "")
        raise subprocess.CalledProcessError(result.returncode, list(args))
    if capture:
        return result
    return result

def git(*args, capture=False):
    return run("git", *args, capture=capture)

def hg(*args, capture=False):
    return run("hg", *args, capture=capture, extra_env={"HGENCODING": "utf-8"})

def write(path, content):
    full = os.path.join(CHALLENGE_DIR, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w").write(textwrap.dedent(content).lstrip("\n"))

def read(path):
    return open(os.path.join(CHALLENGE_DIR, path)).read()

def patch(path, old, new):
    content = read(path)
    open(os.path.join(CHALLENGE_DIR, path), "w").write(content.replace(old, new))

def git_commit(msg):
    git("add", "-A")
    git("commit", "-q", "-m", msg)

def hg_commit(msg, hg_extra=None):
    """
    Commit to Mercurial, optionally injecting extras into the changeset.
    hg_extra: "key=value" string.

    Uses the Mercurial Python API to commit with custom extras directly,
    avoiding the unreliable strip+reimport approach.
    """
    # Verify there are staged changes before committing
    status = hg("status", capture=True).stdout.strip()
    if not status:
        raise RuntimeError(f"hg_commit('{msg}'): nothing to commit — working dir is clean")

    if not hg_extra:
        hg("commit", "-m", msg, "-u", "ops@nexuslabs.internal")
        return

    key, _, val = hg_extra.partition("=")
    key = key.strip()
    val = val.strip()

    # Use the Mercurial Python API to commit with custom extras
    from mercurial import ui as hgui, hg as hgmod
    u = hgui.ui.load()
    u.setconfig(b"ui", b"username", b"ops@nexuslabs.internal")
    repo = hgmod.repository(u, path=CHALLENGE_DIR.encode())
    extra = {key.encode(): val.encode()}
    repo.commit(
        text=msg.encode(),
        user=b"ops@nexuslabs.internal",
        extra=extra,
    )

# ── Scaffold ──────────────────────────────────────────────────────────────────

print(f"[*] Building challenge in: {CHALLENGE_DIR}")
if os.path.exists(CHALLENGE_DIR):
    print("[!] Directory already exists. Remove it first.")
    sys.exit(1)
os.makedirs(CHALLENGE_DIR)

# ── Init both repos ───────────────────────────────────────────────────────────

git("init", "-q")
git("config", "user.email", "ops@nexuslabs.internal")
git("config", "user.name", "Nexus Ops")
git("config", "core.autocrlf", "false")

hg("init")
with open(os.path.join(CHALLENGE_DIR, ".hg", "hgrc"), "w") as f:
    f.write("[ui]\nusername = ops@nexuslabs.internal\n")

# .hgignore so mercurial doesn't track .git internals
write(".hgignore", "syntax: glob\n.git/\n")

# ── Site files ────────────────────────────────────────────────────────────────

write("index.html", """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>NEXUS LABORATORIES</title>
  <link rel="stylesheet" href="static/css/style.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
</head>
<body>
  <div class="scanlines"></div>
  <div class="noise"></div>

  <header>
    <div class="logo">
      <span class="logo-bracket">[</span>
      NEXUS<span class="logo-accent">LABS</span>
      <span class="logo-bracket">]</span>
    </div>
    <div class="header-right">
      <span class="status-dot"></span>
      <span class="status-text">SECURE FACILITY — AUTHORIZED PERSONNEL ONLY</span>
    </div>
  </header>

  <main>
    <section class="hero">
      <div class="hero-label">// CLASSIFIED RESEARCH DIVISION</div>
      <h1>UNDERGROUND<br><span class="accent">RESEARCH</span><br>COMPLEX</h1>
      <p class="hero-sub">
        Nexus Laboratories operates a subterranean research facility at an
        undisclosed location. Access to this portal is restricted to cleared
        personnel with an active Level-4 security badge.
      </p>
      <div class="cta-row">
        <a href="#" class="btn btn-primary" onclick="handleAuth(event)">ACCESS TERMINAL</a>
        <a href="#" class="btn btn-ghost">REQUEST CLEARANCE</a>
      </div>
      <div class="depth-indicator">
        <span>FACILITY DEPTH</span>
        <span class="depth-value">−312m</span>
      </div>
    </section>

    <section class="divisions">
      <div class="section-header">
        <span class="section-tag">// RESEARCH DIVISIONS</span>
      </div>
      <div class="grid">
        <div class="card">
          <div class="card-tag">DIV-01</div>
          <h3>Quantum Dynamics</h3>
          <p>High-energy particle research and quantum state manipulation at cryogenic temperatures.</p>
          <div class="card-status">STATUS: <span class="status-active">ACTIVE</span></div>
        </div>
        <div class="card">
          <div class="card-tag">DIV-02</div>
          <h3>Biogenesis Lab</h3>
          <p>Synthetic organism development and cellular reconstruction protocols.</p>
          <div class="card-status">STATUS: <span class="status-restricted">RESTRICTED</span></div>
        </div>
        <div class="card">
          <div class="card-tag">DIV-03</div>
          <h3>Neural Interface</h3>
          <p>Brain-computer interface development. Cognitive augmentation research.</p>
          <div class="card-status">STATUS: <span class="status-active">ACTIVE</span></div>
        </div>
        <div class="card">
          <div class="card-tag">DIV-04</div>
          <h3>Dark Matter Studies</h3>
          <p>Detection and analysis of non-baryonic matter. Gravitational anomaly mapping.</p>
          <div class="card-status">STATUS: <span class="status-offline">OFFLINE</span></div>
        </div>
      </div>
    </section>

    <section class="terminal-section">
      <div class="terminal">
        <div class="terminal-bar">
          <span class="terminal-title">ops@nexus-secure:~$</span>
          <span class="terminal-dot r"></span>
          <span class="terminal-dot y"></span>
          <span class="terminal-dot g"></span>
        </div>
        <div class="terminal-body" id="tbody">
          <p><span class="prompt">$</span> uptime</p>
          <p class="out">Facility online for 847 days, 14:22:07</p>
          <p><span class="prompt">$</span> df -h /secure</p>
          <p class="out">Filesystem: /dev/sdb1 &nbsp; Size: 48T &nbsp; Used: 31T &nbsp; Avail: 17T</p>
          <p><span class="prompt">$</span> last login</p>
          <p class="out">dr.chen &nbsp;&nbsp; pts/0 &nbsp; 2024-11-03 02:41 (10.0.0.44)</p>
          <p><span class="prompt">$</span> <span class="cursor">█</span></p>
        </div>
      </div>
    </section>
  </main>

  <footer>
    <p>NEXUS LABORATORIES — CLASSIFIED FACILITY // ALL ACTIVITY LOGGED AND MONITORED</p>
    <p class="footer-sub">Unauthorized access will be prosecuted under the Nexus Security Act §44.7</p>
  </footer>

  <script src="static/js/app.js"></script>
</body>
</html>
""")

write("static/css/style.css", """
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap');

:root {
  --bg:        #050a05;
  --bg2:       #080f08;
  --panel:     #0a140a;
  --border:    #1a3a1a;
  --green:     #00ff41;
  --green-dim: #00b32c;
  --green-dark:#003d0d;
  --amber:     #ffb000;
  --red:       #ff2d2d;
  --text:      #b8d4b8;
  --text-dim:  #4a7a4a;
  --mono:      'Share Tech Mono', monospace;
  --display:   'Orbitron', sans-serif;
}

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body { font-family: var(--mono); background: var(--bg); color: var(--text); overflow-x: hidden; }

.scanlines {
  position: fixed; inset: 0; z-index: 100; pointer-events: none;
  background: repeating-linear-gradient(0deg, transparent, transparent 2px, rgba(0,0,0,0.08) 2px, rgba(0,0,0,0.08) 4px);
}
.noise {
  position: fixed; inset: 0; z-index: 99; pointer-events: none; opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}

header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 2.5rem; border-bottom: 1px solid var(--border);
  background: var(--bg2); position: sticky; top: 0; z-index: 50;
}
.logo { font-family: var(--display); font-size: 1.2rem; font-weight: 900; color: var(--green); letter-spacing: 4px; text-shadow: 0 0 20px rgba(0,255,65,0.5); }
.logo-bracket { color: var(--text-dim); }
.logo-accent { color: var(--amber); }
.header-right { display: flex; align-items: center; gap: .6rem; font-size: .7rem; color: var(--text-dim); }
.status-dot { width: 8px; height: 8px; border-radius: 50%; background: var(--green); box-shadow: 0 0 8px var(--green); animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:.3} }

.hero { padding: 7rem 2.5rem 5rem; max-width: 800px; margin: 0 auto; }
.hero-label { font-size: .75rem; color: var(--green-dim); letter-spacing: 3px; margin-bottom: 2rem; }
h1 { font-family: var(--display); font-size: clamp(2.5rem, 7vw, 5rem); font-weight: 900; line-height: 1.05; color: #e8f5e8; text-shadow: 0 0 40px rgba(0,255,65,0.15); margin-bottom: 2rem; }
h1 .accent { color: var(--green); text-shadow: 0 0 30px rgba(0,255,65,0.6); }
.hero-sub { color: var(--text-dim); line-height: 1.8; max-width: 520px; margin-bottom: 2.5rem; font-size: .9rem; }
.cta-row { display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 3rem; }
.btn { font-family: var(--display); font-size: .7rem; font-weight: 700; letter-spacing: 2px; padding: .75rem 1.8rem; text-decoration: none; border: 1px solid; transition: all .2s; }
.btn-primary { background: var(--green); color: #000; border-color: var(--green); box-shadow: 0 0 20px rgba(0,255,65,0.3); }
.btn-primary:hover { box-shadow: 0 0 40px rgba(0,255,65,0.7); }
.btn-ghost { color: var(--green); border-color: var(--border); }
.btn-ghost:hover { border-color: var(--green); }
.depth-indicator { display: inline-flex; gap: 1.5rem; align-items: center; font-size: .7rem; color: var(--text-dim); letter-spacing: 2px; border: 1px solid var(--border); padding: .4rem 1rem; }
.depth-value { color: var(--amber); font-size: .9rem; }

.divisions { padding: 4rem 2.5rem; max-width: 1000px; margin: 0 auto; }
.section-header { margin-bottom: 2rem; }
.section-tag { font-size: .75rem; color: var(--green-dim); letter-spacing: 3px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 1px; background: var(--border); border: 1px solid var(--border); }
.card { background: var(--panel); padding: 1.5rem; }
.card-tag { font-size: .65rem; color: var(--text-dim); letter-spacing: 3px; margin-bottom: .75rem; }
.card h3 { font-family: var(--display); font-size: .85rem; color: #e8f5e8; margin-bottom: .75rem; letter-spacing: 1px; }
.card p { font-size: .78rem; color: var(--text-dim); line-height: 1.7; margin-bottom: 1rem; }
.card-status { font-size: .65rem; letter-spacing: 2px; color: var(--text-dim); }
.status-active { color: var(--green); }
.status-restricted { color: var(--amber); }
.status-offline { color: var(--red); }

.terminal-section { padding: 2rem 2.5rem 5rem; max-width: 700px; margin: 0 auto; }
.terminal { border: 1px solid var(--border); background: #020702; }
.terminal-bar { display: flex; align-items: center; padding: .5rem 1rem; border-bottom: 1px solid var(--border); background: var(--bg2); }
.terminal-title { font-size: .75rem; color: var(--green-dim); flex: 1; }
.terminal-dot { width: 10px; height: 10px; border-radius: 50%; margin-left: .4rem; }
.terminal-dot.r { background: #ff5f57; }
.terminal-dot.y { background: #ffbd2e; }
.terminal-dot.g { background: #28c840; }
.terminal-body { padding: 1.2rem 1.5rem; font-size: .82rem; line-height: 2; }
.prompt { color: var(--green); margin-right: .5rem; }
.out { color: var(--text-dim); padding-left: 1.2rem; }
.cursor { animation: blink .8s step-end infinite; }
@keyframes blink { 50% { opacity: 0; } }

footer { border-top: 1px solid var(--border); padding: 2rem 2.5rem; text-align: center; }
footer p { font-size: .7rem; color: var(--text-dim); letter-spacing: 2px; }
.footer-sub { margin-top: .5rem; font-size: .6rem; color: #2a4a2a; }
""")

write("static/js/app.js", """
// Nexus Labs — Secure Portal v3.0.1
function handleAuth(e) {
  e.preventDefault();
  const lines = [
    'Initializing secure handshake...',
    'Verifying badge credentials...',
    'ERROR: Badge serial not found in registry.',
    'Access denied. Incident logged.',
  ];
  const body = document.getElementById('tbody');
  let i = 0;
  const interval = setInterval(() => {
    if (i >= lines.length) { clearInterval(interval); return; }
    const p = document.createElement('p');
    p.className = 'out';
    p.style.color = i === lines.length - 1 ? '#ff2d2d' : '';
    if (i === 0) {
      p.className = '';
      p.innerHTML = '<span class="prompt">$</span> auth --badge=&lt;redacted&gt;';
    } else {
      p.textContent = lines[i];
    }
    body.insertBefore(p, body.lastElementChild);
    i++;
  }, 600);
}
""")

write("README.md", """
# Nexus Laboratories — Secure Portal

Internal web portal for cleared facility personnel.

## Dev Setup
```
python3 -m http.server 8080
```

Connects to internal API at `https://api.nexuslabs.internal` (facility network only).
""")

# ── Git track ─────────────────────────────────────────────────────────────────
print("[*] Building git history...")

# Add .hgignore to git too so it's tracked as a normal project file
git_commit("feat: initial portal scaffold")

# Git flag 1 — accidentally committed ops config
write(".ops-config", (
    "# Nexus Labs — Ops Configuration\n"
    "# Generated by provisioning script — do not commit\n\n"
    "[database]\n"
    "host     = db-secure-01.nexuslabs.internal\n"
    "port     = 5432\n"
    "user     = nexus_ops\n"
    "password = 9xK_mQ2_pL8_rN5v\n\n"
    "[api]\n"
    "endpoint = https://api.nexuslabs.internal\n"
    "token    = nx-prod-a7f3c9e2b4d1f8a6\n\n"
    "[facility]\n"
    "level    = 4\n"
    "sector   = DEEP-CORE\n"
    f"access_token = {GIT_FLAG1}\n"
))
git_commit("ops: push provisioning config")

write(".gitignore", ".ops-config\n*.env\n*.key\n*.pem\nnode_modules/\n")
git("rm", "-q", ".ops-config")
git_commit("fix: remove ops config from repo — see INC-2024-0819")

patch("index.html", "847 days, 14:22:07", "1,204 days, 09:14:52")
git_commit("content: update facility uptime counter")

patch("static/css/style.css", "clamp(2.5rem, 7vw, 5rem)", "clamp(2.8rem, 7vw, 5.2rem)")
git_commit("style: bump hero heading size slightly on large screens")

run("git", "branch", "-m", "master", "main", check=False)

# Git flag 2 — orphan commit under non-standard ref
git("checkout", "-q", "--orphan", "experiment-7-archive")
git("reset", "-q", "--hard")

flag2_b64 = base64.b64encode(GIT_FLAG2.encode()).decode()
write("EXPERIMENT_LOG.txt", (
    "NEXUS LABORATORIES — Experiment Archive\n"
    "========================================\n"
    "Experiment: EXP-7 — Temporal Displacement Field Test\n"
    "Lead Researcher: Dr. A. Vasquez\n"
    "Classification: EYES ONLY\n"
    "Date closed: 2024-01-30\n\n"
    "Summary:\n"
    "Experiment suspended following anomalous readings on day 3.\n"
    "Full data archived per protocol ARCH-9. Results not for distribution.\n\n"
    "Archive checksum (base64 — verify against secure manifest):\n"
    f"  {flag2_b64}\n\n"
    "Containment status: STABLE\n"
    "Next review: 2026-01-30\n"
))
git("add", "-A")
git("commit", "-q", "-m", "archive: EXP-7 closed — data retained per ARCH-9")
orphan_hash = git("rev-parse", "HEAD", capture=True).stdout.strip()
git("checkout", "-q", "main")
git("branch", "-q", "-D", "experiment-7-archive")

ref_dir = os.path.join(CHALLENGE_DIR, ".git", "refs", "experiments", "archived")
os.makedirs(ref_dir, exist_ok=True)
open(os.path.join(ref_dir, "experiment-7"), "w").write(orphan_hash + "\n")

# Git flag 3 — note on a non-HEAD commit
log = git("log", "--oneline", capture=True).stdout.strip().splitlines()
target_commit = log[1].split()[0]  # second newest
git("notes", "--ref=refs/notes/deployment", "add", "-m",
    f"pipeline: nexus-portal-deploy\n"
    f"run-id: f2a8e1c4\n"
    f"status: SUCCESS\n"
    f"branch: main\n"
    f"environment: production\n"
    f"deploy-key: {GIT_FLAG3}\n"
    f"runner: nexus-runner-02\n"
    f"timestamp: 2024-10-14T03:17:52Z",
    target_commit)

# ── Mercurial track ───────────────────────────────────────────────────────────
print("[*] Building mercurial history...")

# Re-write site files to a clean known state before hg track starts.
# The git track may have left files in a partially patched state depending
# on the orphan branch dance. We define explicit content per hg revision.

# hg rev 0 state: same as git initial (uptime = 847 days, original css/js)
patch("index.html", "1,204 days, 09:14:52", "847 days, 14:22:07")
patch("static/css/style.css", "clamp(2.8rem, 7vw, 5.2rem)", "clamp(2.5rem, 7vw, 5rem)")

hg("addremove")
hg_commit("feat: initial portal scaffold")

# hg rev 1: uptime bump — FLAG_A in extras
patch("index.html", "847 days, 14:22:07", "1,204 days, 09:14:52")
hg_commit("content: weekly uptime counter sync",
          hg_extra=f"sys.calibration_ref={HG_FLAG_A}")

# hg rev 2: css tweak
patch("static/css/style.css", "clamp(2.5rem, 7vw, 5rem)", "clamp(2.8rem, 7vw, 5.2rem)")
hg_commit("style: bump hero heading on large viewports")

# hg rev 3: js fix — FLAG_B in extras
patch("static/js/app.js", "Incident logged.", "Incident logged. Ref: INC-2024-1103.")
hg_commit("fix: add incident ref to auth error message",
          hg_extra=f"sys.calibration_ref={HG_FLAG_B}")

# hg rev 4: docs
write("README.md", read("README.md") + "\n## Deploy\nPush to `default` triggers CI. Credentials via Vault.\n")
hg_commit("docs: add deploy notes")

# ── Summary ───────────────────────────────────────────────────────────────────
print(f"""
[+] Done. Challenge at: {CHALLENGE_DIR}
    Both .git and .hg present in the same directory.

GIT FLAGS
  Flag 1: {GIT_FLAG1}
    git log --all --oneline -- .ops-config
    git show <add-commit>:.ops-config

  Flag 2: {GIT_FLAG2}
    git for-each-ref  (find refs/experiments/archived/experiment-7)
    git show <hash>:EXPERIMENT_LOG.txt  ->  base64 -d

  Flag 3: {GIT_FLAG3}
    git for-each-ref refs/notes/
    git log --notes=refs/notes/deployment --format='%H %N' | grep deploy-key

MERCURIAL FLAG
  Flag 4: {HG_FLAG_A + HG_FLAG_B}
    hg log -T '{{rev}}: {{join(extras, " | ")}}\\n' | grep calibration_ref
    (concatenate rev 1 value + rev 3 value)

Serve: cd {CHALLENGE_DIR} && python3 -m http.server 8080
""")