# Nexus Labs CTF — Git Internals Challenge
## Solutions & Design Notes

---

## Stage 1 — Deleted Config File in Git History

**Concept:** A provisioning script committed `.ops-config` with real credentials
and an access token. The developer noticed, deleted the file, and added it to
`.gitignore`. The blob is permanently in the object store.

```bash
# Find commits that touched the file (shows both the add and the delete)
git log --all --oneline -- .ops-config

# Read the file at the commit that added it (second result — the first is the delete)
git show <add-commit>:.ops-config
# access_token = polycyber{exp0sed_g1t_1s_a_cl4ssic_m1stake}
```

---

## Stage 2 — Orphan Commit Under Non-Standard Ref

**Concept:** An experiment branch was committed, the branch deleted, but the
commit hash stored manually under `refs/experiments/archived/experiment-7`.
This namespace is completely custom — git's normal commands ignore it entirely.

```bash
# None of these show it:
git log --all --oneline    # orphan — no branch points to it
git branch -a              # not a heads/ ref
git tag                    # not a tag

# These do:
git for-each-ref           # lists every ref regardless of namespace
ls .git/refs/experiments/archived/
git fsck --unreachable 2>&1 | grep commit

# Read the commit
HASH=$(cat .git/refs/experiments/archived/experiment-7)
git show "$HASH":EXPERIMENT_LOG.txt

# Decode the checksum
echo "<base64_value>" | base64 -d
# polycyber{d3ad_c0mm1ts_t3ll_t4les_f0rgott3n}
```

---

## Stage 3 — Flag in a Git Note

**Concept:** `git notes` attaches freeform metadata to existing commits without
rewriting them. Notes are stored in `refs/notes/<namespace>` and are invisible
in `git log` unless explicitly requested. The flag is the `deploy-key` field in
a note that looks like a CI deployment record.

```bash
# Discovery — notes don't show up in normal git log output
git for-each-ref refs/notes/
# -> refs/notes/deployment

# Read all notes in the namespace
git log --notes=refs/notes/deployment --format='%H %N' | grep -v '^$'

# Or read the note on a specific commit
git notes --ref=refs/notes/deployment show <commit-hash>

# The deploy-key field contains the flag:
# deploy-key: polycyber{g1t_n0t3s_4r3_th3_h1dd3n_d1mens10n}
```

---

## Stage 4 — Flag Split Across Mercurial Changeset Extras

**Concept:** Mercurial changesets carry an `extras` dictionary — a set of
arbitrary key/value pairs baked into the changeset metadata. The flag is
split across two commits (revisions 1 and 3) under the key
`sys.calibration_ref`. Neither half looks like a flag on its own; the full
value is obtained by concatenating them in order.

```bash
# Discovery — list all revisions with their extras
hg log -T '{rev}: {join(extras, " | ")}\n'
# rev 1: branch=default | sys.calibration_ref=CTF{hg_extr
# rev 3: branch=default | sys.calibration_ref=as_r3v34l_4ll}

# Concatenate the two values to reconstruct the flag:
# polycyber{hg_extras_r3v34l_4ll}

# Alternatively, target the key directly:
hg log -T '{rev}: {extras("sys.calibration_ref")}\n' | grep -v '^[^:]*: $'
```

---
# Nexus Labs CTF — Défi Git Internals
## Solutions & Notes de conception

---

## Étape 1 — Fichier de configuration supprimé dans l'historique Git

**Concept :** Un script de provisionnement a commité `.ops-config` avec de vraies
informations d'identification et un jeton d'accès. Le développeur s'en est rendu
compte, a supprimé le fichier et l'a ajouté au `.gitignore`. Le blob est
définitivement stocké dans l'object store.

```bash
# Trouver les commits qui ont touché le fichier (montre l'ajout et la suppression)
git log --all --oneline -- .ops-config

# Lire le fichier au commit qui l'a ajouté (deuxième résultat — le premier est la suppression)
git show <add-commit>:.ops-config
# access_token = polycyber{exp0sed_g1t_1s_a_cl4ssic_m1stake}
```

## Étape 2 — Commit orphelin sous une référence non standard

**Concept :** Une branche d'expérimentation a été commitée, la branche supprimée,
mais le hash du commit stocké manuellement sous
`refs/experiments/archived/experiment-7`. Cet espace de noms est entièrement
personnalisé — les commandes normales de git l'ignorent complètement.

```bash
# Aucune de ces commandes ne le montre :
git log --all --oneline    # orphelin — aucune branche ne pointe vers lui
git branch -a              # pas une référence heads/
git tag                    # pas un tag

# Celles-ci le montrent :
git for-each-ref           # liste toutes les références quel que soit l'espace de noms
ls .git/refs/experiments/archived/
git fsck --unreachable 2>&1 | grep commit

# Lire le commit
HASH=$(cat .git/refs/experiments/archived/experiment-7)
git show "$HASH":EXPERIMENT_LOG.txt

# Décoder le checksum
echo "<base64_value>" | base64 -d
# polycyber{d3ad_c0mm1ts_t3ll_t4les_f0rgott3n}
```

---

## Étape 3 — Flag dans une note Git

**Concept :** `git notes` attache des métadonnées libres à des commits existants
sans les réécrire. Les notes sont stockées dans `refs/notes/<namespace>` et sont
invisibles dans `git log` sauf si explicitement demandé. Le flag est le champ
`deploy-key` dans une note qui ressemble à un enregistrement de déploiement CI.

```bash
# Découverte — les notes n'apparaissent pas dans la sortie normale de git log
git for-each-ref refs/notes/
# -> refs/notes/deployment

# Lire toutes les notes dans l'espace de noms
git log --notes=refs/notes/deployment --format='%H %N' | grep -v '^$'

# Ou lire la note sur un commit spécifique
git notes --ref=refs/notes/deployment show <commit-hash>

# Le champ deploy-key contient le flag :
# deploy-key: polycyber{g1t_n0t3s_4r3_th3_h1dd3n_d1mens10n}
```

---

## Étape 4 — Flag réparti sur les extras de changesets Mercurial

**Concept :** Les changesets Mercurial transportent un dictionnaire `extras` —
un ensemble de paires clé/valeur arbitraires intégrées dans les métadonnées du
changeset. Le flag est réparti sur deux commits (révisions 1 et 3) sous la clé
`sys.calibration_ref`. Aucune moitié ne ressemble à un flag prise isolément ;
la valeur complète s'obtient en les concaténant dans l'ordre.

```bash
# Découverte — lister toutes les révisions avec leurs extras
hg log -T '{rev}: {join(extras, " | ")}\n'
# rev 1: branch=default | sys.calibration_ref=CTF{hg_extr
# rev 3: branch=default | sys.calibration_ref=as_r3v34l_4ll}

# Concaténer les deux valeurs pour reconstruire le flag :
# polycyber{hg_extras_r3v34l_4ll}

# Ou cibler la clé directement :
hg log -T '{rev}: {extras("sys.calibration_ref")}\n' | grep -v '^[^:]*: $'
```
